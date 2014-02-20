using JSON
#@everywhere using ProfileView

jsfile = ARGS[1]
PARS = JSON.parse(readall(jsfile))

#PARS["ncores"] > 1 && addprocs(PARS["ncores"])
#needs to be after addprocs
require("base.jl")

@eval @everywhere PARS = JSON.parse(readall($jsfile))
@everywhere println(PARS)

const infile = PARS["infile"]
const outfile = PARS["outfile"]
@eval @everywhere (
    println("loading dataframe...");
    df = readdf($infile)
)

require("histogram_defaults.jl")

@everywhere begin

const bdt_strings = {bdt=>@sprintf("%.5f", bdt) for bdt in bdt_cuts}
const bdt_symbs = {bdt=>symbol(@sprintf("%.5f", bdt)) for bdt in bdt_cuts}
const lepton_symbs = {13=>:mu, 11=>:ele, -13=>:mu, -11=>:ele, 15=>:tau, -15=>:tau}
const do_transfer_matrix = true

print_bdt(bdt_cut) = bdt_strings[bdt_cut]

function getr(ret::Associative, x::HistKey, k::Symbol)
    if !(x in keys(ret))
        ret[x] = defaults_func[k]()::Union(Histogram, NHistogram)
    end
    return ret[x]::Union(Histogram, NHistogram)
end

function fill_histogram(
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

        const w = wfunc(row)::Union(NAtype, Float64)
        (isnan(w) || isna(w)) && error("$kk: w=$w $(df[row.row, :])") 
        h.bin_contents[bin] += w
        h.bin_entries[bin] += 1
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

end

@everywhere begin

    #default transfer matrix shortcut
    const TM = defaults[:transfer_matrix]

    #vector of transfer matrix dimensions
    const TM_hsize = tuple([length(ed) for ed in TM.edges]...)

    #selection function
    sel(row::DataFrameRow, nj=2, nt=1) = (Cuts.njets(row, nj) & Cuts.ntags(row, nt) & Cuts.dr(row))::Bool
    
    function process_df(rows)
        const t0 = time()

        nproc = 0
        ret = Dict()

        ret[:nreco] = 0

        ret[:fails_lepton] = 0
        ret[:ele] = 0
        ret[:mu] = 0

        ret[:fails_bdt] = 0
        
        
        #println("looping over $(nrow(df)) rows")
        for row::DataFrameRow in eachrow(sub(df, rows))

            nproc += 1
            nproc%10000==0 && println("$nproc")
            const cur_row = rows[nproc]::Int64
            
            is_any_na(row, :sample, :systematic, :isolation)::Bool && continue

            const sample = hmap_symb_from[row[:sample]::Int64]
            const systematic = hmap_symb_from[row[:systematic]::Int64]
            const iso = hmap_symb_from[row[:isolation]::Int64]
            const true_lep = sample==:tchan ? int64(row[:gen_lepton_id]::Int32) : int64(0)

            const isdata = ((sample == :data_mu) || (sample == :data_ele))
            if hists_nominal_only && !isdata 
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
                
                #get indices into transfer matrix
                const nx = (isna(x)||isnan(x)) ? 1 : searchsortedfirst(TM.edges[1], x)-1
              
                #loop over systematic weight scenarios for a given systematic processing
                for (scen_name::(Symbol, Symbol), scen) in scens_gr[systematic]
                    
                    #do we want to process only nominal transfer matrix?
                    tm_nominal_only && scen_name[1]!=:nominal && continue
                    
                    #the weight does not change depending on the BDT cut
                    const w = scen[:weight](row)::Float64
                    
                    #weight should be nontrivial
                    (isnan(w) || isna(w)) && error("$k2: w=$w $(df[row.row, :])")
                    
                    for bdt_cut::Float64 in bdt_cuts::Vector{Float64}
                        reco = pass_selection(reco, bdt_cut, row)::Bool
    	                
                        #the y index will change depending on reco
                        const ny = (isna(y)||isnan(y)||!reco) ? 1 : searchsortedfirst(TM.edges[2], y)-1
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
                            :bdt_2j_1t,
                            bdt_symbs[bdt_cut],
                            lepton_symbs[true_lep],
                            2, 1
                        )

                        const h = getr(ret, k2, :transfer_matrix)::NHistogram
                        h.baseh.bin_contents[linind] += w
                        h.baseh.bin_entries[linind] += 1.0
                    end
                end
            end

            ###
            ### lepton reco
            ###
            if is_any_na(row, :n_signal_mu, :n_signal_ele)
                ret[:fails_lepton] += 1
                continue
            end

            if Cuts.is_reco_lepton(row, :mu)
                const lepton = :mu
                ret[:mu] += 1
            elseif Cuts.is_reco_lepton(row, :ele)
                const lepton = :ele
                ret[:ele] += 1
            else
                ret[:fails_lepton] += 1
                continue
            end

            ###
            ### pre-bdt
            ###
            if is_any_na(row, :njets, :ntags, :bdt_sig_bg, :cos_theta_lj, :bdt_qcd)
                ret[:fails_bdt] += 1
                continue
            end
            (isna(row[:bdt_sig_bg]) || isnan(row[:bdt_sig_bg])) && error("bdt was NA/NaN")

            ###
            ### QCD rejection
            ###
            const reco = Cuts.qcd_mva_wp(row, lepton)
            
            ###
            ### project BDT templates with full systematics
            ###
            for (nj, nt) in [(2, 0), (2,1), (3,2)]

                #pre-bdt selection
                const _reco = reco & sel(row, nj, nt)::Bool
                _reco || continue

                fill_histogram(
                    row, isdata,
                    :bdt_sig_bg,
                    row->row[:bdt_sig_bg]::Float64,
                    ret,

                    sample,
                    iso,
                    systematic,
                    :preselection,
                    :nothing,
                    lepton,
                    nj, nt
                )

#                fill_histogram(
#                    row, isdata,
#                    :abs_ljet_eta, row->abs(row[:ljet_eta]),
#                    p, ret
#                )
#
#                fill_histogram(
#                    row, isdata,
#                    :C, row->row[:C],
#                    p, ret
#                )

                # fill_histogram(
                #     row, isdata,
                #     :cos_theta_lj, row->row[:cos_theta_lj],
                #     p, ret
                # )

#                fill_histogram(
#                    row, isdata,
#                    :cos_theta_bl, row->row[:cos_theta_bl],
#                    p, ret
#                )
                
            end
            

            reco = reco && sel(row)::Bool
            
            ###
            ### cut-based cross-check, 2J1T
            ###
            if (reco && Cuts.cutbased_etajprime(row))

                # const p = {
                #     :sample => sample,
                #     :iso => iso,
                #     :lepton => lepton,
                #     :systematic => systematic,
                #     :njets => 2,
                #     :ntags => 1,
                #     :purification => :etajprime
                # }

                # fill_histogram(
                #     row, isdata,
                #     :cos_theta_lj, row->row[:cos_theta_lj],
                #     p, ret
                # )
                

#                fill_histogram(
#                    row, isdata,
#                    :cos_theta_bl, row->row[:cos_theta_bl],
#                    p, ret
#                )
                
            end

            ###
            ### post BDT, 2J1T
            ###
            # const p = {
            #     :sample => sample,
            #     :iso => iso,
            #     :lepton => lepton,
            #     :systematic => systematic,
            #     :njets => 2,
            #     :ntags => 1
            #}

            for bdt_cut in bdt_cuts
                if (reco && Cuts.bdt(row, bdt_cut))  

                    # const bdt_p = merge(p, {:purification=>:bdt_sig_bg, :bdt_cut=>print_bdt(bdt_cut)})

                    # fill_histogram(
                    #     row, isdata,
                    #     :cos_theta_lj, row->row[:cos_theta_lj],
                    #     bdt_p, ret
                    # )

                    fill_histogram(
                        row, isdata,
                        :cos_theta_lj,
                        row->row[:cos_theta_lj]::Float32,
                        ret,

                        sample,
                        iso,
                        systematic,
                        :bdt,
                        bdt_symbs[bdt_cut],
                        lepton,
                        2, 1
                    )

#                    fill_histogram(
#                        row, isdata,
#                        :cos_theta_bl, row->row[:cos_theta_bl],
#                        bdt_p, ret
#                    )
                else
                    continue
                end
            end

        end

        const t1 = time()
        println("processing ", rows.start, ":", rows.start+rows.len-1, " (N=$(length(rows))) took $(t1-t0) seconds")

        ret[:time] = (t1-t0)
        return ret
    end
end

#const N = PARS["maxevents"] > 0 ? PARS["maxevents"] : nrow(df)
#N > nrow(df) && error("too many rows specified: $N > $(nrow(df))")
#const cn = 10^4

#const rowsplits = chunks(cn, N)
println("mapping over events ", PARS["start"], ":", PARS["stop"])
tic()

#Profile.init(10^10, 0.001)

#@profile ret = process_df(PARS["start"]:PARS["stop"])
ret = process_df(PARS["start"]:PARS["stop"])

#svg = open("profile.svg", "w")
#ProfileView.viewsvg(svg)
#close(svg)

q=toc()
#println("mapped, reduced $(N/q) events/second")
println("projected $(length(ret)) objects")

#for k in keys(ret)
#    if (typeof(ret[k]) <: Histogram)
#        println("H $k ", @sprintf("%.2f", integral(ret[k])))
#        ovfw = ret[k].bin_contents[1]
#        if ovfw>0
#            println("overflow in bin=1: $ovfw")
#        end
#        #println(ret[k])
#    end
#    (typeof(ret[k]) <: NHistogram) && println("H $k ", @sprintf("%.2f", integral(ret[k])), " N=$(nentries(ret[k]))")
#end

#ret[:nproc] == N || error("incomplete processing ", ret[:nproc], "!=", N)
println(ret[:time])

println("saving file $outfile")
tic()
mkpath(dirname(outfile))
of = jldopen(outfile, "w")
write(of, "ret", ret)
close(of)
println("saved file $outfile")
toc()
