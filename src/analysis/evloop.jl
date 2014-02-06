require("base.jl")

jsfile = ARGS[1]

@eval @everywhere PARS = JSON.parse(readall($jsfile))
@everywhere println(PARS)

const infile = PARS["infile"]
const outfile = PARS["outfile"]
@eval @everywhere (println("loading dataframe...");df = readdf($infile))

@everywhere begin
    const bdt_cut = PARS["bdt_cut"]
    #ct_binning = PARS["binning"] #fix Inf JSON reading
    ct_binning = vcat(-Inf, linspace(-1, 1, 11), Inf)
   
    const nominal_only = false #run over nominal events only, is quicker
    const do_project_bdt = PARS["project_bdt"]
    defaults_func = {
        :cos_theta_lj => ()->Histogram(ct_binning),
        :bdt_sig_bg => ()->Histogram(vcat(-Inf, linspace(-1, 1, 30), Inf)),
        :transfer_matrix => ()->NHistogram({ct_binning, ct_binning})
    }
    
    defaults = Dict{Symbol, Any}()
    for (k, v) in defaults_func
        defaults[k] = v()
    end
end

@everywhere begin

    const TM = defaults[:transfer_matrix]
    const hsize = tuple([length(ed) for ed in TM.edges]...)


    sel(row, nj=2, nt=1) = (Cuts.njets(row, nj) & Cuts.ntags(row, nt) & Cuts.dr(row))::Bool
    
    function process_df(rows)
        const t0 = time()

        T_cos = eltype(df[:cos_theta_lj_gen])

        nproc = 0
        ret = Dict()
        ret[:nreco] = 0
        function getr(path::Associative, k::Symbol)
            const x = merge(path, {:obj=>k})
            if !(x in keys(ret))
                ret[x] = defaults_func[k]()
            end
            return ret[x]
        end
        
        sample_counters = Dict{Symbol, Int64}()
        sample_counters[:tchan] = 0
        sample_counters[:data_mu] = 0
        sample_counters[:data_ele] = 0
        sample_counters[:wjets] = 0
        sample_counters[:ttjets] = 0
        
        cut_counters = Dict{Symbol, Int64}()
        cut_counters[:tchan] = 0
        cut_counters[:data_mu] = 0
        cut_counters[:data_ele] = 0
        cut_counters[:wjets] = 0
        cut_counters[:ttjets] = 0
        
        #println("looping over $(nrow(df)) rows")
        for row in eachrow(sub(df, rows))
            nproc += 1
            #nproc%10000==0 && println("$nproc")
            const cur_row = rows[nproc]::Int64
            
            is_any_na(row, :sample, :systematic, :isolation) && continue
            const sample = hmap_symb_from[row[:sample]::Int64]
            const syst = hmap_symb_from[row[:systematic]::Int64]


            const iso = hmap_symb_from[row[:isolation]::Int64]
            const true_lep = sample==:tchan ? row[:gen_lepton_id]::Int32 : int32(0)
            const isdata = ((sample == :data_mu) || (sample == :data_ele)) 
            !isdata && nominal_only && (!(syst == :nominal)||(syst == :unknown)) && continue
            for s in [:data_mu, :data_ele, :tchan, :ttjets, :wjets]
                sample_counters[s] += (sample == s) ? 1 : 0
            end
            
            #transfer matrices
            if sample==:tchan && iso==:iso
                const x = row[:cos_theta_lj_gen]::T_cos
                const y = row[:cos_theta_lj]::Union(NAtype, T_cos)
               
                local reco = true 
                if !is_any_na(row, :njets, :ntags, :bdt_sig_bg)
                    reco = reco && sel(row) && Cuts.bdt(row, bdt_cut)
                    if reco && Cuts.truelepton(row, :mu)
                        reco = reco & Cuts.qcd_mva_wp(row, :mu) & Cuts.is_mu(row)
                    elseif reco && Cuts.truelepton(row, :ele)
                        reco = reco & Cuts.qcd_mva_wp(row, :ele) & Cuts.is_ele(row)
                    else
                        reco = false
                    end
                else
                    reco = false
                end
                ret[:nreco] += int(reco)

                const nx = (isna(x)||isnan(x)) ? 1 : searchsortedfirst(TM.edges[1], x)-1
    	        const ny = (isna(y)||isnan(y)||!reco) ? 1 : searchsortedfirst(TM.edges[2], y)-1
                const linind = sub2ind(hsize, nx, ny)
                
                (linind>=1 && linind<=length(TM.baseh.bin_contents)) || error("incorrect index $linind for $nx,$ny $x,$y")

                for (scen_name, scen) in scens_gr[syst]
                    
                    nominal_only && scen_name[1]!=:nominal && continue

                    h = getr({
                            :sample=>sample, :iso=>iso, :true_lep=>true_lep,
                            :systematic=>syst, :scenario=>scen_name[1]
                        },
                        :transfer_matrix
                    )::NHistogram
                   
                    const w = scen[:weight](row)
                   
                    h.baseh.bin_contents[linind] += isnan(w) ? 0.0 : w 
                    h.baseh.bin_entries[linind] += 1.0
                end
            end
            
            #pre-bdt
            is_any_na(row, :njets, :ntags, :bdt_sig_bg, :cos_theta_lj, :bdt_qcd) && continue
            (isna(row[:bdt_sig_bg]) || isnan(row[:bdt_sig_bg])) && error("bdt was NA/NaN")

            ####
            #project 2J1T, 3J2T BDT templates with full systematics
            ####
            reco = true
            if Cuts.is_reco_lepton(row, :mu)
                const lepton = :mu
                reco = reco & Cuts.qcd_mva_wp(row, lepton)
            elseif Cuts.is_reco_lepton(row, :ele)
                const lepton = :ele
                reco = reco & Cuts.qcd_mva_wp(row, lepton)
            else
                continue
            end
            
            if do_project_bdt
                for (nj, nt) in [(2, 0), (2,1), (3,2)]
                    #pre-bdt selection
                    _reco = reco & sel(row, nj, nt)::Bool
                    _reco || continue
                    
                    const p = {:sample=>sample, :iso=>iso, :lepton=>lepton, :systematic=>syst, :njet=>nj, :ntag=>nt} 
                    const x = row[:bdt_sig_bg]::Float64
                    const bin = findbin(defaults[:bdt_sig_bg]::Histogram, x)::Int64
                    for (scen::Symbol, wfunc::Function) in weight_scenarios
                        
                        nominal_only && !(scen==:nominal || scen==:unweighted) && continue

                        #in case of the systematically variated sample, we only want to use the nominal weight
                        (!isdata && syst != :nominal && scen != :nominal) && continue
                        (isdata && scen != :unweighted) && continue
                        
                        const kk = merge(p, {:scenario=>scen})
                        h = getr(kk, :bdt_sig_bg)::Histogram
                        const w = wfunc(row)::Union(NAtype, Float64)
                        
                        h.bin_contents[bin] += isnan(w) ? 0.0 : w 
                        h.bin_entries[bin] += 1
                    end
                    
                end
            end

            #post bdt, 2J1T, cos_theta lj
            reco = reco & sel(row)::Bool
            reco = reco & Cuts.bdt(row, bdt_cut)
            reco || continue

            for s in [:data_mu, :data_ele, :tchan, :ttjets, :wjets]
                cut_counters[s] += (sample == s) ? 1 : 0
            end
            
            begin
                const p = {:sample=>sample, :iso=>iso, :lepton=>lepton, :systematic=>syst, :bdt_cut=>bdt_cut} 
                const x = row[:cos_theta_lj]::T_cos
                const bin = findbin(defaults[:cos_theta_lj]::Histogram, x)::Int64
                for (scen::Symbol, wfunc::Function) in weight_scenarios

                    #in case of the systematically variated sample, we only want to use the nominal weight
                    (!isdata && syst != :nominal && scen != :nominal) && continue
                    (isdata && scen != :unweighted) && continue
                    
                    const kk = merge(p, {:scenario=>scen})
                    h = getr(kk, :cos_theta_lj)::Histogram
                    const w = wfunc(row)::Union(NAtype, Float64)

                    h.bin_contents[bin] += isnan(w) ? 0.0 : w 
                    h.bin_entries[bin] += 1
                end
            end
        end

        const t1 = time()
        println("processing $(length(rows)) took $(t1-t0) seconds, Npre=$sample_counters Npost=$cut_counters, Nreco=$(ret[:nreco])")

        ret[:nproc] = nproc
        ret[:sample_counters] = sample_counters
        ret[:cut_counters] = sample_counters
        ret[:time] = (t1-t0)
        return ret
    end
end

N = nrow(df)
cn = 10^6
#N = 10^4
#cn = 10^3
rowsplits = chunks(cn, N)

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
            println("overflow in bin=1: $(ret[k].bin_contents[1])")
        end
    end
    (typeof(ret[k]) <: NHistogram) && println("H $k ", @sprintf("%.2f", integral(ret[k])))
end

ret[:nproc] == N || error("incomplete processing ", ret[:nproc], "!=", N)
println(ret[:sample_counters])
println(ret[:time])

of = jldopen(outfile, "w")
write(of, "ret", ret)
close(of)
println("saved file $outfile")
