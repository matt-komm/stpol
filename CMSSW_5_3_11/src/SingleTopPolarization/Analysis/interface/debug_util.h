
#include <iostream>
#include <algorithm>

template <typename T>
const std::string vec_to_str(std::vector<T> vec) {
    std::stringstream ss;
    ss << "(";
    unsigned int i = 0;
    for (auto & c : vec) {
        ss << c;
        if (i<vec.size()-1)
            ss << ", ";
        i++;
    }
    ss << ")";
    return ss.str();
}

