#ifndef INFO_H
#define INFO_H

#include <TString.h>

//TString file_t = "trees_8TeV/Nominal/T_t_ToLeptons.root";
//TString file_tbar = "trees_8TeV/Nominal/Tbar_t_ToLeptons.root";

TString file_t = "trees_8TeV/mu/mc/iso/nominal/Jul15/T_t_ToLeptons.root";
TString file_tbar = "trees_8TeV/mu/mc/iso/nominal/Jul15/Tbar_t_ToLeptons.root";

//TString file_t_presel = "trees_8TeV/presel/TToLeptons_t_presel.root";
//TString file_tbar_presel = "trees_8TeV/presel/TBarToLeptons_t_presel.root";

TString file_t_presel = file_t;
TString file_tbar_presel = file_tbar;

Float_t lumi = 6784+6398+5277;

#endif
