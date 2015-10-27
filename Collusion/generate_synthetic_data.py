"""

Sanity-check synthetic data generator
-------------------------------------

Each probe has one feature which is taken as linear combination of DNN layer
activations plus some noise. One probe has fixed set of weights across all stimuli.
This set of weights is what a linear model should capture.

The layer which should be mapped to the probe will have its activity multiplied by 
the same set of weights for each of the stimuli. Other layers' activity will be
multiplied by a random set of weights generater anew for each of the stimuli.

The way to check if linear models did indeed capture the weights we have generated
we will need to check probe-to-layer assignment files generated by the
`map_layers_to_probes.py` script. For every subject it should look like
000000111111222223333333....777777 with minor mistakes.

"""

import os
import numpy as np
import scipy.io as sio
from sklearn.preprocessing import scale

print 'Loading list of layers...'
layers = os.listdir('../../Data/DNN/Activations/numpy')

# load list of stimuli in the order they were presented to DNN
print 'Loading DNN stimuli...'
dnn_stimuli = np.loadtxt('../../Data/DNN/imagesdone.txt', dtype={'names': ('stimulus', 'class'), 'formats': ('S10', 'i1')})
dnn_stimuli = [x[0].split('.')[0] for x in dnn_stimuli]

# load subject data
s = sio.loadmat('../../Data/Intracranial/Processed/maxamp/AL_25FEV13N.mat')
subject = {}
subject['stimseq'] = [x[0][0] for x in s['s']['stimseq'][0][0]]
subject['stimgroups'] = [x[0] for x in s['s']['stimgroups'][0][0]]
subject['probes'] = {}
subject['probes']['rod_names'] = list(s['s']['probes'][0][0][0][0][0])
subject['probes']['probe_ids'] = [x[0] for x in list(s['s']['probes'][0][0][0][0][1])]
subject['probes']['mni'] = s['s']['probes'][0][0][0][0][2]
subject['data'] = s['s']['data'][0][0]
subject['name'] = s['s']['name'][0][0][0]

# keep activations only for the relevant stimuli
keep_dnn_stimuli = []
for stimulus in subject['stimseq']:
    sid_dnn = dnn_stimuli.index(stimulus)
    keep_dnn_stimuli.append(sid_dnn)

print 'Loading DNN activations...'
activations = {}
for layer in layers:
    activations[layer] = np.load('../../Data/DNN/Activations/numpy/%s/activations.npy' % layer)
    activations[layer] = np.matrix(activations[layer][keep_dnn_stimuli, :])

nprobes = s['s']['data'][0][0].shape[1]
nprobes_per_layer = nprobes / 7



for lid, pstart in enumerate(range(0, nprobes, nprobes_per_layer)):

    # decide the probe range to be assigned to the layer `lid`
    pend = nprobes if lid == 7 else pstart + nprobes_per_layer
    nprobes_in_this_layer = len(range(pstart, pend))

    # generate the set of weights to multiply layer activations
    # to get the responses of the probes in range (pstart, pend)
    d = activations[layers[lid]].shape[1]
    weights = np.matrix(np.random.uniform(5.0, 10.0, d)).T
    drop_idx = np.random.choice(range(1, d), d - 30, replace=False)
    weights[drop_idx] = np.matrix(np.random.uniform(-0.5, 0.5, len(drop_idx))).T

    # generate each probe's activity, for the probes within the 
    # [pstart, pend) range the activity will be calculated as
    # the mulitpication of the layer activation by the weights
    one_probe_activity = scale(activations[layers[lid]] * weights)
    all_probe_activity = np.tile(one_probe_activity, nprobes_in_this_layer)
    noise = np.random.uniform(-0.5, 0.5, (319, nprobes_in_this_layer))
    s['s']['data'][0][0][:, pstart:pend] = all_probe_activity + noise

sio.savemat('../../Data/Intracranial/Processed/synthetic/AL_25FEV13N.mat', s)
