
function part(x, y)
    return symbol(string(x, "_", y))
end

function ifpresent(arr, n::Integer=1)
    if all(isna(arr)) 
        return NA
    end
    if length(arr)==n
        return arr[n]
    else
        return NA
    end
end

ispresent(x) = (typeof(x) != NAtype && !any(isna(x)))

function either(a, b, n::Integer=1)
    if length(a)==n && length(b)==0
        return (a[n], :first)
    elseif length(b)==n && length(a)==0
        return (b[n], :second)
    else
        return (NA, :neither)
    end
end
