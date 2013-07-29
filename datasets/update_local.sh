#!/bin/bash
python ~/util/das_cli.py --query="dataset site=T2_EE_Estonia" --limit=0 > $STPOL_DIR/datasets/local_datasets.txt
