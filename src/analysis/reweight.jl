if !isdefined(:REWEIGHT)
const _lumis = JSON.parse(readall("$BASE/metadata/lumis.json"))
const lumis = {symbol(k)=>v for (k,v) in _lumis}

const lumis_id = {:13 => lumis[:mu], :11 => lumis[:ele]}

include("selection.jl")

function reweight(indata, inds)

    indata["totweight"] = 1.0
    indata["fitweight"] = 1.0
    
    indata[inds[:data], :pu_weight] = 1.0
    indata[:totweight] = indata[:totweight].*indata[:pu_weight].*indata[:b_weight]
    
    #Sherpa reweight to madgraph yield
    #indata[indata["sample"].==int(hash("wjets_sherpa")), :xsweight] = 0.04471345 .* indata[sample_is("wjets_sherpa"), :xsweight]
    
    #remove events with incorrect weights
    indata[isna(indata[:totweight]), :totweight] = 0.0
    
    ##########
    #  LUMI  #
    ##########
    
    for c in [:mu, :ele]
        tic()
        println("xs reweighting: $c")
        indata[inds[c], :xsweight] *= lumis[c]
        toc()
    end
    
    indata[inds[:data], :xsweight] = 1.0
end

const REWEIGHT=1

end #ifdef
