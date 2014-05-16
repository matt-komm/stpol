
const nb_reco = 48

const binnings = {
    :cos_theta_lj => {
        :gen => infb(linspace(-1, 1, int(nb_reco/2) + 1)),
        :reco => infb(linspace(-1, 1, int(nb_reco) + 1)),
    },
    :bdt => infb(linspace(-1, 1, 30)),
}

#functions to make default histograms
#these are called when a necessary histogram was not found in the database
const defaults_func = {

    :ljet_pt => () -> Histogram(infb(linspace(40, 300, 30))),
    :bjet_pt => () -> Histogram(infb(linspace(40, 300, 30))),

    :cos_theta_lj => () -> Histogram(binnings[:cos_theta_lj][:reco]),
    :cos_theta_bl => () -> Histogram(binnings[:cos_theta_lj][:reco]),
    :cos_theta_lj_gen => () -> Histogram(binnings[:cos_theta_lj][:gen]),
    :cos_theta_bl_gen => () -> Histogram(binnings[:cos_theta_lj][:gen]),
    :bdt_sig_bg => () -> Histogram(binnings[:bdt]),
    :bdt_sig_bg_top_13_001 => () -> Histogram(infb(linspace(-1, 1, 21))),
    :bdt_qcd => () -> Histogram(infb(linspace(-1, 1.0, 30))),

    :C => () -> Histogram(infb(linspace(0, 1, 30))),
    :C_21 => () -> Histogram(infb(linspace(0, 1, 21))),
    :C_signalregion => () -> Histogram(infb(linspace(0, 0.3, 30))),

    :shat => () -> Histogram(infb(linspace(150, 1200, 30))),
    :ht => () -> Histogram(infb(linspace(80, 400, 30))),

    :met_phi => () -> Histogram(infb(linspace(-3.2, 3.2, 30))),

    :transfer_matrix => () -> NHistogram({
        binnings[:cos_theta_lj][:gen],
        binnings[:cos_theta_lj][:reco]
    }),
    :abs_ljet_eta => () -> Histogram(infb(linspace(0, 5, 30))),
    :abs_ljet_eta_16 => () -> Histogram(infb(linspace(0, 4.5, 16))),
    :abs_bjet_eta => () -> Histogram(infb(linspace(0, 5, 30))),

    :ljet_eta => () -> Histogram(infb(linspace(-5, 5, 30))),
    :bjet_eta => () -> Histogram(infb(linspace(-5, 5, 30))),

    :lepton_iso => () -> Histogram(infb(linspace(0, 0.3, 60))),

    :lepton_eta => () -> Histogram(infb(linspace(-3, 3, 60))),

    :ljet_dr => () -> Histogram(infb(linspace(0, 2, 30))),
    :bjet_dr => () -> Histogram(infb(linspace(0, 2, 30))),

    :mtw => () -> Histogram(infb(linspace(0, 200, 30))),

    :lepton_pt => () -> Histogram(infb(linspace(25, 200, 30))),
    :lepton_eta => () -> Histogram(infb(linspace(-5, 5, 30))),
    :abs_lepton_eta => () -> Histogram(infb(linspace(0, 5, 30))),

    :bjet_pt => () -> Histogram(infb(linspace(40, 300, 30))),
    :bjet_mass => () -> Histogram(infb(linspace(40, 150, 30))),
    :ljet_mass => () -> Histogram(infb(linspace(40, 150, 30))),

    :top_mass => () -> Histogram(infb(linspace(70, 400, 30))),
    :top_mass_signalregion => () -> Histogram(infb(linspace(120, 230, 30))),

    :top_pt => () -> Histogram(infb(linspace(0, 400, 30))),
    :n_good_vertices => () -> Histogram(infb(linspace(0, 50, 51))),
    :met => () -> Histogram(infb(linspace(0, 200, 30))),

    :nu_soltype => () -> Histogram(infb([-1, 0, 1])),
    :njets => () -> Histogram(infb([-1, 0, 1, 2, 3, 4, 5, 6])),
    :ntags => () -> Histogram(infb([-1, 0, 1, 2, 3, 4, 5, 6])),

    :lepton_charge => () -> Histogram(infb([-2, 0, 2])),

}

#default histograms
const defaults = Dict{Symbol, Any}()
for (k, v) in defaults_func
    defaults[k] = v()
end

include("histkey.jl")
