for x in [:tchan, :twchan, :schan, :wjets, :data_mu, :data_ele, :diboson, :gjets, :dyjets, :ttjets]
    run(`julia yields.jl $x`)
end
