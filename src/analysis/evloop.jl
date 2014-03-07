using JSON

jsfile = ARGS[1]
PARS = JSON.parse(readall(jsfile))

require("base.jl")
using CMSSW

PARS = JSON.parse(readall(jsfile))
println(PARS)

require("hroot.jl")

const infile = PARS["infile"]
const outfile = PARS["outfile"]
println("loading dataframe...");

const df_base = TreeDataFrame(infile)
df_base.doget = false

#load the TTree with the QCD values, xs weights
const df_added = TreeDataFrame("$infile.added")
df_added.doget = false
println(names(df_added))

#create a combined access doorway for both ttrees
df = MultiColumnDataFrame(TreeDataFrame[df_base, df_added])

require("histogram_defaults.jl")

const bdt_strings = {bdt=>@sprintf("%.5f", bdt) for bdt in bdt_cuts}
const bdt_symbs = {bdt=>symbol(@sprintf("%.5f", bdt)) for bdt in bdt_cuts}
const lepton_symbs = {13=>:mu, 11=>:ele, -13=>:mu, -11=>:ele, 15=>:tau, -15=>:tau}

const do_transfer_matrix = false

print_bdt(bdt_cut) = bdt_strings[bdt_cut]

include("$BASE/src/skim/jet_cls.jl")

function getr{K <: Any, V <: Any}(ret::Dict{K, V}, x::HistKey, k::Symbol)
    const hk = x
    if !haskey(ret, hk)
        ret[hk] = defaults_func[k]()::V
    end
    return ret[hk]::Union(Histogram, NHistogram)
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

    const x = hex(row)::Union(Float64, Float32)

    const bin = findbin(defaults[hname]::Histogram, x)::Int64

    for (scenario::Symbol, wfunc::Function) in weight_scenarios
        
        hists_nominal_only && !(scenario==:nominal || scenario==:unweighted) && continue
        #in case of the systematically variated sample, we only want to use the nominal weight
        (!isdata && systematic != :nominal && scenario != :nominal) && continue
        (isdata && scenario != :unweighted) && continue #only unweighted data
        #(!isdata && scen == :unweighted) && continue #dont care about unweighted MC
        

        const kk = HistKey(
            hname,
            sample,
            iso,
            systematic,
            scenario,
            selection_major,
            selection_minor,
            lepton,
            njets,
            ntags,
        )

        h = getr(ret, kk, hname)::Histogram

        const w = wfunc(nw, row)::Union(NAtype, Float64)
        (isnan(w) || isna(w)) && error("$kk: w=$w $(df[row.row, :])") 
        h.bin_contents[bin] += w
        h.bin_entries[bin] += 1

        #fill W+jets jet flavours separately
        if sample == :wjets
            for cls in jet_classifications
                const kk = HistKey(
                    hname,
                    symbol("wjets__$(cls)"),
                    iso,
                    systematic,
                    scenario,
                    selection_major,
                    selection_minor,
                    lepton,
                    njets,
                    ntags,
                )

                h = getr(ret, kk, hname)::Histogram

                const w = wfunc(nw, row)::Union(NAtype, Float64)
                (isnan(w) || isna(w)) && error("$kk: w=$w $(df[row.row, :])") 
                h.bin_contents[bin] += w
                h.bin_entries[bin] += 1
            end
        end
    end
end

function pass_selection(reco::Bool, bdt_cut::Float64, row::DataFrameRow)
    if reco && !is_any_na(row, :njets, :ntags, :bdt_sig_bg, :n_signal_mu, :n_signal_ele, :n_veto_mu, :n_veto_ele)::Bool

        reco = reco && sel(row)::Bool && Cuts.bdt(row, bdt_cut)::Bool

        if reco && Cuts.truelepton(row, :mu)::Bool
            reco = reco && Cuts.qcd_mva_wp(row, :mu)::Bool && Cuts.is_reco_lepton(row, :mu)::Bool
        elseif reco && Cuts.truelepton(row, :ele)::Bool
            reco = reco && Cuts.qcd_mva_wp(row, :ele)::Bool && Cuts.is_reco_lepton(row, :ele)::Bool
        else
            reco = false
        end
    else
        reco = false
    end
    return reco
end


#default transfer matrix shortcut
const TM = defaults[:transfer_matrix]

#vector of transfer matrix dimensions
const TM_hsize = tuple([length(ed) for ed in TM.edges]...)

#selection function
sel(row::DataFrameRow, nj=2, nt=1) = (Cuts.njets(row, nj) & Cuts.ntags(row, nt) & Cuts.dr(row))::Bool

function process_df(rows::AbstractVector{Int64})
    const t0 = time()
    
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
        nproc%1000==0 && println("$nproc")
        
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
        if do_transfer_matrix && sample==:tchan && iso==:iso

            const x = row[:cos_theta_lj_gen]::Float32
            const y = row[:cos_theta_lj]::Union(Float32, NAtype)
           
            #did event pass reconstruction ?
            local reco = true 
            
            #can get gen-level index here
            const nx = (isna(x)||isnan(x)) ? 1 : searchsortedfirst(TM.edges[1], x)-1

            const nw = nominal_weight(row)::Float64

            for bdt_cut::Float64 in bdt_cuts::Vector{Float64}
                reco = pass_selection(reco, bdt_cut, row)::Bool
	           
                #need to get the reco-axis index here, it will depend on passing the BDT cut
                const ny = (isna(y)||isnan(y)||!reco) ? 1 : searchsortedfirst(TM.edges[2], y)-1
                
                #get transfer matrix linear index from 2D index
                const linind = sub2ind(TM_hsize, nx, ny)
                
                (linind>=1 && linind<=length(TM.baseh.bin_contents)) ||
                    error("incorrect index $linind for $nx,$ny $x,$y")

                for (scen_name::(Symbol, Symbol), scen::Scenario) in scens_gr[systematic]
                    tm_nominal_only && scen_name[1]!=:nominal && continue
                    
                    const k2 = HistKey(
                        :transfer_matrix,
                        sample,
                        iso,
                        systematic,
                        scen_name[1],
                        :bdt,
                        bdt_symbs[bdt_cut],
                        lepton_symbs[true_lep],
                        2, 1
                    )

                    const h = getr(ret, k2, :transfer_matrix)::NHistogram
                   
                    const w = scen.weight(nw, row)::Float64
                    (isnan(w) || isna(w)) && error("$k2: w=$w $(df[row.row, :])")

                    h.baseh.bin_contents[linind] += w
                    h.baseh.bin_entries[linind] += 1.0
                end
            end
        end

        ###
        ### lepton reco
        ###
        if is_any_na(row, :n_signal_mu, :n_signal_ele)
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

        ###
        ### QCD rejection
        ###        
        if sel(row, 2, 1)
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
                    2, 1 
                )
            end
        end

        const reco = Cuts.qcd_mva_wp(row, lepton)
        reco || continue
        
        ###
        ### project BDT templates with full systematics
        ###
        for (nj, nt) in [(2, 0), (2,1), (3,2)]

            #pre-bdt selection
            const _reco = reco & sel(row, nj, nt)::Bool
            _reco || continue

            for var in [
                :bdt_sig_bg, :bdt_sig_bg_top_13_001,
                (:abs_ljet_eta, row::DataFrameRow -> abs(row[:ljet_eta])),
                :C, :met, :mtw, :shat, :ht, :lepton_pt,
                :bjet_pt,
                (:abs_bjet_eta, row::DataFrameRow -> abs(row[:bjet_eta])),
                :bjet_mass, :top_mass,
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
        if (reco && Cuts.cutbased_etajprime(row))
            for var in [:cos_theta_lj]
                fill_histogram(
                    nw,
                    row, isdata,
                    var,
                    row->row[var],
                    ret,

                    sample,
                    iso,
                    systematic,
                    :cutbased,
                    :etajprime_topmass_default,
                    lepton,
                    2, 1
                )
            end
        end

        #final selection by BDT
        for bdt_cut in bdt_cuts
            if (reco && Cuts.bdt(row, bdt_cut))
                for var in [:cos_theta_lj]
                    fill_histogram(
                        nw,
                        row, isdata,
                        var,
                        row->row[var],
                        ret,

                        sample,
                        iso,
                        systematic,
                        :bdt,
                        bdt_symbs[bdt_cut],
                        lepton,
                        2, 1
                    )
                end
            else
                continue
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
println("saving to $rfile")
mkpath(dirname(rfile))
tf = TFile(tempf, "RECREATE")
for (k, v) in ret
    typeof(k) <: HistKey || continue
    println(k)
	toroot(tf, tostr(k), v)
end
println("projected $(length(ret)) objects in $q seconds")
write(tf.p)
close(tf)
cp(tempf, outfile)
rm(tempf)
