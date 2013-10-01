//We need to have a missing value identifier. NaN is a good candidate but not ideal.
#include "ROOT.jl/src/fwlite.hh"
static const double NA = nan("");

static const char *PROCESS = "STPOLSEL2";

//One often needs to get the N-th value of a vector, with a placeholder for missing values
float value(const std::vector<float> *p, unsigned int n = 0)
{
    if (p->size() != 1 || p->size() < n + 1)
    {
        return NA;
    }
    return p->at(n);
}

class SimpleGetter {
    private:
        h_vfloat handle;
        const label lab;
    public:
        SimpleGetter(const char* label, const char* instance, const char* process)
        : handle()
        , lab(make_tuple(label, instance, process))
        {
            
        }

        const std::vector<float>* get(fw_event *ev) {
            return get_vfloat(&handle, ev, lab);
        }
};

//It is convenient to group objects to namespaces
//Instead of copying this for electrons etc, one should generalize!
class mu
{

private:
static const char *src;
static SimpleGetter _pt;
static SimpleGetter _eta;
static SimpleGetter _phi;

public:
const static float pt(fw_event *ev)
{
    return value(_pt.get(ev));
}
};

const char* mu::src = "goodSignalMuonsNTupleProducer";
SimpleGetter mu::_pt(mu::src, "Pt", PROCESS);
SimpleGetter mu::_eta(mu::src, "Eta", PROCESS);
SimpleGetter mu::_phi(mu::src, "Phi", PROCESS);
