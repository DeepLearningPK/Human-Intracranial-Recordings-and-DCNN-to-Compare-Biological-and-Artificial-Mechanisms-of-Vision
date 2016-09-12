import os
import glob
import numpy as np
import argparse
from scipy.stats import spearmanr, pearsonr
from sklearn.preprocessing import MinMaxScaler

# read in command line arguments
parser = argparse.ArgumentParser(description='Compute RSA matrices for each electrode')
parser.add_argument('-f', '--featureset', dest='featureset', type=str, required=True, help='Directory with brain features (Processed/?)')
parser.add_argument('-d', '--distance', dest='dist', type=str, required=True, help='The distance metric to use')
parser.add_argument('-s', '--shuffle', dest='shuffle', type=bool, required=False, default=False, help='Whether to shuffle data for a permutation test')
args = parser.parse_args()
featureset = str(args.featureset)
dist = str(args.dist)
shuffle = bool(args.shuffle)

suffix = ''
if shuffle:
    suffix = '.shuffled'

# load layer similarity matrices including the "layer 0" (pixel space)
layers = ['pixels', 'conv1', 'conv2', 'conv3', 'conv4', 'conv5', 'fc6', 'fc7', 'fc8']
dnn_dsm = {}
for layer in layers:
    dnn_dsm[layer] = np.loadtxt('../../Data/RSA/%s%s/numbers/dnn-%s.txt' % (dist, suffix, layer))

# load area response dissimilarity matrices
area_dsm = {}
listing = glob.glob('../../Data/RSA/%s%s/numbers/area-*.txt' % (dist, suffix))
nareas = len(listing)
for aid, filename in enumerate(listing):
    area_dsm[aid] = np.loadtxt(filename)

# compute correlation between every layer-brain pair of RSA matrices
mms = MinMaxScaler()
nstim = area_dsm[0].shape[0]
maps = np.empty((nareas, len(layers)))
for lid, layer in enumerate(layers):
    for aid in range(nareas):
        dnn = mms.fit_transform(dnn_dsm[layer])
        area = mms.fit_transform(area_dsm[aid])
        score = 0
        for i in range(nstim):
            # here we can decide what do we use as a score between the two matrices
            # a) number of images that were significantly correlated in both matrices
            #r, p = spearmanr(dnn[i, :], area[i, :])
            #if p < 0.00001:
            #    score += 1

            # b) sum of r scores of all significanly correlated images
            r, p = spearmanr(dnn[i, :], area[i, :])
            if p < 0.01:
                score += r
        
        maps[aid, lid] = score / float(nstim)

# replace NaN's with 0
maps[np.isnan(maps)] = 0.0

# store the scores
np.savetxt('../../Data/Intracranial/Probe_to_Layer_Maps/rsa_%s%s_%s/all.txt' % (dist, suffix, featureset), maps, fmt='%.4f')

