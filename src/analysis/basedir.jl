
#paths to be added here
if ENV["USER"] == "joosep"
    const BASE = joinpath(ENV["HOME"], "Dropbox/kbfi/top/stpol")
else
    error("undefined BASE")
end
