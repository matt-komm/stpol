from plots.common.cuts import Cuts, Weights, Cut, Var
"""
A list of hierarchical cuts
"""
cuts = [
    ("CHANNEL", [
        ("mu", Cuts.lepton("mu")),
        ("ele", Cuts.lepton("ele"))
    ]),
    ("NJETS", [
        ("none", Cuts.no_cut),
        ("2J", Cuts.n_jets(2)),
        ("3J", Cuts.n_jets(3))
    ]),
    ("NTAGS", [
        ("none", Cuts.no_cut),
        ("0T", Cuts.n_tags(0)),
        ("1T", Cuts.n_tags(1)),
        ("2T", Cuts.n_tags(2))
    ]),
    ("MET", [
        # ("met", [
        #     ("none", Cuts.no_cut),
        #     ("30", Cut("met>30")),
        #     ("40", Cut("met>40"))
        # ]),
        ("mtw", [
            ("nominal", Cuts.mt_mu()),
            ("up", Cuts.mt_mu("up")),
            ("down", Cuts.mt_mu("down")),
        ])
    ]),
    ]

weights = [
    ("PU", [
        ("nominal", Weights.pu()),
        ("up", Weights.pu("up")),
        ("down", Weights.pu("down")),
        ("none", Weights.no_weight),
    ]),
    ("BTAG", [
            ("nominal", Weights.b_weight()),
            ("BC", [
                ("up", Weights.b_weight("BC", "up")),
                ("down", Weights.b_weight("BC", "down"))
            ]),
            ("L", [
                ("up", Weights.b_weight("L", "up")),
                ("down", Weights.b_weight("L", "down"))
            ]),
            ("none", Weights.no_weight),
    ]),
    ("WJETS.yield", [
        ("nominal", Weights.wjets_madgraph_flat_weight("nominal")),
        ("up", Weights.wjets_madgraph_flat_weight("wjets_up")),
        ("down", Weights.wjets_madgraph_flat_weight("wjets_down")),
        ("none", Weights.no_weight),
    ]),
    ("WJETS.shape", [
        ("nominal", Weights.wjets_madgraph_shape_weight("nominal")),
        ("up", Weights.wjets_madgraph_shape_weight("wjets_up")),
        ("down", Weights.wjets_madgraph_shape_weight("wjets_down")),
        ("none", Weights.no_weight),
    ]),
]


variables = [
        ("VARS", [
            ("cos_theta", [
                ("fixed1", Var("cos_theta", (20, -1, 1))),
                ("v1", Var("cos_theta", [0.2, 0.5, 0.6, 0.9, 1.0]))
            ]),
            ("eta_lj", [
                ("full", Var("eta_lj", (20, -5, 5))),
                ("abs", Var("abs(eta_lj)", (20, 0, 5))),
            ])
        ])
    ]   
