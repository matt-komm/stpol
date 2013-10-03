#include "SingleTopPolarization/FWTools/interface/fwlite.hh" //In $STPOL_DIR/deps

namespace stpol {

//A private interface that may change    
namespace unstable {
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


//A simple Handle<vector<float>> wrapper
class SimpleGetterVFloat {
    private:
        h_vfloat handle; //the underlying data container
        const label lab; //the name of the product that is used

    public:
        SimpleGetterVFloat(const char* label, const char* instance, const char* process)
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
class Lepton 
{

protected:
//Internal interface
const char *src;

//Handle, label pairs for the data in the edm ntuple
SimpleGetterVFloat _pt;
SimpleGetterVFloat _eta;
SimpleGetterVFloat _phi;

Lepton(const char* _src) :
    src(_src),
    _pt(SimpleGetterVFloat(_src, "Pt", PROCESS)),
    _eta(SimpleGetterVFloat(_src, "Eta", PROCESS)),
    _phi(SimpleGetterVFloat(_src, "Phi", PROCESS)) {
}

float get(fw_event *ev, SimpleGetterVFloat& g) {
    return value(g.get(ev));
}

};



} //namespace unstable

// ----------------------
// -- PUBLIC INTERFACE --
// ----------------------
// Anything that is exported here as public will probably not change in declaration(shape).
// For example, you can always call stpol::stable::signal::muon.pt(events).
// Precise definition(implementation) may change, so you need not know how the pt is accessed for the signal muon.
// To make the existing analysis code work with a different "backend", such as a flat ROOT TTree instead of the EDM format,
// one would have to implement this interface with exactly the same structure as here.
namespace stable {
   
    //A type for which there is no physical value available
    typedef double na_type;

    //A placeholder value.
    static const na_type NA = unstable::NA;

    //Check if something was NA. Depends on the type of the NA, but in general will be kept stable.
    bool is_na(na_type v) { return std::isnan(v); }

    //Interfaces for the leptons
    class Muon : public unstable::Lepton {
        public:
            Muon() : unstable::Lepton("goodSignalMuonsNTupleProducer") {
            }

            float pt(fw_event *ev) { return get(ev, _pt); };
            float eta(fw_event *ev) { return get(ev, _eta); };
            float phi(fw_event *ev) { return get(ev, _phi); };

    };
    
    class Electron : public unstable::Lepton {
        public:
            Electron() : unstable::Lepton("goodSignalElectronsNTupleProducer") {
            }
            
            float pt(fw_event *ev) { return get(ev, _pt); };
            float eta(fw_event *ev) { return get(ev, _eta); };
            float phi(fw_event *ev) { return get(ev, _phi); };
    };
   
    namespace signal {
        static Muon muon;
        static Electron electron;
    }

} //namespace stable

} //namespace stpol
