#!/home/joosep/.julia/ROOT/julia
println("running skim.jl")
tstart = time()
println("hostname $(gethostname()) ", "SLURM_JOB_ID" in keys(ENV) ? ENV["SLURM_JOB_ID"] : getpid())

using ROOT
using DataFrames
using HDF5
using JLD
using HEP

include("xs.jl")

const NOSKIM = ("STPOL_NOSKIM" in keys(ENV) && ENV["STPOL_NOSKIM"]=="1")
if NOSKIM
    println("*** skimming DEACTIVATED")
end
const DEBUG=("DEBUG" in keys(ENV) && int(ENV["DEBUG"])==1)
if DEBUG
    println("*** DEBUG mode activated")
end

output_file = ARGS[1]

flist = Any[]
append!(flist, ARGS[2:length(ARGS)])
nflist = Any[]
rflist = Any[]
for fi in flist
    ev = Events([fi])
    println("EVL ", fi, " ", length(ev))
    if length(ev) > 0
        push!(nflist, fi)
    else
        push!(rflist, fi)
        println("removing empty file $fi from list")
    end
end
flistd = {f=>i for (f, i) in zip(nflist, 1:length(nflist))}

#try to load the Events 
events = Events(convert(Vector{ASCIIString}, nflist))

#save information on spectator jets
const do_specjets = true

maxev = length(events) 
println("running over $maxev events")

#events
df = similar(
        DataFrame(
            hlt=Bool[],
            hlt_mu=Bool[], hlt_ele=Bool[],
            
            lepton_pt=Float32[], lepton_eta=Float32[],
            lepton_iso=Float32[], lepton_phi=Float32[],
            lepton_type=Float32[],
            lepton_id=Int32[], lepton_charge=Int32[],

#jets associated with t-channel
            bjet_pt=Float32[], bjet_eta=Float32[], bjet_mass=Float32[], bjet_id=Float32[],
            #bjet_bd_a=Float32[],
            bjet_bd_b=Float32[],
            bjet_phi=Float32[],
            bjet_dr=Float32[],
            bjet_pumva=Float32[],

            ljet_pt=Float32[], ljet_eta=Float32[], ljet_mass=Float32[], ljet_id=Float32[],
            #ljet_bd_a=Float32[],
            ljet_bd_b=Float32[],
            ljet_rms=Float32[],
            ljet_phi=Float32[],
            ljet_dr=Float32[],
            ljet_pumva=Float32[],
#
##spectator jets
            sjet1_pt=Float32[], sjet1_eta=Float32[], sjet1_id=Float32[], sjet1_bd=Float32[], 
            sjet2_pt=Float32[], sjet2_eta=Float32[], sjet2_id=Float32[], sjet2_bd=Float32[], 

#event-level characteristics
            cos_theta_lj=Float32[], 
            cos_theta_bl=Float32[], 
            cos_theta_lj_gen=Float32[], 
            cos_theta_bl_gen=Float32[], 
            met=Float32[], njets=Int32[], ntags=Int32[], mtw=Float32[],
            met_phi=Float32[],

            C=Float32[], D=Float32[], circularity=Float32[], sphericity=Float32[], isotropy=Float32[], aplanarity=Float32[], thrust=Float32[],  
            top_mass=Float32[], top_eta=Float32[], top_phi=Float32[], top_pt=Float32[],
            #wjets_cls=Int32[],
            jet_cls=Int32[],
            ht=Float32[], shat=Float32[],
            
            nu_soltype=Int32[],
            n_signal_mu=Int32[], n_signal_ele=Int32[],
            n_veto_mu=Int32[], n_veto_ele=Int32[],
            n_good_vertices=Int32[],
#weights
            pu_weight=Float32[],
            pu_weight__up=Float32[],
            pu_weight__down=Float32[],
            
            lepton_weight__id=Float32[],
            lepton_weight__id__up=Float32[],
            lepton_weight__id__down=Float32[],
            lepton_weight__iso=Float32[],
            lepton_weight__iso__up=Float32[],
            lepton_weight__iso__down=Float32[],
            lepton_weight__trigger=Float32[],
            lepton_weight__trigger__up=Float32[],
            lepton_weight__trigger__down=Float32[],
            
            gen_weight=Float32[],
            gen_lepton_id=Int32[],

            top_weight=Float32[],
            top_weight__up=Float32[],
            top_weight__down=Float32[],

            b_weight=Float32[],
            b_weight__bc__up=Float32[],
            b_weight__bc__down=Float32[],
            b_weight__l__up=Float32[],
            b_weight__l__down=Float32[],

#file-level metadata
            run=Int64[], lumi=Int64[], event=Int64[],
            fileindex=Int64[],
            passes=Bool[],

            xs=Float32[],
            sample=Int64[],
            subsample=Int64[],
            isolation=Int64[],
            systematic=Int64[],
            fname=Int64[],
            processing_tag=Int64[],

        ),
        maxev
)

include("stpol.jl")

#Loop over the lumi sections, get the total processed event count
prfiles = similar(
    DataFrame(
        files=ASCIIString[],
        total_processed=Int64[],
        cls=Any[]
    ),
    length(flist)
)

i = 1
for fi in vcat(nflist, rflist)
    x = ROOT.get_counter_sum([fi], "singleTopPathStep1MuPreCount")
    prfiles[i, :files] = fi
    prfiles[i, :total_processed] = x
    prfiles[i, :cls] = sample_type(fi)
    i += 1
end

#Loop over the events
println("Beginning event loop")
nproc = 0

fails = {
    :lepton => 0,
    :met => 0,
    :jet => 0,
}

tic()
timeelapsed = @elapsed for i=1:maxev
    nproc += 1
    if nproc%(ceil(maxev/20)) == 0
        println("$nproc ($(ceil(nproc/maxev*100.0))%) events processed")
        toc()
        tic()
    end
    
    to!(events, i)
    #println("EV $(time_ns()) $i ", where_file(events))
    
    if DEBUG
        run, lumi, event = where(events)
        println("EV $i ev=", int(run), ":", int(lumi), ":", int(event))
    end

    for cn in names(df)
        df[i, cn] = NA
    end

    df[i, :passes] = false
    
    df[i, :gen_lepton_id] = events[sources[(:lepton, :gen, :id)]]
    
    #string representations of the feynman diagrams 
    #genstring_mu = events[sources[(:muon, :geninfo)]]
    #genstring_ele = events[sources[(:electron, :geninfo)]]

    df[i, :hlt] = passes_hlt(events, hlts) 
    df[i, :hlt_mu] = passes_hlt(events, HLTS[:mu]) 
    df[i, :hlt_ele] = passes_hlt(events, HLTS[:ele]) 
    
    #println(gen_id, " '", genstring_mu, "' '", genstring_ele, "'")

    
    df[i, :cos_theta_lj_gen] = events[sources[:cos_theta_lj_gen]] |> ifpresent
    df[i, :cos_theta_bl_gen] = events[sources[:cos_theta_bl_gen]] |> ifpresent

    df[i, :run], df[i, :lumi], df[i, :event] = where(events)
    fn = string("file:", get_current_file_name(events))
    
    findex = flistd[fn]
    df[i, :fileindex] = findex
        
    if fn != prfiles[findex, :files]
        error("incorrect file: $fn $(prfiles[findex, :files])")
    end
    

    df[i, :b_weight] = events[sources[weight(:btag)]]
    df[i, :b_weight__bc__up] = events[sources[weight(:btag, :bc, :up)]]
    df[i, :b_weight__bc__down] = events[sources[weight(:btag, :bc, :down)]]
    df[i, :b_weight__l__up] = events[sources[weight(:btag, :l, :up)]]
    df[i, :b_weight__l__down] = events[sources[weight(:btag, :l, :down)]]
    
    df[i, :top_weight] = events[sources[weight(:top)]]
    df[i, :top_weight__up] = df[i, :top_weight]^2
    df[i, :top_weight__down] = 1.0

    df[i, :gen_weight] = events[sources[weight(:gen)]]
    
    cls = prfiles[findex, :cls]
    sample = cls[:sample]
   
    df[i, :subsample] = int(hash(sample))
    df[i, :sample] = int(hash(string(get_process(sample))))
    df[i, :fname] = int(hash(fn))
    df[i, :xs] = haskey(cross_sections, sample) ? float32(cross_sections[sample]) : NA
    df[i, :isolation] = int(hash(string(cls[:iso])))
    df[i, :systematic] = int(hash(string(cls[:systematic])))
    df[i, :processing_tag] = int(hash(string(cls[:tag])))

    if DEBUG
        println("EV $i $genstring_mu $genstring_ele")
    end
   
    nmu = events[sources[:nsignalmu]]
    nele = events[sources[:nsignalele]]
    
    if DEBUG
        println("EV $i nmu=", events[sources[:nsignalmu]])
        println("EV $i nele=", events[sources[:nsignalele]])
    end
    
    df[i, :n_signal_mu] = nmu 
    df[i, :n_signal_ele] = nele

    if isna(nmu) || isna(nele)
        fails[:lepton] += 1
        continue
    end
    
    lepton_type = nothing
    if nmu==1 && nele==0
        lepton_type = :muon
        df[i, :lepton_type] = 13
    elseif nele==1 && nmu==0
        lepton_type = :electron
        df[i, :lepton_type] = 11
    else
        fails[:lepton] += 1
        continue
    end
    
    nveto_mu = events[sources[vetolepton(:mu)]]
    nveto_ele = events[sources[vetolepton(:ele)]]
    if DEBUG
        println("EV $i nvetomu=", events[sources[vetolepton(:mu)]])
        println("EV $i nvetoele=", events[sources[vetolepton(:ele)]])
    end
    df[i, :n_veto_mu] = nveto_mu
    df[i, :n_veto_ele] = nveto_ele

    if nveto_mu != 0 || nveto_ele != 0
        fails[:lepton] += 1
        continue
    end
    
    if DEBUG
        println("EV $i lepton_type = ", lepton_type)
    end
    if lepton_type == :muon || lepton_type == :electron
        df[i, :lepton_id] = events[sources[part(lepton_type, :genPdgId)]] |> ifpresent
        df[i, :lepton_eta] = events[sources[part(lepton_type, :Eta)]] |> ifpresent
        df[i, :lepton_pt] = events[sources[part(lepton_type, :Pt)]] |> ifpresent
        df[i, :lepton_iso] = events[sources[part(lepton_type, :relIso)]] |> ifpresent
        df[i, :lepton_charge] = events[sources[part(lepton_type, :Charge)]] |> ifpresent
        df[i, :lepton_phi] = events[sources[part(lepton_type, :Phi)]] |> ifpresent
        df[i, :mtw] = events[sources[part(lepton_type, :mtw)]] |> ifpresent
    end 
    df[i, :met] = events[sources[:met]] |> ifpresent
    df[i, :met_phi] = events[sources[(:met, :phi)]] |> ifpresent
    
  
    ##event had no MET
    #if (isna(df[i, :met]) || isna(df[i, :mtw]) || df[i, :met] < 00)
    #    fails[:met] += 1
    #    continue
    #end

#    #check for muon/electron and mtw/met
#    if  (lepton_type == :muon && df[i, :mtw] < 10.0) ||
#        (lepton_type == :electron && df[i, :met] < 10.0)
#        fails[:met] += 1
#        continue
#    end
    
    #get jet, tag
    df[i, :njets] = events[sources[:njets]]
    df[i, :ntags] = events[sources[:ntags]]
    
    #check for 2 jets
    if !(df[i, :njets] >= 2 && df[i, :ntags] >= 0)
        fails[:jet] += 1
        continue
    end

    df[i, :bjet_pt] = events[sources[:bjet_Pt]] |> ifpresent
    df[i, :bjet_eta] = events[sources[:bjet_Eta]] |> ifpresent
    df[i, :bjet_mass] = events[sources[:bjet_Mass]] |> ifpresent
    df[i, :bjet_id] = events[sources[:bjet_partonFlavour]] |> ifpresent
    #df[i, :bjet_bd_a] = events[sources[:bjet_bDiscriminatorTCHP]] |> ifpresent
    df[i, :bjet_bd_b] = events[sources[:bjet_bDiscriminatorCSV]] |> ifpresent
    df[i, :bjet_phi] = events[sources[:bjet_Phi]] |> ifpresent
    df[i, :bjet_dr] = events[sources[:bjet_deltaR]] |> ifpresent
    df[i, :bjet_pumva] = events[sources[:bjet_puMva]] |> ifpresent

    df[i, :ljet_pt] = events[sources[:ljet_Pt]] |> ifpresent
    df[i, :ljet_eta] = events[sources[:ljet_Eta]] |> ifpresent
    df[i, :ljet_mass] = events[sources[:ljet_Mass]] |> ifpresent
    df[i, :ljet_id] = events[sources[:ljet_partonFlavour]] |> ifpresent
    #df[i, :ljet_bd_a] = events[sources[:ljet_bDiscriminatorTCHP]] |> ifpresent
    df[i, :ljet_bd_b] = events[sources[:ljet_bDiscriminatorCSV]] |> ifpresent
    df[i, :ljet_rms] = events[sources[:ljet_rms]] |> ifpresent
    df[i, :ljet_phi] = events[sources[:ljet_Phi]] |> ifpresent
    df[i, :ljet_dr] = events[sources[:ljet_deltaR]] |> ifpresent
    df[i, :ljet_pumva] = events[sources[:ljet_puMva]] |> ifpresent
    
    df[i, :jet_cls] = jet_cls_to_number(jet_classification(df[i, :ljet_id], df[i, :bjet_id])) 
    df[i, :cos_theta_lj] = events[sources[:cos_theta_lj]] |> ifpresent
    df[i, :cos_theta_bl] = events[sources[:cos_theta_bl]] |> ifpresent
    
    df[i, :n_good_vertices] = events[sources[:n_good_vertices]] |> ifpresent
    
    df[i, :pu_weight] = events[sources[weight(:pu)]]
    df[i, :pu_weight__up] = events[sources[weight(:pu, :up)]]
    df[i, :pu_weight__down] = events[sources[weight(:pu, :down)]]
    
    df[i, :lepton_weight__id] = events[sources[weight(lepton_type, :id)]]
    df[i, :lepton_weight__id__up] = events[sources[weight(lepton_type, :id, :up)]]
    df[i, :lepton_weight__id__down] = events[sources[weight(lepton_type, :id, :down)]]
    df[i, :lepton_weight__trigger] = events[sources[weight(lepton_type, :trigger)]]
    df[i, :lepton_weight__trigger__up] = events[sources[weight(lepton_type, :trigger, :up)]]
    df[i, :lepton_weight__trigger__down] = events[sources[weight(lepton_type, :trigger, :down)]]
    
    if lepton_type == :muon
        df[i, :lepton_weight__iso] = events[sources[weight(lepton_type, :iso)]]
        df[i, :lepton_weight__iso__up] = events[sources[weight(lepton_type, :iso, :up)]]
        df[i, :lepton_weight__iso__down] = events[sources[weight(lepton_type, :iso, :down)]]
    else
        df[i, :lepton_weight__iso] = 1.0
        df[i, :lepton_weight__iso__up] = 1.0
        df[i, :lepton_weight__iso__down] = 1.0
    end
   
    if do_specjets
        
        #get all jets
        jet_pts = events[sources[part(:jets, :Pt)]]
        if !ispresent(jet_pts) || length(jet_pts)==0
            continue
        end
        jet_etas = events[sources[part(:jets, :Eta)]]
        jet_ids  = events[sources[part(:jets, :partonFlavour)]]
        jet_bds  = events[sources[part(:jets, :bDiscriminatorCSV)]]
        
        if all(map(ispresent, Any[jet_pts, jet_etas, jet_ids, jet_bds]))
            #get the indices of the b-tagged jet and the light jet by comparing with pt
            indb = find(x -> abs(x-df[i, :bjet_pt])<eps(x), jet_pts)[1]
            indl = find(x -> abs(x-df[i, :ljet_pt])<eps(x), jet_pts)[1]

            #get the indices of the other jets
            specinds = Int64[]
            for k=1:length(jet_pts)
                if k!=indb && k!=indl
                    push!(specinds, k)
                end
            end

            #get all the other jets
            #order by pt-descending
            j = 1
            for (pt, eta, id, bd, ind) in sort(
                [z for z in zip(jet_pts, jet_etas, jet_ids, jet_bds, [1:length(jet_pts)])],
                rev=true
            )
                #is a 'spectator jet'
                if (ind in specinds)
                    df[i, symbol("sjet$(j)_pt")] = pt
                    df[i, symbol("sjet$(j)_eta")] = eta
                    df[i, symbol("sjet$(j)_id")] = id
                    df[i, symbol("sjet$(j)_bd")] = bd
                    
                    #up to two
                    if j==2
                        break
                    else
                        j += 1
                    end
                end
            end
        end
    end

    for v in [:C, :D, :circularity, :isotropy, :sphericity, :aplanarity, :thrust]
        df[i, v] = events[sources[v]]
    end

    #df[i, :wjets_cls] = events[sources[:wjets_cls]] |> ifpresent
    for k in [:Pt, :Eta, :Phi, :Mass]
        p = part(:top, k)
        df[i, lowercase(string(p))] = events[sources[p]] |> ifpresent
    end

    if lepton_type == :muon || lepton_type == :electron
        df[i, :nu_soltype] = events[sources[part(lepton_type, :nu_soltype)]] |> ifpresent
    end

    #calculate the invariant mass of the system
    totvec = FourVectorSph(0.0, 0.0, 0.0, 0.0)
    for particle in [:top, :ljet]
        vec = Float64[]
        #this should be in the order of FourVectorSph
        for k in [:pt, :eta, :phi, :mass]
            x = df[i, part(particle, k)]
            if isna(x)
                break
            end
            v = convert(Float64, x)
            push!(vec, v)
        end
        if length(vec)==4
            v = FourVectorSph(vec...)
            totvec += v
        end
    end

    df[i, :shat] = l(totvec)
    df[i, :ht] = df[i, :bjet_pt] + df[i, :ljet_pt]
   
    if DEBUG
        println("SEL EV fi=", df[i, :fileindex], " f=", prfiles[df[i, :fileindex], :files],
            " ev=", int(df[i, :run]), ":", int(df[i, :lumi]), ":", int(df[i, :event]),
            " s=", sample, " p=", get_process(sample),
            " hm=", int(df[i, :hlt_mu]), " he=", int(df[i, :hlt_ele]),
            " nsm=", df[i, :n_signal_mu], " nse=", df[i, :n_signal_ele],
            " nvm=", df[i, :n_veto_mu], " nve=", df[i, :n_veto_ele],
            " nj=", df[i, :njets], " nt=", df[i, :ntags],
            " mtw=", df[i, :mtw],
            " met=", df[i, :met],
            " rms=", df[i, :ljet_rms],
        )
    end

    df[i, :passes] = true
end

println("processed $(nproc/timeelapsed) events/second")

show(df)

#skim only non-signal events
pass = (df["passes"]) | (df["sample"] .== int(hash("tchan")))

#Select only the events that actually pass
mydf = NOSKIM ? df : df[pass, :]
show(mydf)

println("NOSKIM=$NOSKIM, df=$(nrow(df)), my_df=$(nrow(mydf))")

for cn in names(mydf)
    if all(isna(mydf[cn]))
        println("$cn ISNA")
    end
end

#describe(mydf)
println("total rows = $(nrow(mydf))")
println("failure reasons: $fails")

#save output
writetable("$(output_file)_processed.csv", prfiles)
writetree("$(output_file).root", mydf)
write(jldopen("$(output_file).jld", "w"), "df", mydf)

tend = time()
ttot = tend-tstart
println("total script time $ttot seconds")
