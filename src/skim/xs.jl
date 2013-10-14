function sample_type(fn, prefix="file:/hdfs/cms/store/user")
    r = Regex("$prefix/(.*)/(.*)/(.*)/(.*)/(.*)/output_(.*).root")
    m = match(r, fn)
    
    tag = m.captures[2]
    iso = m.captures[3]
    syst = m.captures[4]
    samp = m.captures[5]
    
    if m != nothing
        return {:tag => tag, :iso => iso, :systematic => syst, :sample => samp}
    else
        warn("no match for $fn")
        return {
            :tag => :unknown,
            :iso => :unknown,
            :systematic => :unknown,
            :sample => :unknown
        }
    end
end

ENV["PYTHONPATH"] = string(joinpath(ENV["STPOL_DIR"]), ":", ENV["PYTHONPATH"])
using PyCall
cross_sections = pyimport("plots.common.cross_sections")[:xs]
