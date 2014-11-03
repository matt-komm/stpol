#!/home/software/.julia/CMSSW/julia
println("running skim.jl")
tstart = time()
println(
    "hostname $(gethostname()) ",
    "SLURM_JOB_ID" in keys(ENV) ? ENV["SLURM_JOB_ID"] : getpid()
)

using CMSSW, DataFrames, HEP

include("../analysis/base.jl")

output_file = ARGS[1]

flist = Any[]
append!(flist, ARGS[2:length(ARGS)])

#check input files
good_filelist = ASCIIString[]
for i=1:length(flist)

    if !beginswith(flist[i], "file:")
        flist[i] = string("file:",flist[i])
    end

    try
        println("trying to open file $(flist[i])")
        ev = Events([flist[i]])
        if length(ev)>0
            println("adding good file $(flist[i])")
            push!(good_filelist, flist[i])
        else
            warn("file was empty: $(flist[i])")
        end
    catch err
        warn("could not open events from $(flist[i]): $err")
    end
end

println("opening files from $good_filelist")
flistd = {f=>i for (f, i) in zip(good_filelist, 1:length(good_filelist))}

#try to load the Events
events = Events(convert(Vector{ASCIIString}, good_filelist))

#save information on spectator jets
const do_specjets = true

maxev = length(events)
println("running over $maxev events")

#processes the decay tree string to get the generated parent of the lepton
gen_parent(s::NAtype) = NA
function gen_parent(s::ASCIIString)
    arr = map(x->int(split(x, ":")[1]), map(x->strip(x)[2:end], split(s, ",")))
    idx = findfirst(x-> !(abs(x) in [11,13]), arr)
    return (idx > 0 && idx<= length(arr)) ? arr[idx] : NA
end

#events
df = similar(#Data frame as big as the input
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
            cos_theta_whel_lj=Float32[],
            cos_theta_bl=Float32[],
            cos_theta_lj_gen=Float32[],
            cos_theta_whel_lj_gen=Float32[],
            cos_theta_bl_gen=Float32[],
            met=Float32[], njets=Int32[], ntags=Int32[], mtw=Float32[],
            met_phi=Float32[],

            C=Float32[], D=Float32[], circularity=Float32[], sphericity=Float32[], isotropy=Float32[], aplanarity=Float32[], thrust=Float32[],
            C_with_nu=Float32[],
            top_mass=Float32[], top_pt=Float32[], top_eta=Float32[], top_phi=Float32[],
            top_mass_gen=Float32[], top_pt_gen=Float32[], top_eta_gen=Float32[], top_phi_gen=Float32[],

            w_mass_gen=Float32[], w_pt_gen=Float32[], w_eta_gen=Float32[], w_phi_gen=Float32[],
            w_mass=Float32[], w_pt=Float32[], w_eta=Float32[], w_phi=Float32[],

            #wjets_cls=Int32[],
            jet_cls=Int32[],
            hadronic_pt=Float32[], hadronic_eta=Float32[], hadronic_phi=Float32[], hadronic_mass=Float32[],
            shat_pt=Float32[], shat_eta=Float32[], shat_phi=Float32[], shat_mass=Float32[],
            shat=Float32[],
            ht=Float32[],

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
            gen_parent_id=Int32[],

            top_weight=Float32[],
            top_weight__up=Float32[],
            top_weight__down=Float32[],

            b_weight=Float32[],
            b_weight__bc__up=Float32[],
            b_weight__bc__down=Float32[],
            b_weight__l__up=Float32[],
            b_weight__l__down=Float32[],
            b_weight_simple=Float32[],
            b_weight_tchpt=Float32[],
            b_weight_tchpt__bc__up=Float32[],
            b_weight_tchpt__bc__down=Float32[],
            b_weight_tchpt__l__up=Float32[],
            b_weight_tchpt__l__down=Float32[],

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

prfiles = similar(
    DataFrame(
        files=ASCIIString[],
        total_processed=Int64[],
        cls=Any[]
    ),
    length(good_filelist)
)

i = 1

#Get the number of processed events from all files
for fi in good_filelist
    #filename
    prfiles[i, :files] = fi

    #total number of processed (generated) events
    x = CMSSW.get_counter_sum([fi], "singleTopPathStep1MuPreCount")
    prfiles[i, :total_processed] = x

    #classify sample according to file name
    prfiles[i, :cls] = SingleTopBase.sample_type(fi)
    i += 1
end

all(prfiles[:files] .== good_filelist) || error("mismatch in input files")

nproc = 0

#keep track of the reasons why an event was not further processed
fails = {
    :lepton => 0,
    :met => 0,
    :jet => 0,
}

tic()

#keep track of the previously processed file
prevfile = ""

#Loop over the events
println("Beginning event loop")

totype(x,t) = isna(x) ? NA : t(x)
totype_i(x) = totype(x, int)

for i=1:maxev
    #println(i)
    nproc += 1

    #progress printout
    if maxev>1000 && nproc%(ceil(maxev/20)) == 0
        println("$nproc ($(ceil(nproc/maxev*100.0))%) events processed")
        toc()
        tic()
    end

    to!(events, i)

    df[i, :passes] = false

    df[i, :gen_lepton_id] = events[sources[(:lepton, :gen, :id)]] |> totype_i

    #string representations of the feynman diagrams
    #genstring_mu = events[sources[(:muon, :geninfo)]]
    #genstring_ele = events[sources[(:electron, :geninfo)]]

    df[i, :hlt] = passes_hlt(events, hlts)
    df[i, :hlt_mu] = passes_hlt(events, HLTS[:mu])
    df[i, :hlt_ele] = passes_hlt(events, HLTS[:ele])

    ##println(gen_id, " '", genstring_mu, "' '", genstring_ele, "'")


    df[i, :cos_theta_lj_gen] = events[sources[:cos_theta_lj_gen]] |> ifpresent
    df[i, :cos_theta_whel_lj_gen] = events[sources[:cos_theta_whel_lj_gen]] |> ifpresent
    df[i, :cos_theta_bl_gen] = events[sources[:cos_theta_bl_gen]] |> ifpresent

    df[i, :run], df[i, :lumi], df[i, :event] = where(events)
    fn = string("file:", get_current_file_name(events))

    if fn != prevfile
        println("$i switching to $fn")
        prevfile = fn
    end

    findex = flistd[fn]
    df[i, :fileindex] = findex

    if fn != prfiles[findex, :files]
        error("incorrect file: $fn $(prfiles[findex, :files])")
    end


    df[i, :b_weight] = events[sources[weight(:btag)]]
    df[i, :b_weight_tchpt] = events[sources[weight(:btag, :tchpt)]]|>ifpresent
    df[i, :b_weight_simple] = events[sources[weight(:btag, :simple)]]|>ifpresent

    df[i, :b_weight__bc__up] = events[sources[weight(:btag, :bc, :up)]]
    df[i, :b_weight__bc__down] = events[sources[weight(:btag, :bc, :down)]]
    df[i, :b_weight__l__up] = events[sources[weight(:btag, :l, :up)]]
    df[i, :b_weight__l__down] = events[sources[weight(:btag, :l, :down)]]
    
    df[i, :b_weight_tchpt__bc__up] = events[sources[weight(:btag, :tchpt, :bc, :up)]]
    df[i, :b_weight_tchpt__bc__down] = events[sources[weight(:btag, :tchpt, :bc, :down)]]
    df[i, :b_weight_tchpt__l__up] = events[sources[weight(:btag, :tchpt, :l, :up)]]
    df[i, :b_weight_tchpt__l__down] = events[sources[weight(:btag, :tchpt, :l, :down)]]

    df[i, :top_weight] = events[sources[weight(:top)]]
    df[i, :top_weight__up] = df[i, :top_weight]^2
    df[i, :top_weight__down] = 1.0

    df[i, :gen_weight] = events[sources[weight(:gen)]]

    cls = prfiles[findex, :cls]
    sample = cls[:sample]

    df[i, :subsample] = int(hash(string(sample)))
    df[i, :sample] = int(hash(string(get_process(sample))))
    df[i, :fname] = int(hash(fn))
    df[i, :xs] = haskey(cross_sections, sample) ? float32(cross_sections[sample]) : NA
    df[i, :isolation] = int(hash(string(cls[:iso])))
    df[i, :systematic] = int(hash(string(cls[:systematic])))
    df[i, :processing_tag] = int(hash(string(cls[:tag])))

    nmu = events[sources[:nsignalmu]]
    nele = events[sources[:nsignalele]]

    df[i, :n_signal_mu] = nmu
    df[i, :n_signal_ele] = nele
    
    for k in [:Pt, :Eta, :Phi, :Mass]
        p = part(:top, k, :gen)
        df[i, lowercase("top_$(k)_gen")|>symbol] = events[sources[p]] |> ifpresent
    end

    ### Cuts start here
    if isna(nmu) || isna(nele)
        fails[:lepton] += 1
        continue
    end

    lepton_type = NA
    if nmu==1 && nele==0
        lepton_type = :muon
        df[i, :lepton_type] = 13
        genparent = gen_parent(events[sources[(:muon, :geninfo)]])
        df[i, :gen_parent_id] = genparent |> totype_i
    elseif nele==1 && nmu==0
        lepton_type = :electron
        df[i, :lepton_type] = 11
        genparent = gen_parent(events[sources[(:electron, :geninfo)]])
        df[i, :gen_parent_id] = genparent |> totype_i
    else
        fails[:lepton] += 1
        continue
    end

    nveto_mu = events[sources[vetolepton(:mu)]]
    nveto_ele = events[sources[vetolepton(:ele)]]

    df[i, :n_veto_mu] = nveto_mu
    df[i, :n_veto_ele] = nveto_ele

    if nveto_mu != 0 || nveto_ele != 0
        fails[:lepton] += 1
        continue
    end

    if lepton_type == :muon || lepton_type == :electron
        df[i, :lepton_id] = events[sources[part(lepton_type, :genPdgId)]] |> ifpresent |> totype_i
        df[i, :lepton_eta] = events[sources[part(lepton_type, :Eta)]] |> ifpresent
        df[i, :lepton_pt] = events[sources[part(lepton_type, :Pt)]] |> ifpresent
        df[i, :lepton_iso] = events[sources[part(lepton_type, :relIso)]] |> ifpresent
        df[i, :lepton_charge] = events[sources[part(lepton_type, :Charge)]] |> ifpresent
        df[i, :lepton_phi] = events[sources[part(lepton_type, :Phi)]] |> ifpresent
        df[i, :mtw] = events[sources[part(lepton_type, :mtw)]] |> ifpresent
    end
    
    #println("lepton")

    df[i, :met] = events[sources[:met]] |> ifpresent
    df[i, :met_phi] = events[sources[(:met, :phi)]] |> ifpresent

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
    df[i, :bjet_id] = events[sources[:bjet_partonFlavour]] |> ifpresent |> totype_i
    #df[i, :bjet_bd_a] = events[sources[:bjet_bDiscriminatorTCHP]] |> ifpresent
    df[i, :bjet_bd_b] = events[sources[:bjet_bDiscriminatorCSV]] |> ifpresent
    df[i, :bjet_phi] = events[sources[:bjet_Phi]] |> ifpresent
    df[i, :bjet_dr] = events[sources[:bjet_deltaR]] |> ifpresent
    df[i, :bjet_pumva] = events[sources[:bjet_puMva]] |> ifpresent

    df[i, :ljet_pt] = events[sources[:ljet_Pt]] |> ifpresent
    df[i, :ljet_eta] = events[sources[:ljet_Eta]] |> ifpresent
    df[i, :ljet_mass] = events[sources[:ljet_Mass]] |> ifpresent
    df[i, :ljet_id] = events[sources[:ljet_partonFlavour]] |> ifpresent |> totype_i
    #df[i, :ljet_bd_a] = events[sources[:ljet_bDiscriminatorTCHP]] |> ifpresent
    df[i, :ljet_bd_b] = events[sources[:ljet_bDiscriminatorCSV]] |> ifpresent
    df[i, :ljet_rms] = events[sources[:ljet_rms]] |> ifpresent
    df[i, :ljet_phi] = events[sources[:ljet_Phi]] |> ifpresent
    df[i, :ljet_dr] = events[sources[:ljet_deltaR]] |> ifpresent
    df[i, :ljet_pumva] = events[sources[:ljet_puMva]] |> ifpresent
    #println("jet")

    df[i, :jet_cls] = jet_cls_to_number(jet_classification(df[i, :ljet_id], df[i, :bjet_id]))
    df[i, :cos_theta_lj] = events[sources[:cos_theta_lj]] |> ifpresent
    df[i, :cos_theta_whel_lj] = events[sources[:cos_theta_whel_lj]] |> ifpresent
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
        jet_ids  = map(totype_i, events[sources[part(:jets, :partonFlavour)]])
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
    df[i, :C_with_nu] = events[sources[:C_with_nu]]

    #df[i, :wjets_cls] = events[sources[:wjets_cls]] |> ifpresent
    for k in [:Pt, :Eta, :Phi, :Mass]
    #for k in [:Mass, :Pt]
        p = part(:top, k, :reco)
        df[i, lowercase("top_$k")|>symbol] = events[sources[p]] |> ifpresent
    end
    
    for k in [:Pt, :Eta, :Phi, :Mass]
        for x in [:shat, :hadronic]
            p = part(x, k)
            df[i, lowercase("$(x)_$(k)")|>symbol] = events[sources[p]] |> ifpresent
        end
    end
    
    for k in [:Pt, :Eta, :Phi, :Mass]
        for x in [:W]
            p = part(x, k, :reco)
            df[i, lowercase("$(x)_$(k)")|>symbol] = events[sources[p]] |> ifpresent
            
            p = part(x, k, :gen)
            df[i, lowercase("$(x)_$(k)_gen")|>symbol] = events[sources[p]] |> ifpresent
        end
    end

    if lepton_type == :muon || lepton_type == :electron
        df[i, :nu_soltype] = events[sources[part(lepton_type, :nu_soltype)]] |> ifpresent
    end

    ##calculate the invariant mass of the system
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
    df[i, :ht] = df[i, :ljet_pt] + df[i, :bjet_pt]

    df[i, :passes] = true
end

#println(df)

#skim only non-signal events
pass = (df[:passes]) | (df[:sample] .== int(hash("tchan")))
#Select only the events that actually pass
mydf = df[pass, :]

#keep all rows
#mydf = df

for cn in names(mydf)
    if all(isna(mydf[cn]))
        println("$cn ISNA")
    end
end

#describe(mydf)
println("total rows = $(nrow(mydf))")
println("failure reasons: $fails")

###
### write metadata
###

#save output
prfile = "$(output_file)_processed.csv"
isfile(prfile) && rm(prfile)
writetable(prfile, prfiles)
if nrow(prfiles)>0
    sleep(1)
    run(`timeout 60 sync`)
    isfile(prfile) || error("processed file not created")

    if nrow(mydf)>0
        c = readall(prfile)
        if (length(c) > 0)
            if !(all(nrow(readtable(prfile)) == nrow(prfiles)))
                error("problem writing processed files to $prfile")
            end
        else
            warn("$prfile was empty, while nrow(prfiles)=$(nrow(prfiles))")
        end
    end
end


###
### ROOT output
###
println("root...")
tempf = mktemp()[1]
outfile = "$(output_file).root"
println("writing to temporary file $(tempf)")
writetree(tempf, mydf)
sleep(1)
for i=1:5
    try
        println("cleaning $outfile...");isfile(outfile) && rm(outfile)
        println("copying...");cp(tempf, outfile)
        sleep(1)
        run(`timeout 60 sync`)
        s = stat(outfile)
        s.size == 0 && error("file corrupted: size=0")
        tdf = TreeDataFrame(outfile)
        nrow(tdf) == nrow(mydf) || error("file corrupted, $(nrow(tdf))!=$(nrow(mydf))")

        break
    catch err
        println("$err: retrying")
        sleep(5)
    end
end

tend = time()
ttot = tend-tstart
println("total script time $ttot seconds")
