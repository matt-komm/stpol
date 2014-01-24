const jet_classifications = [:bb, :gg, :cc, :bc, :bX, :cX, :gX, :XX]

#returns the 2-jet classification basesd on the pdgid of the 2 jets
function jet_classification(id1::Number, id2::Number)
    a = abs(int(id1))
    b = abs(int(id2))
    a==5 && b==5 && return :bb
    a==21 && b==21 && return :gg
    a==4 && b==4 && return :cc
    
    (a==5 && b==4) || (b==5 && a==4) && return :bc
    a==5 || b==5 && return :bX
    a==4 || b==4 && return :cX
    a==21 || b==21 && return :gX
    return :XX
end

function jet_cls_to_number(s::Symbol)
    ind = indexin([s], jet_classifications)
    return length(ind)==1 ? ind[1] : -1
end

function jet_cls_from_number(i::Integer)
    i>0 && i<=length(jet_classifications) ? jet_classifications[i] : :unknown
end

function jet_cls_heavy_light(s::Symbol)
    if s in [:bb, :cc, :bX, :cX, :bc]
        return :heavy
    elseif s in [:gg, :gX, :XX]
        return :light
    else
        error("unknown jet classification $s")
    end
end

jet_cls_heavy_light(x::Integer) = jet_cls_heavy_light(jet_cls_from_number(x))