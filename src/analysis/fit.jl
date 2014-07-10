import Base.getindex
import Base.show, Base.display

type FitResult
    means::Vector{Float64}
    sigmas::Vector{Float64}
    corr::Array{Float64, 2}
    names::Vector{ASCIIString}
    chi2::Float64
    nbins::Int64
end

Base.display(io::IO, fr::FitResult) = println(io,
    string(
        "chi2/n = ", @sprintf("%.2f", fr.chi2/fr.nbins),
        "\n",
        DataFrame(name=fr.names, mean=fr.means, sigma=fr.sigmas)
    )
)

fit_classification = {
    :beta_signal => {:tchan},
    :wzjets => {:wjets, :gjets, :dyjets, :diboson},
    :ttjets => {:ttjets, :schan, :twchan}
}

function get_fit_classification(process)
    for (k, v) in fit_classification
        process in v && return k
    end
    return :nothing
end

function cov(fr::FitResult)
    m = zeros(size(fr.corr))
    for i=1:size(m, 1)
        for j=1:size(m, 2)
            m[i,j] = fr.corr[i,j] * fr.sigmas[i] * fr.sigmas[j]
        end
    end
    return m
end

function getindex(fr::FitResult, k)
    return fr.means[indexof(fr, k)]
end

function indexof(fr::FitResult, k)
    sk = string(k)
    sk in fr.names || error("$k not in names")
    return findfirst(fr.names, sk)
end

function FitResult(fn::ASCIIString)
    fit = JSON.parse(readall(fn));
    n = length(fit["names"])
    FitResult(
        convert(Vector{Float64}, fit["means"]),
        convert(Vector{Float64}, fit["errors"]),
        convert(Array{Float64, 2}, [fit["corr"][x][y] for x=1:n,y=1:n]),
        #corr_ij = cov_ij / (sigma_i * sigma_j)
        #Float64[fit["cov"][x][y]/(fit["errors"][x] * fit["errors"][y]) for x=1:n, y=1:n],
        convert(Vector{ASCIIString}, fit["names"]),
        fit["chi2"][1],
        fit["nbins"]
    )
end

function todf(fr::FitResult)
    procs = fr.names
    df = DataFrame()

    for (m, s, p) in zip(fr.means, fr.sigmas, fr.names)
        df["mean__$p"] = m
        df["sigma__$p"] = s
    end
    df["chi2"] = fr.chi2
    df["nbins"] = fr.nbins

    for (c1, c2) in collect(combinations(fr.names, 2))
        i = findfirst(fr.names, c1)
        j = findfirst(fr.names, c2)
        df["corr__$(c1)__$(c2)"] = fr.corr[i,j]
    end
    return df
end


function run_fit(indir::ASCIIString, infiles::Vector{ASCIIString}; output=false, timeout=10.0)

    prevdir = pwd()
    workdir = "$BASE/src/fraction_fit"

    cd(workdir)

    redir(cmd) = output ? run(cmd) : readall(cmd)

    infs = join(infiles, " ")
    #run theta
    println("running fit on $infs")
    #run(`rm -f $workdir/*.cfg`)
    cmd = `$workdir/runtheta.sh bgfit.py $indir/temp_fit $infs`
    println(cmd)
    t = spawn(cmd)
    tw = timedwait(()->process_exited(t), timeout)
    tw == :ok || error("fit did not succeed, tw=$tw, $t")
    println("fit is done")
    fitres = FitResult("$indir/temp_fit.json")
    return fitres
end

function reweight_hists_to_fitres(fr, hists)
    #means = {k=>v for (k,v) in zip(fr.names, fr.means)}

    vname = hists_varname(hists)
    vname_s = vname == nothing ? "" : "$(vname)__"
    println(vname_s)
    hists = deepcopy(hists)
    function weightall(a, b)
        for k in keys(hists)
            if contains(string(k), a)
                #println("weighting $k by $(fr[b])")
                hists[k] = hists[k] * fr[b]
            end
        end
    end


    function weightsyst(a, b)
        idx = findfirst(fr.names, b)
        for k in keys(hists)
            if k == "$(vname_s)$(a)"
                #println("weighting $k by ", (fr.means[idx] + fr.sigmas[idx]), " instead of ", fr.means[idx], " to get $(k)__$(b)__up")
                #println("weighting $k by ", (fr.means[idx] - fr.sigmas[idx]), " instead of ", fr.means[idx], " to get $(k)__$(b)__down")
                hists["$(k)__$(b)__up"] = hists[k] * (fr.means[idx] + fr.sigmas[idx])/(fr.means[idx])
                hists["$(k)__$(b)__down"] = hists[k] * (fr.means[idx] - fr.sigmas[idx])/(fr.means[idx])
            end
        end
    end

    for s in ["wjets", "gjets", "dyjets", "diboson"]
        weightall(s, "wzjets")
        weightsyst(s, "wzjets")
    end

    for s in ["ttjets", "twchan", "schan"]
        weightall(s, "ttjets")
        weightsyst(s, "ttjets")
    end

    weightall("tchan", "beta_signal")
    weightsyst("tchan", "beta_signal")
    #weightall("qcd", "qcd")
    return hists
end

export FitResult, reweight_hists_to_fitres, cov, indexof
