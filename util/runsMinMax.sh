#!/bin/bash

python ~/util/das_cli.py --query="run dataset=$1" --limit=0 > runs
cat runs | head -n1
cat runs | tail -n1
