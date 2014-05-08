using JSON

const infile = ARGS[1]
const outfile = ARGS[2]
const PARS = JSON.parse(readall(ARGS[3]))

#how to cut on QCD?
const QCD_CUT_TYPE = symbol(PARS["qcd_cut"])
const DO_LJET_RMS = PARS["do_ljet_rms"]

#FIXME: currently this is different for TCHPT and CSVT
const B_WEIGHT_NOMINAL = symbol(PARS["b_weight_nominal"])

const BDT_VAR = symbol(PARS["bdt_var"])
#const BDT_CUTS = vcat(-1.0, [-0.2:0.01:0.8])
const BDT_CUTS = [0.0, 0.06, 0.13, 0.2, 0.4, 0.6, 0.8, 0.9]

#PAS
#const BDT_CUTS = [0.06, 0.13]

const sp = dirname(Base.source_path())
require("$sp/base.jl")

using ROOT, ROOTDataFrames
using ROOT.ROOTHistograms

println("loading dataframe:$infile");

#Load the main event TTree
const df_base = TreeDataFrame(infile)
df_base.tt == C_NULL && (warn("empty TTree for $infile, exiting");exit(0))
nrow(df_base)>0 || (warn("$infile was emtpy, exiting");exit(0))

#load the TTree with the QCD values, xs weights
const df_added = TreeDataFrame("$infile.added")

#create a combined view of both ttrees
df = MultiColumnDataFrame(TreeDataFrame[df_base, df_added])

require("$sp/histogram_defaults.jl")

const BDT_SYMBOLS = {bdt=>symbol(@sprintf("%.5f", bdt)) for bdt in BDT_CUTS}
const LEPTON_SYMBOLS = {13=>:mu, 11=>:ele, -13=>:mu, -11=>:ele, 15=>:tau, -15=>:tau}

const DO_TRANSFER_MATRIX = true
const HISTS_NOMINAL_ONLY = false
const TM_NOMINAL_ONLY = false
const JET_TAGS = [(2, 0), (2, 1), (3, 0), (3, 1), (3, 2)]

const crosscheck_vars = [
    :bdt_sig_bg, :bdt_sig_bg_top_13_001,

    (:abs_ljet_eta, row::DataFrameRow -> abs(row[:ljet_eta])),
    (:abs_ljet_eta_16, row::DataFrameRow -> abs(row[:ljet_eta])),
    (:abs_bjet_eta, row::DataFrameRow -> abs(row[:bjet_eta])),
    :C, :shat, :ht,
    (:C_signalregion, row->row[:C]),
    (:top_mass_signalregion, row->row[:top_mass]),

    :lepton_pt, :lepton_iso, :lepton_eta,
    (:abs_lepton_eta, r->abs(r[:lepton_eta])),
    :met_phi, :met, :mtw,
    :bjet_pt, :ljet_pt,
    :ljet_eta, :bjet_eta,
    :bjet_mass, :ljet_mass,
    :ljet_dr, :bjet_dr,

    :top_mass, :top_pt,

    :n_good_vertices,
    :cos_theta_lj, :cos_theta_bl,
    :cos_theta_lj_gen, :cos_theta_bl_gen,
    :nu_soltype,
    :njets,
    :ntags,
    :lepton_charge
]

const SOLTYPE = symbol(PARS["soltype"])

#default transfer matrix shortcut
const TM = defaults[:transfer_matrix]

#vector of transfer matrix dimensions
const TM_hsize = tuple([length(ed) for ed in TM.edges]...)

include("$BASE/src/skim/jet_cls.jl")

#returns the object corresponding to key x from the dictionary ret
#if ret[x] does not exist, it is created according to defaults_func[k](),
#where k is a key specifying the description of the object to create
function getr{K <: Any, V <: Any}(ret::Dict{K, V}, x::HistKey, k::Symbol)
    if !haskey(ret, x)
        ret[x] = defaults_func[k]()::V
    end
    return ret[x]::Union(Histogram, NHistogram)
end

function print_ev(row)
    println("hlt=", row[:hlt], " Nj=", row[:njets], " Nt=", row[:ntags], " nsigmu=", row[:n_signal_mu], " nsigele=", row[:n_signal_ele],
        " nvetomu=", row[:n_veto_mu], " nvetoele=", row[:n_veto_ele], " bdt_qcd=", row[:bdt_qcd], " bdt_sig_bg=", row[:bdt_sig_bg],
        " ljet_dr=", row[:ljet_dr], " bjet_dr=", row[:bjet_dr],
    )
end

function fill_histogram(
    nw::Float64, #nominal weight value
    row::DataFrameRow, #present data row
    isdata::Bool, #data or MC?
    hname::Symbol, #name of the histogram
    hex::Function, #function row->Real used to fill the histogram
    ret::Dict, #the reference to the dict of all the histograms

    sample::Symbol,
    iso::Symbol,
    systematic::Symbol,
    selection_major::Symbol,
    selection_minor::Symbol,
    lepton::Symbol,
    njets::Int64,
    ntags::Int64,

    )

    #value to be filled to histogram
    const x = hex(row)

    #get the index of the bin to be filled.
    #this is the same regardless of the systematic scenario or weight
    const bin = findbin(defaults[hname]::Histogram, x)::Int64

    #loop over all the systematic scenarios
    for (scname, scenario::Scenario) in scenarios

        #get the type of weighting to be applied
        const w_scenario = scenario.weight_scenario

        #scenario not defined for this sample
        sample != scenario.sample && continue

        #scenario not defined for this systematic processing
        systematic != scenario.systematic && continue

        if HISTS_NOMINAL_ONLY && !(
                w_scenario==:nominal || w_scenario==:unweighted
            )
            continue
        end

        if haskey(SingleTopBase.SYSTEMATICS_TABLE, w_scenario)
            const wname = SingleTopBase.SYSTEMATICS_TABLE[w_scenario]
        else
            const wname = w_scenario
        end

        const kk = HistKey(
            hname,
            sample,
            iso,
            systematic,
            wname,
            selection_major,
            selection_minor,
            lepton,
            njets,
            ntags,
        )

        #get the histogram for this sample, systematic scenario
        h = getr(ret, kk, hname)::Histogram

        const w = scenario.weight(nw, row)::Union(NAtype, Float64)
        (isnan(w) || isna(w)) && error("$kk: w=$w $(df[row.row, :])")

        #fill the histogram
        h.bin_contents[bin] += w
        h.bin_entries[bin] += 1

        #fill W+jets jet flavours separately as well
        if sample == :wjets
            for cls in jet_classifications
                const ev_cls = row[:jet_cls] |> jet_cls_from_number
                ev_cls == cls || continue

                ev_cls = jet_cls_heavy_light(ev_cls)

                const kk = HistKey(
                    hname,
                    symbol("wjets__$(ev_cls)"),
                    iso,
                    systematic,
                    w_scenario,
                    selection_major,
                    selection_minor,
                    lepton,
                    njets,
                    ntags,
                )

                h = getr(ret, kk, hname)::Histogram

                const w = scenario.weight(nw, row)::Union(NAtype, Float64)

                (isnan(w) || isna(w)) && error("$kk: w=$w $(df[row.row, :])")
                #fill the histogram
                h.bin_contents[bin] += w
                h.bin_entries[bin] += 1
            end
        end
    end
end

#selection function
sel(row::DataFrameRow, nj=2, nt=1) = (Cuts.njets(row, nj) & Cuts.ntags(row, nt) & Cuts.dr(row))::Bool

function process_df(rows::AbstractVector{Int64})
    const t0 = time()
    tprev = time()

    println("mapping across $(length(rows)) rows")

    nproc = 0

    nfsel = 0

    const ret = Dict{HistKey, Any}()

    for cur_row::Int64 in rows
        #println("row=$cur_row")
        #get entries corresponding to current row in TTrees
        for sdf in df.dfs
            #CMSSW.getentry!(sdf.tree, cur_row)
            load_row(sdf, cur_row)
        end

        const row = DataFrameRow(df, cur_row)
        nproc += 1
        if nproc % 10000==0
            dt = time() - tprev
            println("$nproc $dt $nfsel")
            tprev = time()
        end
        is_any_na(row, :sample, :systematic, :isolation)::Bool &&
            warn("sample, systematic or isolation were NA")

        const sample = hmap_symb_from[row[:sample]::Int64]
        const systematic = hmap_symb_from[row[:systematic]::Int64]
        const iso = hmap_symb_from[row[:isolation]::Int64]
        const true_lep = sample==:tchan ? int64(row[:gen_lepton_id]::Int32) : int64(0)

        const isdata = ((sample == :data_mu) || (sample == :data_ele))
        if !isdata && HISTS_NOMINAL_ONLY
            if !((systematic==:nominal)||(systematic==:unknown))
                continue
            end
        end

        ###
        ### transfer matrices
        ###
        const transfer_matrix_reco = {
            :mu=>{k=>false for k in BDT_CUTS},
            :ele=>{k=>false for k in BDT_CUTS}
        }

        if DO_TRANSFER_MATRIX && sample==:tchan && iso==:iso

            const x = row[:cos_theta_lj_gen]::Float32
            const y = row[:cos_theta_lj]::Union(Float32, NAtype)
            const ny_ = searchsortedfirst(TM.edges[2], y)

            #can get gen-level index here
            const nx = (isna(x)||isnan(x)) ? 1 : searchsortedfirst(TM.edges[1], x)-1

            const nw = nominal_weight(row)::Float64

            for reco_lep in Symbol[:ele, :mu]

                #did event pass reconstruction ?
                #need to reinitialize for each new cut-tree "branch"
                local reco = true
                reco = reco && !is_any_na(row, :njets, :ntags, :bdt_sig_bg, :n_signal_mu, :n_signal_ele, :n_veto_mu, :n_veto_ele)::Bool
                reco = reco && sel(row)
                reco = reco && Cuts.is_reco_lepton(row, reco_lep)
                reco = reco && Cuts.qcd_cut(row, QCD_CUT_TYPE, reco_lep)
                reco = reco && Cuts.nu_soltype(row, SOLTYPE)

                if DO_LJET_RMS
                    reco = reco && Cuts.ljet_rms(row)
                end

                const lep_symb = symbol("gen_$(LEPTON_SYMBOLS[true_lep])__reco_$(reco_lep)")

                for (scen_name::(Symbol, Symbol), scen::Scenario) in scens_gr[systematic]
                    (TM_NOMINAL_ONLY && scen_name[1]!=:nominal) && continue

                    const w = scen.weight(nw, row)::Float64
                    (isnan(w) || isna(w)) && error("$k2: w=$w $(df[row.row, :])")

                    #assumes BDT cut points are sorted ascending
                    for bdt_cut::Float64 in BDT_CUTS::Vector{Float64}
                        const _reco = reco &&
                            Cuts.bdt(row, bdt_cut, BDT_VAR)

                        #if scen_name[1] == :nominal
                        #    transfer_matrix_reco[reco_lep][bdt_cut] = reco
                        #end

                        #need to get the reco-axis index here, it will depend on passing the BDT cut
                        #unreconstructed events are put to underflow bin
                        const ny = (isna(y)||isnan(y)||!_reco) ? 1 : ny_ - 1

                        #get transfer matrix linear index from 2D index
                        const linind = sub2ind(TM_hsize, nx, ny)

                        (linind>=1 && linind<=length(TM.baseh.bin_contents)) ||
                            error("incorrect index $linind for $nx,$ny $x,$y")


                        const k2 = HistKey(
                            :transfer_matrix,
                            sample,
                            iso,
                            systematic,
                            scen_name[1],
                            :bdt,
                            BDT_SYMBOLS[bdt_cut],
                            lep_symb,
                            2, 1
                        )

                        const h = getr(ret, k2, :transfer_matrix)::NHistogram

                        h.baseh.bin_contents[linind] += w
                        h.baseh.bin_entries[linind] += 1.0
                    end

                    #assumes BDT cut points are sorted ascending
                    for (cut_major, cut_minor, cutfn) in {
                            (:cutbased, :etajprime_topmass_default, Cuts.cutbased_etajprime)
                        }
                        const _reco = reco && cutfn(row)
                        const ny = (isna(y)||isnan(y)||!_reco) ? 1 : ny_ - 1
                        const linind = sub2ind(TM_hsize, nx, ny)

                        (linind>=1 && linind<=length(TM.baseh.bin_contents)) ||
                            error("incorrect index $linind for $nx,$ny $x,$y")

                        const k2 = HistKey(
                            :transfer_matrix,
                            sample,
                            iso,
                            systematic,
                            scen_name[1],
                            cut_major,
                            cut_minor,
                            lep_symb,
                            2, 1
                        )

                        const h = getr(ret, k2, :transfer_matrix)::NHistogram

                        h.baseh.bin_contents[linind] += w
                        h.baseh.bin_entries[linind] += 1.0
                    end
                end
            end
        end

        ###
        ### lepton reco
        ###
        if is_any_na(row, :n_signal_mu, :n_signal_ele, :n_veto_mu, :n_veto_ele)
            continue
        end

        if Cuts.is_reco_lepton(row, :mu)
            const lepton = :mu
        elseif Cuts.is_reco_lepton(row, :ele)
            const lepton = :ele
        else
            continue
        end

        ###
        ### pre-bdt
        ###
        is_any_na(row, :njets, :ntags, :cos_theta_lj, :bdt_sig_bg) && continue

        #cache nominal weight
        const nw = nominal_weight(row)::Float64

        #pre-qcd plots
        for (nj, nt) in JET_TAGS
            #pre-bdt selection
            const _reco = sel(row, nj, nt)::Bool
            _reco || continue

            for var in [:bdt_qcd, :mtw, :met, :met_phi]
                fill_histogram(
                    nw,
                    row, isdata,
                    var,
                    row->row[var],
                    ret,

                    sample,
                    iso,
                    systematic,
                    :preqcd,
                    :nothing,
                    lepton,
                    nj, nt
                )
            end
        end

        if DO_LJET_RMS
            Cuts.ljet_rms(row) || continue
        end

        ###
        ### QCD rejection
        ###
        const reco = Cuts.qcd_cut(row, QCD_CUT_TYPE, lepton)
        reco || continue

        ###
        ### project BDT templates and input variables with full systematics
        ###
        for (nj, nt) in JET_TAGS
            #pre-bdt selection
            const _reco = reco && sel(row, nj, nt)::Bool && Cuts.nu_soltype(row, SOLTYPE)
            _reco || continue

            for var in crosscheck_vars

                #if a 2-tuple is specified, 2. arg is the function to apply
                #otherwise, identity
                if isa(var, Tuple)
                    var, f = var
                else
                    var, f = var, (row::DataFrameRow -> row[var])
                end

                fill_histogram(
                    nw,
                    row, isdata,
                    var,
                    row -> f(row),
                    ret,
                    sample,
                    iso,
                    systematic,
                    :preselection,
                    :nothing,
                    lepton,
                    nj, nt
                )
            end
        end

        ###
        ### cut-based cross-check, 2J1T
        ###
        for (nj, nt) in JET_TAGS
            if (reco &&
                Cuts.cutbased_etajprime(row) &&
                sel(row, nj, nt)::Bool &&
                Cuts.nu_soltype(row, SOLTYPE)
            )
                for var in crosscheck_vars

                    #if a 2-tuple is specified, 2. arg is the function to apply
                    #otherwise, identity
                    if isa(var, Tuple)
                        var, f = var
                    else
                        var, f = var, (row::DataFrameRow -> row[var])
                    end

                    fill_histogram(
                        nw,
                        row, isdata,
                        var,
                        f,
                        ret,
                        sample,
                        iso,
                        systematic,
                        :cutbased,
                        :etajprime_topmass_default,
                        lepton,
                        nj, nt
                    )
                end
            end
        end

        #final selection by BDT
        for (nj, nt) in JET_TAGS
            for bdt_cut in BDT_CUTS

                if (reco &&
                    Cuts.bdt(row, bdt_cut, BDT_VAR) &&
                    sel(row, nj, nt)::Bool &&
                    Cuts.nu_soltype(row, SOLTYPE)
                )
                    for var in crosscheck_vars
                        #if a 2-tuple is specified, 2. arg is the function to apply
                        #otherwise, identity
                        if isa(var, Tuple)
                            var, f = var
                        else
                            var, f = var, (row::DataFrameRow -> row[var])
                        end

                        nfsel += 1

                        fill_histogram(
                            nw,
                            row, isdata,
                            var,
                            f,
                            ret,
                            sample,
                            iso,
                            systematic,
                            :bdt,
                            BDT_SYMBOLS[bdt_cut],
                            lepton,
                            nj, nt
                        )
                    end
                else
                    continue
                end
            end
        end
    end #event loop

    const t1 = time()
    println(
        "processing ", first(rows), ":", last(rows),
        " (N=$(length(rows))) took $(t1-t0) seconds, nfsel=$nfsel"
    )

    return ret

end #function

tic()
ret = process_df(1:nrow(df))
q = toc()

###
### OUTPUT
###
tempf = mktemp()[1]
rfile = string(splitext(outfile)[1], ".root")
println("saving to $rfile, temp file $tempf")
mkpath(dirname(rfile))
tf = TFile(convert(ASCIIString, tempf), "RECREATE")
Cd(tf, "")
for (k, v) in ret
    typeof(k) <: HistKey || continue
    println(
        k, " sument=$(sum(entries(v))) ",
        @sprintf(" int=%.2f", integral(v)),
        @sprintf(" sumerr=%.2f", sum(errors(v)))
    )
    #isa(v, Histogram) && println(v)

    hi = to_root(v, tostr(k))
end

println("projected $(length(ret)) objects in $q seconds")
print("writing...");Write(tf);println("done")
Close(tf)

for i=1:5
    try
        println("cleaning $outfile...");isfile(outfile) && rm(outfile)
        mkpath(dirname(outfile))
        println("copying...");cp(tempf, outfile)
        s = stat(outfile)
        #run(`sync`)
        s.size == 0 && error("file corrupted")
        break
    catch err
        println("$err: retrying")
        sleep(5)
    end
end

println("cleaning $tempf...");rm(tempf)
