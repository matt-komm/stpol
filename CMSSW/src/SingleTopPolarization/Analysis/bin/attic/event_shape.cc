#include "event_shape.h"

void EvtShapeVars::initialize_branches() {
    if( doEvtShapeVars ){
        branch_vars.vars_float["sphericity"] = BranchVars::def_val;
        branch_vars.vars_float["aplanarity"] = BranchVars::def_val;
        branch_vars.vars_float["C"] = BranchVars::def_val;
        branch_vars.vars_float["D"] = BranchVars::def_val;
        branch_vars.vars_float["sphericity_withNu"] = BranchVars::def_val;
    }
}

EvtShapeVars::EvtShapeVars(const edm::ParameterSet& pars, BranchVars& _branch_vars) :
CutsBase(_branch_vars),
leptonChannel(pars.getParameter<std::string>("leptonChannel"))
{
    doEvtShapeVars = pars.getParameter<bool>("doEvtShapeVars");
    initialize_branches();
    
    if( leptonChannel == "mu"){
        lepPtSrc = pars.getParameter<edm::InputTag>("muPtSrc");
        lepEtaSrc = pars.getParameter<edm::InputTag>("muEtaSrc");
        lepPhiSrc = pars.getParameter<edm::InputTag>("muPhiSrc");
    }
    
    if( leptonChannel == "ele"){
        lepPtSrc = pars.getParameter<edm::InputTag>("elPtSrc");
        lepEtaSrc = pars.getParameter<edm::InputTag>("elEtaSrc");
        lepPhiSrc = pars.getParameter<edm::InputTag>("elPhiSrc");
    }
    
    bjPtSrc = pars.getParameter<edm::InputTag>("bjPtSrc");
    bjEtaSrc = pars.getParameter<edm::InputTag>("bjEtaSrc");
    bjPhiSrc = pars.getParameter<edm::InputTag>("bjPhiSrc");
    
    ljPtSrc = pars.getParameter<edm::InputTag>("ljPtSrc");
    ljEtaSrc = pars.getParameter<edm::InputTag>("ljEtaSrc");
    ljPhiSrc = pars.getParameter<edm::InputTag>("ljPhiSrc");
    
    nuPtSrc = pars.getParameter<edm::InputTag>("nuPtSrc");
    nuEtaSrc = pars.getParameter<edm::InputTag>("nuEtaSrc");
    nuPhiSrc = pars.getParameter<edm::InputTag>("nuPhiSrc");
}

bool EvtShapeVars::process(const edm::EventBase& event) {
    pre_process();
    float lep_pt, lep_eta, lep_phi;
    float bj_pt, bj_eta, bj_phi;
    float lj_pt, lj_eta, lj_phi;
    float nu_pt, nu_eta, nu_phi;
    
    lep_pt = get_collection_n<float>(event, lepPtSrc, 0);
    lep_eta = get_collection_n<float>(event, lepEtaSrc, 0);
    lep_phi = get_collection_n<float>(event, lepPhiSrc, 0);
    
    lj_pt = get_collection_n<float>(event, ljPtSrc, 0);
    lj_eta = get_collection_n<float>(event, ljEtaSrc, 0);
    lj_phi = get_collection_n<float>(event, ljPhiSrc, 0);
    
    bj_pt = get_collection_n<float>(event, bjPtSrc, 0);
    bj_eta = get_collection_n<float>(event, bjEtaSrc, 0);
    bj_phi = get_collection_n<float>(event, bjPhiSrc, 0);
    
    nu_pt = get_collection_n<float>(event, nuPtSrc, 0);
    nu_eta = get_collection_n<float>(event, nuEtaSrc, 0);
    nu_phi = get_collection_n<float>(event, nuPhiSrc, 0);
    
    if(bj_pt != bj_pt || lj_pt != lj_pt || lep_pt != lep_pt || nu_pt != nu_pt) //evt shape vars not calculated in case of nan values
        return true;
    
    TVector3 lep, bj, lj, nu;
    lep.SetPtEtaPhi(lep_pt, lep_eta, lep_phi);
    bj.SetPtEtaPhi(bj_pt, bj_eta, bj_phi);
    lj.SetPtEtaPhi(lj_pt, lj_eta, lj_phi);
    nu.SetPtEtaPhi(nu_pt, nu_eta, nu_phi);
    
    const int nr_particles = 4;
    TVector3 particles[nr_particles] = {lep, bj, lj, nu};
    
    TMatrixD MomentumTensor(nr_particles-1,nr_particles-1);
    TMatrixD MomentumTensor_withNu(nr_particles,nr_particles);
    
    double p2_sum = 0.;
    double p2_sum_withNu = 0.;
    
    for(int i = 0; i != nr_particles; i++){ //loop over particles
        double px = particles[i].Px();
        double py = particles[i].Py();
        double pz = particles[i].Pz();
        
        //fill MomentumTensor by hand
        if(i < nr_particles-1){
            MomentumTensor(0, 0) += px * px;
            MomentumTensor(0,1) += px * py;
            MomentumTensor(0,2) += px * pz;
            MomentumTensor(1,0) += py * px;
            MomentumTensor(1,1) += py * py;
            MomentumTensor(1,2) += py * pz;
            MomentumTensor(2,0) += pz * px;
            MomentumTensor(2,1) += pz * py;
            MomentumTensor(2,2) += pz * pz;
            
            //add 3 momentum squared to sum
            p2_sum += (px * px + py * py + pz * pz);
        }
        
        MomentumTensor_withNu(0, 0) += px * px;
        MomentumTensor_withNu(0,1) += px * py;
        MomentumTensor_withNu(0,2) += px * pz;
        MomentumTensor_withNu(1,0) += py * px;
        MomentumTensor_withNu(1,1) += py * py;
        MomentumTensor_withNu(1,2) += py * pz;
        MomentumTensor_withNu(2,0) += pz * px;
        MomentumTensor_withNu(2,1) += pz * py;
        MomentumTensor_withNu(2,2) += pz * pz;
        
        p2_sum_withNu += (px * px + py * py + pz * pz);
    }
    
    //Normalize MomentumTensor
    if (p2_sum != 0.)
    {
        for (int i=0; i<3; i++) //px, py, pz
            for (int j=0; j<3; j++)//px, py, pz
            {
                MomentumTensor(i,j) = MomentumTensor(i,j) / p2_sum;
                MomentumTensor_withNu(i,j) = MomentumTensor_withNu(i,j) / p2_sum_withNu;
            }
    }
    
    TVectorD* ev = new TVectorD(3);
    TVectorD* ev_withNu = new TVectorD(4);
    MomentumTensor.EigenVectors(*ev); //the eigenvalues are automatically sorted
    MomentumTensor_withNu.EigenVectors(*ev_withNu);
    
    //some checks & limited precision of TVectorD
    double lambda1= fabs((*ev)[0]) < 0.000000000000001 ? 0 : (*ev)[0];
    double lambda2= fabs((*ev)[1]) < 0.000000000000001 ? 0 : (*ev)[1];
    double lambda3= fabs((*ev)[2]) < 0.000000000000001 ? 0 : (*ev)[2];
    
    double lambda1_withNu = fabs((*ev_withNu)[0]) < 0.000000000000001 ? 0 : (*ev_withNu)[0];
    double lambda2_withNu = fabs((*ev_withNu)[1]) < 0.000000000000001 ? 0 : (*ev_withNu)[1];
    double lambda3_withNu = fabs((*ev_withNu)[2]) < 0.000000000000001 ? 0 : (*ev_withNu)[2];
    
    //std::cout << "Eigenvalues: "<<std::endl;
    //std::cout << "1: "<<lambda1<<std::endl;
    //std::cout << "2: "<<lambda2<<std::endl;
    //std::cout << "3: "<<lambda3<<std::endl;
    
    float sphericity = 3./2. * (lambda2 + lambda3);
    float sphericity_withNu = 3./2. * (lambda2_withNu + lambda3_withNu);
    
    float aplanarity = 3./2. * lambda3;
    float C = 3.*(lambda3*lambda2 + lambda3*lambda1 + lambda2*lambda1);
    float D = 27.*(lambda1*lambda2*lambda3);
    
    //std::cout <<"sphericity: "<< sphericity <<std::endl;
    //std::cout <<"sphericity (with nu): "<< sphericity_withNu <<std::endl;
    branch_vars.vars_float["sphericity"] = sphericity;
    branch_vars.vars_float["sphericity_withNu"] = sphericity_withNu;
    branch_vars.vars_float["aplanarity"] = aplanarity;
    branch_vars.vars_float["C"] = C;
    branch_vars.vars_float["D"] = D;
    
    post_process();
    return true;
}
