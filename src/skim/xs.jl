using DataFrames

function sample_type(fn, prefix="file:/hdfs/cms/store/user")
    r = Regex("$prefix/(.*)/(.*)/(.*)/(.*)/(.*)/output_(.*).root")
    m = match(r, fn)
   
    if m==nothing
        warn("no match for $fn")
        return {
            :tag => :unknown,
            :iso => :unknown,
            :systematic => :unknown,
            :sample => :unknown
        }
    end
    
    tag = m.captures[2]
    iso = m.captures[3]
    syst = m.captures[4]
    samp = m.captures[5]
    return {:tag => tag, :iso => iso, :systematic => syst, :sample => samp}
end

df = readtable("cross_sections.txt", allowcomments=true)
cross_sections = Dict{String, Float64}()
for i=1:nrow(df)
    cross_sections[df[i, 1]] = df[i, 2]
end
#cross_sections = pyimport("plots.common.cross_sections")[:xs]
