#include <iostream>
#include <TSystem.h>
#include <DataFormats/FWLite/interface/Event.h>
#include "DataFormats/FWLite/interface/Handle.h"
#include <FWCore/FWLite/interface/AutoLibraryLoader.h>

#include <SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h>
#include <DataFormats/MuonReco/interface/Muon.h>
#include <PhysicsTools/FWLite/interface/TFileService.h>
#include <FWCore/ParameterSet/interface/ProcessDesc.h>
#include <FWCore/PythonParameterSet/interface/PythonProcessDesc.h>
#include <DataFormats/Common/interface/MergeableCounter.h>

extern "C" {

    void initialize()
    {
        gSystem->Load( "libFWCoreFWLite" );
        AutoLibraryLoader::enable();
        gSystem->Load("libDataFormatsFWLite");
    }

    void *make_handle_vfloat()
    {
        return new fwlite::Handle<std::vector<float>>();
    }

    TFile *make_tfile(const char *fname)
    {
        return TFile::Open(fname);
    }

    fwlite::Event *make_event(TFile *tfile)
    {
        return new fwlite::Event(tfile);
    }

    void event_toBegin(fwlite::Event *event)
    {
        event->toBegin();
    }

    void event_getByLabel(fwlite::Event *evt, const char *label, void *handle, const void *out)
    {
        const edm::InputTag src(label);
        edm::Handle<std::vector<float>> *_handle = (edm::Handle<std::vector<float>> *)handle;
        evt->getByLabel(src, *_handle);
        out = &(_handle->product()[0]);
        //return (_handle->product());
    }

    bool event_atEnd(fwlite::Event *event)
    {
        return event->atEnd();
    }

    fwlite::Event *event_next(fwlite::Event *event)
    {
        return ++event;
    }

    void hello()
    {
        std::cout << "Hello!" << std::endl;
    }
}
