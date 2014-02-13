using JSON
jsfile = ARGS[1]
PARS = JSON.parse(readall(jsfile))

PARS["ncores"] > 1 && addprocs(PARS["ncores"])
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

@everywhere include("histogram_defaults.jl")

@everywhere begin

function getr(ret::Associative, path::Associative, k::Symbol)
    const x = merge(path, {:obj=>k})
    if !(x in keys(ret))
        ret[x] = defaults_func[k]()
    end
    return ret[x]
end

function fill_histogram(
    row::DataFrameRow,
    isdata::Bool,
    hname::Symbol,
    hex::Function,
    p::Dict,
    ret::Dict
    )

    const syst = p[:systematic]
    const x = hex(row)
    const bin = findbin(defaults[hname]::Histogram, x)::Int64
    for (scen::Symbol, wfunc::Function) in weight_scenarios
        
        nominal_only && !(scen==:nominal || scen==:unweighted) && continue
        #in case of the systematically variated sample, we only want to use the nominal weight
        (!isdata && syst != :nominal && scen != :nominal) && continue
        (isdata && scen != :unweighted) && continue #only unweighted data
        #(!isdata && scen == :unweighted) && continue #dont care about unweighted MC
        
        const kk = merge(p, {:scenario=>scen})
        h = getr(ret, kk, hname)::Histogram

        const w = wfunc(row)::Union(NAtype, Float64)
        (isnan(w) || isna(w)) && error("$kk: w=$w $(df[row.row, :])") 
        h.bin_contents[bin] += w
        h.bin_entries[bin] += 1
    end
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
        for row in eachrow(sub(df, rows))
            nproc += 1
            #nproc%10000==0 && println("$nproc")
            const cur_row = rows[nproc]::Int64
            
            is_any_na(row, :sample, :systematic, :isolation) && continue
            const sample = hmap_symb_from[row[:sample]::Int64]
            const systematic = hmap_symb_from[row[:systematic]::Int64]
            const iso = hmap_symb_from[row[:isolation]::Int64]
            const true_lep = sample==:tchan ? row[:gen_lepton_id]::Int32 : int32(0)

            const isdata = ((sample == :data_mu) || (sample == :data_ele))
            if !isdata && nominal_only
                if !((systematic==:nominal)||(systematic==:unknown))
                    continue
                end
            end

            ###
            ### transfer matrices
            ###
            if sample==:tchan && iso==:iso

                const x = row[:cos_theta_lj_gen]
                const y = row[:cos_theta_lj]
               
                ###
                ### fill the gen-level histogram before selection
                ### 
                const p = {
                    :sample=>sample, :iso=>iso, :true_lep=>true_lep,
                    :systematic=>systematic, :scenario=>:unweighted
                }
                fill_histogram(
                    row, isdata,
                    :cos_theta_lj_gen, row->row[:cos_theta_lj_gen],
                    p, ret
                )
               
                #did event pass reconstruction ?
                local reco = true 

                if !is_any_na(row, :njets, :ntags, :bdt_sig_bg, :n_signal_mu, :n_signal_ele, :n_veto_mu, :n_veto_ele)

                    reco = reco && sel(row) && Cuts.bdt(row, bdt_cut)

                    if reco && Cuts.truelepton(row, :mu)
                        reco = reco & Cuts.qcd_mva_wp(row, :mu) & Cuts.is_reco_lepton(row, :mu)
                    elseif reco && Cuts.truelepton(row, :ele)
                        reco = reco & Cuts.qcd_mva_wp(row, :ele) & Cuts.is_reco_lepton(row, :ele)
                    else
                        reco = false
                    end
                else
                    reco = false
                end

                ret[:nreco] += int(reco)

                #get indices into transfer matrix
                const nx = (isna(x)||isnan(x)) ? 1 : searchsortedfirst(TM.edges[1], x)-1
    	        const ny = (isna(y)||isnan(y)||!reco) ? 1 : searchsortedfirst(TM.edges[2], y)-1
                
                #get transfer matrix linear index from 2D index
                const linind = sub2ind(TM_hsize, nx, ny)
                
                (linind>=1 && linind<=length(TM.baseh.bin_contents)) ||
                    error("incorrect index $linind for $nx,$ny $x,$y")

                for (scen_name, scen) in scens_gr[systematic]
                    
                    nominal_only && scen_name[1]!=:nominal && continue
                    const kk = {
                        :sample=>sample, :iso=>iso, :true_lep=>true_lep,
                        :systematic=>systematic, :scenario=>scen_name[1]
                    }

                    const h = getr(ret, kk, :transfer_matrix)::NHistogram
                   
                    const w = scen[:weight](row)

                    (isnan(w) || isna(w)) && error("$kk: w=$w $(df[row.row, :])")

                    h.baseh.bin_contents[linind] += w
                    h.baseh.bin_entries[linind] += 1.0
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
            if do_project_bdt::Bool
                for (nj, nt) in [(2, 0), (2,1), (3,2)]

                    #pre-bdt selection
                    const _reco = reco & sel(row, nj, nt)::Bool
                    _reco || continue
                    
                    const p = {
                        :sample => sample,
                        :iso => iso,
                        :lepton => lepton,
                        :systematic => systematic,
                        :njets => nj,
                        :ntags => nt
                    }

                    fill_histogram(
                        row, isdata,
                        :bdt_sig_bg, row->row[:bdt_sig_bg],
                        p, ret
                    )

                    fill_histogram(
                        row, isdata,
                        :abs_ljet_eta, row->abs(row[:ljet_eta]),
                        p, ret
                    )

                    fill_histogram(
                        row, isdata,
                        :C, row->row[:C],
                        p, ret
                    )

                    fill_histogram(
                        row, isdata,
                        :cos_theta_lj, row->row[:cos_theta_lj],
                        p, ret
                    )

                    fill_histogram(
                        row, isdata,
                        :cos_theta_bl, row->row[:cos_theta_bl],
                        p, ret
                    )
                    
                end
            end

            reco = reco && sel(row)::Bool

            ###
            ### post BDT, 2J1T
            ###
            if (reco && Cuts.bdt(row, bdt_cut))  
                const p = {
                    :sample => sample,
                    :iso => iso,
                    :lepton => lepton,
                    :systematic => systematic,
                    :njets => 2,
                    :ntags => 1
                }

                const bdt_p = merge(p, {:purification=>:bdt_sig_bg, :bdt_cut=>bdt_cut})

                fill_histogram(
                    row, isdata,
                    :cos_theta_lj, row->row[:cos_theta_lj],
                    bdt_p, ret
                )

                fill_histogram(
                    row, isdata,
                    :cos_theta_bl, row->row[:cos_theta_bl],
                    bdt_p, ret
                )
            end

            ###
            ### cut-based cross-check, 2J1T
            ###
            if (reco && Cuts.cutbased_etajprime(row))

                const p = {
                    :sample => sample,
                    :iso => iso,
                    :lepton => lepton,
                    :systematic => systematic,
                    :njets => 2,
                    :ntags => 1,
                    :purification => :etajprime
                }

                fill_histogram(
                    row, isdata,
                    :cos_theta_lj, row->row[:cos_theta_lj],
                    p, ret
                )
                

                fill_histogram(
                    row, isdata,
                    :cos_theta_bl, row->row[:cos_theta_bl],
                    p, ret
                )
                
            end
        end

        const t1 = time()
        println("processing $(length(rows)) took $(t1-t0) seconds")

        ret[:nproc] = nproc
        ret[:time] = (t1-t0)
        return ret
    end
end

const N = PARS["maxevents"] > 0 ? PARS["maxevents"] : nrow(df)
N > nrow(df) && error("too many rows specified: $N > $(nrow(df))")

const cn = 10^6

const rowsplits = chunks(cn, N)

println("mapping over Nevents=$N with chunksize=$cn, nchunks=$(length(rowsplits))...")
tic()
ret = reduce(+, pmap(process_df, rowsplits))
q=toc()
println("mapped, reduced $(N/q) events/second")
println("projected $(length(ret)) objects")

for k in keys(ret)
    if (typeof(ret[k]) <: Histogram)
        println("H $k ", @sprintf("%.2f", integral(ret[k])))
        ovfw = ret[k].bin_contents[1]
        if ovfw>0
            println("overflow in bin=1: $ovfw")
        end
        #println(ret[k])
    end
    (typeof(ret[k]) <: NHistogram) && println("H $k ", @sprintf("%.2f", integral(ret[k])), " N=$(nentries(ret[k]))")
end

ret[:nproc] == N || error("incomplete processing ", ret[:nproc], "!=", N)
println(ret[:time])

mkpath(dirname(outfile))
of = jldopen(outfile, "w")
write(of, "ret", ret)
close(of)
println("saved file $outfile")
