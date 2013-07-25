#!/usr/bin/env python
#SBATCH -J "MVA-traintest"
import argparse, subprocess

parser = argparse.ArgumentParser()
parser.add_argument('qs', type=float, nargs='*')
parser.add_argument('--bulk-batch', action='store_true')
parser.add_argument('-p', '--partition', type=str, default='main')
parser.add_argument('-b', action='store_true')
args = parser.parse_args()
print 'Arguments:', args

if args.bulk_batch:
	import numpy as np
	print 'Sending bulk'
	# Build the sbatch command:
	cmd  = ['sbatch']
	cmd += ['-p{0}'.format(args.partition)]
	cmd += ['batch.py']
	cmd += ['-b']

	qs = np.linspace(0.02, .98, 49)
	for q in qs:
		cmdstring = ' '.join(cmd + [str(q)])
		print 'Submitting:', cmdstring
		
		submitted = False
		while not submitted:
			submitted = (subprocess.call(cmd) == 0)
			submitted = True
			if not submitted:
				print 'Error submitting. Trying again...'
elif len(args.qs) > 0:
	import train
	Ns = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 20, 22, 23, 25, 28, 30, 33, 35, 38, 42, 45, 49, 53, 58, 63, 68, 74, 81, 87, 95, 103, 112, 121, 132, 143, 155, 168, 183, 198, 215, 233, 253, 275, 298, 323, 351, 380, 413, 448, 486, 527, 572, 620, 673, 730, 792, 859, 932, 1011, 1097, 1190, 1291, 1401, 1519, 1648, 1788, 1940, 2104, 2283, 2477, 2687, 2915, 3162]
	print 'Training with:', Ns, args.qs
	for q in args.qs:
		print ' > q =', q
		train.train(q, Ns)
else:
	print 'Bad arguments!'
