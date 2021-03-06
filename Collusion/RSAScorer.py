import os
import glob
import numpy as np
import argparse
from scipy.stats import spearmanr, pearsonr
from sklearn.preprocessing import MinMaxScaler


class RSAScorer:

    #: Paths
    DATADIR = '../../Data'
    OUTDIR = None

    #: Paramters to compute on: dataeset, method, significance levels
    featureset = None
    scope = None
    threshold = None

    #: List of subjects
    subjects = None

    #: Current subject
    sid = None
    sname = None

    #: List of layers
    layers = ['pixels', 'conv1', 'conv2', 'conv3', 'conv4', 'conv5', 'fc6', 'fc7', 'fc8']

    #: The distance measure that was used to compute RDMs
    distance = None

    #: Addition featureset suffix, marks if the RDM were computed on original or shuffled data
    suffix = ''

    #: RDMs on DNN layers
    dnn_dsm = {}

    #: RDMs on probe responses
    brain_dsm = {}

    #: Final results
    scores = None

    def __init__(self, featureset, distance, sid, scope, threshold, network):
        self.featureset = featureset
        self.distance = distance
        self.sid = sid
        self.scope = scope
        self.threshold = threshold
        self.network = network

        # read list of subjects
        self.subjects = sorted(os.listdir('%s/Intracranial/Processed/%s/' % (self.DATADIR, featureset)))
        self.sname = self.subjects[self.sid].split('.')[0]

        #if shuffle:
            #suffix = '.shuffled'

        # load layer RDMs including the "layer 0" (pixel space)
        for layer in self.layers:
            if layer == 'pixels':
                self.dnn_dsm[layer] = np.loadtxt('../../Data/RSA/%s.%s%s/numbers/dnn-%s.txt' % (self.featureset, self.distance, self.suffix, layer))
            else:
                self.dnn_dsm[layer] = np.loadtxt('../../Data/RSA/%s.%s%s/numbers/dnn-%s-%s.txt' % (self.featureset, self.distance, self.suffix, layer, self.network))

        # load brain response dissimilarity matrices
        listing = sorted(glob.glob('%s/RSA/%s.%s%s/numbers/brain-%s-*.txt' % (self.DATADIR, self.featureset, self.distance, self.suffix, self.sname)))
        for pid in range(len(listing)):
            filename = '%s/RSA/%s.%s%s/numbers/brain-%s-%d.txt' % (self.DATADIR, self.featureset, self.distance, self.suffix, self.sname, pid)
            self.brain_dsm[pid] = np.loadtxt(filename)

        # create a directory
        self.OUTDIR = '%s/Intracranial/Probe_to_Layer_Maps/rsa_%s.%s%s.%s.%s%s' % (self.DATADIR, self.featureset, self.distance, self.suffix, self.network, self.scope, ('%.10f' % self.threshold)[2:].rstrip('0'))
        try:
            os.mkdir(self.OUTDIR)
        except:
            #print 'WARNING: directory %s already exists, make sure we are not overwriting something important there.' % self.OUTDIR
            pass

    @staticmethod
    def compute_one_correlation_score(dnn, brain, scope, threshold):
        '''
        @param scope:     either 'matrix' or 'image' to indicate whethet correlation is computed
                          between whole matrices or image-by-image and then averaged
        @param threshold: signicance threshold a correlation must have to be stored as a result
                          use None to store all of the scores for the permutation test
        '''

        # scale the data
        mms = MinMaxScaler()
        dnn = mms.fit_transform(dnn)
        brain = mms.fit_transform(brain)

        # whole-matrix score
        if scope == 'matrix':
            r, p = spearmanr(np.ravel(dnn), np.ravel(brain))
            if threshold < 1.0:
                if r > 0.0 and p <= threshold:
                    return r
                else:
                    return 0.0
            else:
                return r 

        # per-image score
        if scope == 'image':
            nrows = brain.shape[0]
            score = 0
            for i in range(nrows):
                r, p = spearmanr(dnn[i, :], brain[i, :])
                if threshold < 1.0:
                    if r > 0.0 and p <= threshold:
                        score += r
                else:
                    score += r
            return score / float(nrows)

    def compute_all_correlation_scores(self):
        nprobes = len(self.brain_dsm)
        self.scores = np.zeros((nprobes, len(self.layers)))
        for lid, layer in enumerate(self.layers):
            for pid in range(nprobes):
                self.scores[pid, lid] = RSAScorer.compute_one_correlation_score(self.dnn_dsm[layer], self.brain_dsm[pid],
                                                                                self.scope, self.threshold)

        self.scores[np.isnan(self.scores)] = 0.0

        return self.scores

    def store_all_correlation_scores(self):
        np.savetxt('%s/%s.txt' % (self.OUTDIR, self.sname), self.scores, fmt='%.4f')

    def load_all_correlation_scores(self):
        self.scores = np.loadtxt('%s/%s.txt' % (self.OUTDIR, self.sname))


if __name__ == '__main__':

    # read in command line arguments
    parser = argparse.ArgumentParser(description='Compute correlation scores between RDM matrices for each probe-layer pair')
    parser.add_argument('-i', '--sid', dest='sid', type=int, required=True, help='Subject ID')
    parser.add_argument('-f', '--featureset', dest='featureset', type=str, required=True, help='Directory with brain features (Processed/?)')
    parser.add_argument('-d', '--distance', dest='distance', type=str, required=True, help='The distance metric to use')
    parser.add_argument('-o', '--onwhat', dest='onwhat', type=str, required=True, help='image or matrix depending on which you to compute the correlation on')
    #parser.add_argument('-s', '--shuffle', dest='shuffle', type=bool, required=False, default=False, help='Whether to shuffle data for a permutation test')
    parser.add_argument('-t', '--threshold', dest='threshold', type=float, required=True, help='Significance level a score must have to be counter (1.0 to store all)')
    parser.add_argument('-n', '--network', dest='network', type=str, required=True, help='RDM of activiation of which NN are to be used to compute the scores')
    args = parser.parse_args()
    sid = int(args.sid)
    featureset = str(args.featureset)
    distance = str(args.distance)
    #shuffle = bool(args.shuffle)
    onwhat = str(args.onwhat)
    threshold = float(args.threshold)
    network = str(args.network)

    rsascorer = RSAScorer(featureset, distance, sid, onwhat, threshold, network)
    rsascorer.compute_all_correlation_scores()
    rsascorer.store_all_correlation_scores()

