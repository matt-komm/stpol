//This file can be copied as an example for your own loop
#include "ROOT.jl/src/fwlite.hh"
#include "src/headers/stpol.hh" //present in $STPOL_DIR/src/headers/stpol.hh

int main(int argc, char **argv)
{

    //Call the FWLite library loaders
    initialize();

    //Our list of input files
    vector<string> fn;
    fn.push_back("test_edm.root");

    fw_event *events = new fw_event(fn);

    for (unsigned int i = 0; i < events->size(); i++)
    {
        events->to(i);

        float pt = mu::get_pt(events); //defined in stpol.hh
        std::cout << pt << std::endl;
    }

    return 0;
}
