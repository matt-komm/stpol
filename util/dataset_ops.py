from datasets import possible_ds
import argparse

parser = argparse.ArgumentParser(
    description="Prints out dataset information"
)
parser.add_argument("-d", "--dataset", type=str, required=True,
                    help="The dataset group to print out"
)
args = parser.parse_args()

for d in possible_ds[args.dataset]:
    print str(d)

