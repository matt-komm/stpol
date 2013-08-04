testfiles = dict()
testfiles["step1"] = dict()
testfiles["step1"]["signal"] = "/store/user/joosep/TToLeptons_t-channel_8TeV-powheg-tauola/Jul8_51f69b/e6cee8f160cb239f414a74aa40d88ea9/output_noSkim_1_1_YzB.root"
testfiles["step2"] = dict()
testfiles["step2"]["signal"] = "/store/user/joosep/Aug1_5a0165/iso/nominal/T_t_ToLeptons/output_1_3_fvT.root"

if __name__=="__main__":
    from pprint import pprint
    pprint(testfiles)
