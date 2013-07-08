Use the script datasets2.py in this directory to create the crab.cfg files for the stpol analysis.

The structure of the datasets/ directory is as follows

The various processing steps (step1, step2) are organized as
>datasets/stepN

Each step contains subdirectories for data and MC
>datasets/stepN/{data,mc}

The subdirectories contain files, the name of which reflects where the data belongs logically. The files must have lines that are the following
>NAME_OF_DS /PATH/TO/DATASET/IN/DAS

and optionally they may contain comments starting with a "#".

The configuration for the datasets is done in datasets2.py, using the methods therein.
