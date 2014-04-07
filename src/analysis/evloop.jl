using JSON

const infile = ARGS[1]
const outfile = ARGS[2]
const PARS = JSON.parse(readall(ARGS[3]))

#how to cut on QCD?
const qcd_cut_type = symbol(PARS["qcd_cut"])

#FIXME: currently this is different for TCHPT and CSVT
const B_WEIGHT_NOMINAL = symbol(PARS["b_weight_nominal"])

const sp = dirname(Base.source_path())
require("$sp/base.jl")

using CMSSW

require("$sp/hroot.jl")

println("loading dataframe...");

#Load the main event TTree
const df_base = TreeDataFrame(infile)
df_base.doget = false

#load the TTree with the QCD values, xs weights
const df_added = TreeDataFrame("$infile.added")
df_added.doget = false

#create a combined view of both ttrees
df = MultiColumnDataFrame(TreeDataFrame[df_base, df_added])

require("$sp/histogram_defaults.jl")

const BDT_SYMBOLS = {bdt=>symbol(@sprintf("%.5f", bdt)) for bdt in bdt_cuts}
const LEPTON_SYMBOLS = {13=>:mu, 11=>:ele, -13=>:mu, -11=>:ele, 15=>:tau, -15=>:tau}

const do_transfer_matrix = true

include("$BASE/src/skim/jet_cls.jl")

function getr{K <: Any, V <: Any}(ret::Dict{K, V}, x::HistKey, k::Symbol)
    const hk = x
    if !haskey(ret, hk)
        ret[hk] = defaults_func[k]()::V
    end
    return ret[hk]::Union(Histogram, NHistogram)
end

function print_ev(row)
    println("hlt=", row[:hlt], " Nj=", row[:njets], " Nt=", row[:ntags], " nsigmu=", row[:n_signal_mu], " nsigele=", row[:n_signal_ele],
        " nvetomu=", row[:n_veto_mu], " nvetoele=", row[:n_veto_ele], " bdt_qcd=", row[:bdt_qcd], " bdt_sig_bg=", row[:bdt_sig_bg],
        " ljet_dr=", row[:ljet_dr], " bjet_dr=", row[:bjet_dr], 
    )
end

function fill_histogram(
    nw::Float64,
    row::DataFrameRow,
    isdata::Bool,
    hname::Symbol,
    hex::Function,
    ret::Dict,

    sample::Symbol,
    iso::Symbol,
    systematic::Symbol,
    selection_major::Symbol,
    selection_minor::Symbol,
    lepton::Symbol,
    njets::Int64,
    ntags::Int64,

    )

    const x = hex(row)::Real

    const bin = findbin(defaults[hname]::Histogram, x)::Int64

    for (scname, scenario::Scenario) in scenarios
       
        const w_scenario = scenario.weight_scenario
        
        sample != scenario.sample && continue 
        systematic != scenario.systematic && continue 
        hists_nominal_only && !(w_scenario==:nominal || w_scenario==:unweighted) && continue
        
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

        h = getr(ret, kk, hname)::Histogram

        const w = scenario.weight(nw, row)::Union(NAtype, Float64)
        (isnan(w) || isna(w)) && error("$kk: w=$w $(df[row.row, :])")

        h.bin_contents[bin] += w
        h.bin_entries[bin] += 1

        #fill W+jets jet flavours separately
        if sample == :wjets
            for cls in jet_classifications
                ev_cls = row[:jet_cls] |> jet_cls_from_number
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
                h.bin_contents[bin] += w
                h.bin_entries[bin] += 1
            end
        end
    end
end

#default transfer matrix shortcut
const TM = defaults[:transfer_matrix]

#vector of transfer matrix dimensions
const TM_hsize = tuple([length(ed) for ed in TM.edges]...)

#selection function
sel(row::DataFrameRow, nj=2, nt=1) = (Cuts.njets(row, nj) & Cuts.ntags(row, nt) & Cuts.dr(row))::Bool

function process_df(rows::AbstractVector{Int64})
    const t0 = time()
    tprev = time()

    println("mapping across $(length(rows)) rows")
    
    nproc = 0
    
    const ret = Dict{HistKey, Any}()
     
    for cur_row::Int64 in rows
        #println("row=$cur_row")
        #get entries corresponding to current row in TTrees
        for sdf in df.dfs
            CMSSW.getentry!(sdf.tree, cur_row)
        end

        const row = DataFrameRow(df, cur_row)
        nproc += 1
        if nproc % 10000==0
            dt = time() - tprev
            println("$nproc $dt")
            tprev = time()
        end
        is_any_na(row, :sample, :systematic, :isolation)::Bool && warn("sample, systematic or isolation were NA")

        const sample = hmap_symb_from[row[:sample]::Int64]
        const systematic = hmap_symb_from[row[:systematic]::Int64]
        const iso = hmap_symb_from[row[:isolation]::Int64]
        const true_lep = sample==:tchan ? int64(row[:gen_lepton_id]::Int32) : int64(0)

        const isdata = ((sample == :data_mu) || (sample == :data_ele))
        if !isdata && hists_nominal_only
            if !((systematic==:nominal)||(systematic==:unknown))
                continue
            end
        end

        ###
        ### transfer matrices
        ###

        const transfer_matrix_reco = {
            :mu=>{k=>false for k in bdt_cuts},
            :ele=>{k=>false for k in bdt_cuts}
        }

        if do_transfer_matrix && sample==:tchan && iso==:iso

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
                reco = reco && Cuts.qcd_cut(row, qcd_cut_type, reco_lep)

                const lep_symb = symbol("gen_$(LEPTON_SYMBOLS[true_lep])__reco_$(reco_lep)")

                for (scen_name::(Symbol, Symbol), scen::Scenario) in scens_gr[systematic]
                    (tm_nominal_only && scen_name[1]!=:nominal) && continue
                        
                    const w = scen.weight(nw, row)::Float64
                    (isnan(w) || isna(w)) && error("$k2: w=$w $(df[row.row, :])")
                    
                    #assumes BDT cut points are sorted ascending
                    for bdt_cut::Float64 in bdt_cuts::Vector{Float64}
                        const _reco = reco && Cuts.bdt(row, bdt_cut)
                        
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
                            (:cutbased, :etajprime, Cuts.cutbased_etajprime)
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
        for (nj, nt) in [(2, 0), (2, 1), (3, 2)]
            #pre-bdt selection
            const _reco = sel(row, nj, nt)::Bool
            _reco || continue
            
            for var in [:bdt_qcd, :mtw, :met]
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

        ###
        ### QCD rejection
        ###        
        const reco = Cuts.qcd_cut(row, qcd_cut_type, lepton)
        reco || continue
        
        ###
        ### project BDT templates with full systematics
        ###
        for (nj, nt) in [(2, 0), (2,1), (3,2)]

            #pre-bdt selection
            const _reco = reco & sel(row, nj, nt)::Bool
            _reco || continue

            for var in [
                :bdt_sig_bg,
                :bdt_sig_bg_top_13_001,
                (:abs_ljet_eta, row::DataFrameRow -> abs(row[:ljet_eta])),
                :C, :met, :mtw, :shat, :ht, :lepton_pt,
                :bjet_pt,
                (:abs_bjet_eta, row::DataFrameRow -> abs(row[:bjet_eta])),
                :ljet_eta, :bjet_eta,
                :bjet_mass, :top_mass,
                :top_pt, :n_good_vertices,
                :cos_theta_lj, :cos_theta_bl
                ]

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
        
        #2j1t
        reco = reco && sel(row)::Bool
        
        ###
        ### cut-based cross-check, 2J1T
        ###
        for (nj, nt) in [(2, 0), (2, 1), (3, 2)]
            if (reco && Cuts.cutbased_etajprime(row))
                for var in [
                        (:abs_ljet_eta, row::DataFrameRow -> abs(row[:ljet_eta])),
                        :C, :met, :mtw, :shat, :ht, :lepton_pt,
                        :bjet_pt,
                        (:abs_bjet_eta, row::DataFrameRow -> abs(row[:bjet_eta])),
                        :ljet_eta, :bjet_eta,
                        :bjet_mass, :top_mass,
                        :top_pt, :n_good_vertices,
                        :cos_theta_lj, :cos_theta_bl
                    ]
                    
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

        for (nj, nt) in [(2, 0), (2, 1), (3, 2)]
            #final selection by BDT
            for bdt_cut in bdt_cuts
                
                if (reco && Cuts.bdt(row, bdt_cut))
                    for var in [
                            (:abs_ljet_eta, row::DataFrameRow -> abs(row[:ljet_eta])),
                            :C, :met, :mtw, :shat, :ht, :lepton_pt,
                            :bjet_pt,
                            (:abs_bjet_eta, row::DataFrameRow -> abs(row[:bjet_eta])),
                            :ljet_eta, :bjet_eta,
                            :bjet_mass, :top_mass,
                            :top_pt, :n_good_vertices,
                            :cos_theta_lj, :cos_theta_bl
                        ]
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
    println("processing ", rows.start, ":", rows.start+rows.len-1, " (N=$(length(rows))) took $(t1-t0) seconds")

    return ret

end #function

tic()

ret = process_df(1:nrow(df))

q=toc()

tempf = mktemp()[1]
rfile = string(splitext(outfile)[1], ".root") 
println("saving to $rfile, temp file $tempf")
mkpath(dirname(rfile))
tf = TFile(tempf, "RECREATE")
for (k, v) in ret
    typeof(k) <: HistKey || continue
    print(k, " $(sum(entries(v))) ", @sprintf("%.2f", integral(v)))
    isa(v, NHistogram) && print(" ", sum(sum(entries(v), 1)[2:end]), " ", sum(sum(entries(v), 2)[2:end]))
    println()
    toroot(tf, tostr(k), v)
end

println("projected $(length(ret)) objects in $q seconds")
print("writing...");write(tf.p);println("done")
close(tf)

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
#print(readall(`du $outfile`))
