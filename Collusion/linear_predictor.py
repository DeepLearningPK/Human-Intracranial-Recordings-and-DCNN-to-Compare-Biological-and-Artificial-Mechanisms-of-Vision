import os
import time
import numpy as np
import scipy.io as sio
from sklearn import linear_model
from sklearn import cross_validation
from sklearn.decomposition import PCA
from scipy.stats import spearmanr
from scipy.ndimage import imread
import multiprocessing
from joblib import Parallel, delayed
import argparse


# read in command line arguments
parser = argparse.ArgumentParser(description='Train all linear models for a given subject.')
parser.add_argument('-i', '--sid', dest='sid', type=int, required=True, help='Subject ID')
parser.add_argument('-a', '--activations', dest='np_activation_data', type=str, required=True, help='Directory with DNN activations (DNN/activations/?)')
parser.add_argument('-f', '--featureset', dest='featureset', type=str, required=True, help='Directory with brain features (Processed/?)')
args = parser.parse_args()
sid = int(args.sid)
np_activation_data = str(args.np_activation_data)
featureset = str(args.featureset)

# parameters
print 'Mapping subject %d represented with "%s" to %s DNN activations' % (sid, featureset, np_activation_data)
ncores = 6

def scan_alpha(alphas, n_iter, layer_activity_all, probe_responses_all, n_cv):
    max_r2 = -1.0
    best_alpha = 1.0
    for a in alphas:
        clf = linear_model.Ridge(alpha=a, max_iter=n_iter)
        r2 = np.mean(cross_validation.cross_val_score(clf, layer_activity_all, probe_responses_all, cv=n_cv))
        if r2 >= max_r2:
            best_alpha = a
            max_r2 = r2
    return best_alpha

# train linear model to predict probe [pid] response from [layer]
# activations, measure the prediction performace on the test set
# of stimuli
def predict_from_layer(subject_name, layer, pid, layer_activity_all, probe_responses_all):

    # to do artifact rejection we have dropped some number of images from each of the probes
    # now each proble has varying number of "trials" (images), to keep the data in matrix
    # format we inroduce a "poison pill" value of -123456 -- the images with this values as
    # a response should be excluded from further analysis
    keep_stim = probe_responses_all != -123456
    layer_activity_all = layer_activity_all[keep_stim]
    probe_responses_all = probe_responses_all[keep_stim]

    # parameters
    n_runs = 7
    n_cv = 10
    n_iter = 50

    # uncomment for the permutation test
    #probe_responses_all = np.random.permutation(probe_responses_all)

    # PCA
    try:
        pca = PCA(n_components=200)
        layer_activity_all += np.random.rand(layer_activity_all.shape[0], layer_activity_all.shape[1]) * 1e-6
        layer_activity_all = pca.fit_transform(layer_activity_all)
    except:
        print 'ERROR: PCA did not converge. Skipping the probe'
        return (layer, pid, np.zeros(n_runs))

    # parameter search
    # http://scikit-learn.org/stable/auto_examples/linear_model/plot_lasso_model_selection.html
    alphas = np.array([0.0, 0.0001, 0.001, 0.01, 0.1, 1.0, 10.0, 10.0**2, 10.0**3, 10.0**4, 10.0**5, 10.0**6, 10.0**7, 10.0**8, 10.0**9, 10.0**10, 10.0**11, 10.0**12, 10.0**13, 10.0**14, 10.0**15])
    best_alpha = scan_alpha(alphas, n_iter, layer_activity_all, probe_responses_all, n_cv)

    # more granular search for alpha
    best_alpha_id = np.where(alphas == best_alpha)[0][0]
    from_id = 0 if best_alpha_id == 0 else best_alpha_id - 1
    till_id = len(alphas)-1 if best_alpha_id == len(alphas)-1 else best_alpha_id + 1 
    f = alphas[from_id]
    t = alphas[till_id]
    s = (t - f) / 50.0
    alphas = np.arange(f, t, s)
    best_alpha = scan_alpha(alphas, n_iter, layer_activity_all, probe_responses_all, n_cv)
    
    # repeat predictability estimation [n_runs] times
    r_scores = np.zeros(n_runs)
    for run in range(n_runs):

        # reshuffle the dataset to force another instance of cross-validation
        shuffle_idx = np.random.choice(range(layer_activity_all.shape[0]), size=layer_activity_all.shape[0], replace=False)
        layer_activity_all = layer_activity_all[shuffle_idx]
        probe_responses_all = probe_responses_all[shuffle_idx]

        # predict piecewise all of the data using CV
        clf = linear_model.Ridge(alpha=best_alpha, max_iter=n_iter)
        predicted = cross_validation.cross_val_predict(clf, layer_activity_all, probe_responses_all, cv=n_cv) 

        # store the correlation coefficient
        r, pval = spearmanr(probe_responses_all, predicted)

        # drop not significant results
        if pval > 0.0001 or r < 0.0:
            r = 0.0
        r_scores[run] = r
    
    print 'Fitting  %s: %s to probe %d -- %s' % (subject_name, layer, pid, r_scores)
    return (layer, pid, r_scores)


# prepare lists of probe coordinates for each layer
print 'Loading list of layers...'
layers = sorted(os.listdir('../../Repository/DNN/activations/%s' % np_activation_data))
layers = ['pixels'] + layers

assignments = {}
for layer in layers:
    assignments[layer] = []

# load DNN activations
print 'Loading DNN activations...'
activations = {}
for layer in layers:
    if layer == 'pixels':
        activations[layer] = np.zeros((419, 51529))
        for i, fname in enumerate(sorted(os.listdir('../../Data/DNN/imagesdone/'))):
            activations[layer][i] = np.ravel(imread('../../Data/DNN/imagesdone/%s' % fname))
    else:
        activations[layer] = np.load('../../Repository/DNN/activations/%s/%s/activations.npy' % (np_activation_data, layer))

# load list of stimuli in the order they were presented to DNN
print 'Loading DNN stimuli...'
dnn_stimuli = np.loadtxt('../../Data/DNN/imagesdone.txt', dtype={'names': ('stimulus', 'class'), 'formats': ('S10', 'i1')})
dnn_stimuli = [x[0].split('.')[0] for x in dnn_stimuli]

# read list of subjects
listing = sorted(os.listdir('../../Data/Intracranial/Processed/%s/' % featureset))

# load brain data
sfile = listing[sid]
print 'Loading %s...' % sfile

# load the matlab structure 
s = sio.loadmat('../../Data/Intracranial/Processed/%s/%s' % (featureset, sfile))
subject = {}
subject['stimseq'] = [x[0][0] for x in s['s']['stimseq'][0][0]]
subject['stimgroups'] = [x[0] for x in s['s']['stimgroups'][0][0]]
subject['probes'] = {}
subject['probes']['rod_names'] = list(s['s']['probes'][0][0][0][0][0])
subject['probes']['probe_ids'] = [x[0] for x in list(s['s']['probes'][0][0][0][0][1])]
subject['probes']['mni'] = s['s']['probes'][0][0][0][0][2]
subject['data'] = s['s']['data'][0][0]
subject['name'] = s['s']['name'][0][0][0]

# for convenience
nstims = subject['data'].shape[0]
nprobes = subject['data'].shape[1]

# create the dataset: for each layer we'll have DNN activations as features
# and probe response as the target value to predict
layer_activity = {}
for layer in layers:
    layer_activity[layer] = np.zeros((nstims, activations[layer].shape[1]))
    probe_responses = np.zeros((nstims, nprobes))
    for sid_brain, stimulus in enumerate(subject['stimseq']):
        sid_dnn = dnn_stimuli.index(stimulus)
        layer_activity[layer][sid_brain, :] = activations[layer][sid_dnn, :]
        probe_responses = subject['data']

# grid of (subject, layer, pribe) triples to compute in parallel
parallel_grid = []
for layer in layers:
    for pid in range(len(subject['probes']['probe_ids'])):
        parallel_grid.append((layer, pid))

# for each (layer, probe) combination train a linear model to predict the probe response from the layer activations
start = time.time()
results = Parallel(n_jobs=ncores, backend="threading")(delayed(predict_from_layer)(subject['name'], layer, pid,
                                                               layer_activity[layer], probe_responses[:, pid])
                                                       for (layer, pid) in parallel_grid)

# aggregate results and store to files
print 'Storing mapping for %s...' % subject['name']

output = np.zeros((nprobes, len(layers)))
for record in results:
    layerid = layers.index(record[0])
    pid = record[1]
    output[pid, layerid] = np.mean(record[2])

# store probe to layer mapping for the subject
np.savetxt('../../Data/Intracranial/Probe_to_Layer_Maps/lp_%s/%s.txt' % (featureset, subject['name']), output, fmt='%.4f')
