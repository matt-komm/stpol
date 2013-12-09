const lumis = {:mu => 19764, :ele =>19820}

include("selection.jl")

function reweight(indata)
    indata["totweight"] = 1.0
    indata["fitweight"] = 1.0
    
    #apply PU weighting
    indata[:(sample .== "data_mu"), :pu_weight] = 1.0
    indata[:(sample .== "data_ele"), :pu_weight] = 1.0
    
    indata[:totweight] = indata[:pu_weight].*indata[:totweight]
    
    #electron channel QCD weight (ad-hoc)
    indata[:((sample .== "data_ele") .* (isolation .== "antiiso")), :totweight] = 0.00005
    indata[:((sample .== "data_mu") .* (isolation .== "antiiso")), :totweight] = 0.000025
    indata[:((sample .== "data_mu") .* (isolation .== "antiiso") .* (njets .== 3) .* (ntags .== 2)), :totweight] = 0.0000000002;
    indata[:((sample .== "data_mu") .* (isolation .== "antiiso") .* (njets .== 3) .* (ntags .== 1)), :totweight] = 0.000000002;
    indata[:((sample .== "data_ele") .* (isolation .== "antiiso") .* (njets .== 3) .* (ntags .== 2)), :totweight] = 0.000000002;
    indata[:((sample .== "data_ele") .* (isolation .== "antiiso") .* (njets .== 3) .* (ntags .== 1)), :totweight] = 0.0000002;
    
    #Sherpa reweight to madgraph yield
    indata[:(sample .== "wjets_sherpa"), :xsweight] = 0.04471345 .* indata[sample_is("wjets_sherpa"), :xsweight]
    
    #remove events with incorrect weights
    indata[isna(indata[:totweight]), :totweight] = 0.0
    
    ##########
    #  LUMI  #
    ##########
    
    println("performing xs reweighting")
    for c in [:mu, :ele]
        tic()
        println("xs reweighting: $c")
        indata[selections[c], :xsweight] *= lumis[c]
        toc()
    end
    
    indata[sample_is("data_mu"), :xsweight] = 1.0
    indata[sample_is("data_ele"), :xsweight] = 1.0
end

#########
# SPLIT #
#########
#println("splitting")
#for nt in Any[1, 2]
#    println("ntags=$nt")
#    tic()
#    if isna(nt)
#        df = select(:(isna(ntags)), indata)
#    else
#        df = select(:(ntags .== $nt), indata)
#    end
#    df = DataFrame(df)
#    of = jldopen("$ofname.$(nt)T", "w")
#    write(of, "df", df)
#    close(of)
#    toc()
#end
