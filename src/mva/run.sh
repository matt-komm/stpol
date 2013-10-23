#!/bin/bash

~/parallel -j20 python adder.py {.}_mva1.csv $STPOL_DIR/mvatools/weights/stop_mu_BDT.weights.xml {} < input.txt
~/parallel -j20 python adder.py {.}_mva2.csv $STPOL_DIR/mvatools/weights/stop_ele_BDT.weights.xml {} < input.txt
