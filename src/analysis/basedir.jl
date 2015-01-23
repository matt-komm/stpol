
#paths to be added here
if ENV["USER"] == "joosep"
    const BASE = joinpath(ENV["HOME"], "Dropbox/kbfi/top/stpol")
elseif ENV["USER"] == "andres"
    const BASE = joinpath(ENV["HOME"], "single_top/stpol_pdf")
else
    error("undefined BASE")
end
