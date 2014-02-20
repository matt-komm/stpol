
@pyimport fitted_scale_factors
const sfs = fitted_scale_factors.scale_factors
get_sf(nj, nt, lepton, fit_variables={:mu=>"qcd_mva", :ele=>"qcd_mva"}) = sfs[string(lepton)]["$(nj)j$(nt)t"][fit_variables[lepton]]

function reweight_qcd(indata::AbstractDataFrame, inds)
    
    :qcd_weight in names(indata) || error("qcd_weight not defined for data") 
    for (nj, nt) in [(2,0),(2,1),(3,1),(3,2)]
        for lep in [:mu, :ele]
            sf = get_sf(nj, nt, lep)
            d = inds[lep] & inds[:aiso] & inds[:njets][nj] & inds[:ntags][nt]
   #         println("reweight_qcd(): reweighting anti-iso ($nj jets, $nt tags, $lep) $(sum(d)) rows -> qcd_weight=$sf")
            indata[d, :qcd_weight] = sf
        end
    end
end
