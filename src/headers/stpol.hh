//We need to have a missing value identifier. NaN is a good candidate but not ideal.
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


//It is convenient to group objects to namespaces
//Instead of copying this for electrons etc, one should generalize!
namespace mu
{

static const char *mu_src = "goodSignalMuonsNTupleProducer";

const label pt = make_tuple(mu_src, "Pt", PROCESS);
h_vfloat *h_pt = new h_vfloat();

double get_pt(fw_event *ev)
{
    const std::vector<float> *p = get_vfloat(h_pt, ev, pt);
    return value(p);
}
};

