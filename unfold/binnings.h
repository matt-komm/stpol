#ifndef BINNINGS_H
#define BINNINGS_H
#include "TString.h"

// Number of reconstructed bins should be twice as much as generated
// x: generated
// y: reconstructed
// cosTheta

TString varname = "cos#theta_{l,j}";
TString var_x = "true_cos_theta";
TString var_y = "cos_theta";
const Double_t var_min = -1;
const Double_t var_max = 1;

//const Int_t bin_x = 3;
//const Int_t bin_y = 6;

//const Int_t bin_x = 5;
//const Int_t bin_y = 10;

const Int_t bin_x = 7;
const Int_t bin_y = 14;

// 3 6

//Double_t list_x[bin_x+1] = {-1, 0.051, 0.446, 1};
//Double_t list_y[bin_y+1] = {-1, -0.1982, 0.0854, 0.2956, 0.4814, 0.6546, 1};

// 5 10

//Double_t list_x[bin_x+1] = {-1, -0.1558, 0.142, 0.3718, 0.5904, 1};
//Double_t list_y[bin_y+1] = {-1, -0.3708, -0.1316, 0.04, 0.1726, 0.2956, 0.4118, 0.5162, 0.6186, 0.7306, 1};

// zero
//Double_t list_x[bin_x+1] = {-1, -0.3558, 0.0, 0.4418, 0.6604, 1};
//Double_t list_y[bin_y+1] = {-1, -0.3708, -0.1316, 0.0, 0.1326, 0.2556, 0.4018, 0.5162, 0.6186, 0.7306, 1};

// 7 14

//Double_t list_x[bin_x+1] = {-1, -0.2778, -0.0162, 0.176, 0.3414, 0.4964, 0.6572, 1};
//Double_t list_y[bin_y+1] = {-1, -0.4674, -0.2558, -0.1028, 0.019, 0.116, 0.2126, 0.2956, 0.379, 0.4568, 0.5302, 0.6038, 0.6822, 0.7694, 1};

// 7 14 zero
Double_t list_x[bin_x+1] = {-1, -0.2778, 0.0, 0.176, 0.3414, 0.4964, 0.6572, 1};
Double_t list_y[bin_y+1] = {-1, -0.4674, -0.2558, -0.1028, 0.0, 0.116, 0.2126, 0.2956, 0.379, 0.4568, 0.5302, 0.6038, 0.6822, 0.7694, 1};
#endif
