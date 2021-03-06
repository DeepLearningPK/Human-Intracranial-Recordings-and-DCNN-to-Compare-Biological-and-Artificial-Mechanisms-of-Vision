from abc import ABCMeta, abstractmethod, abstractproperty
import os
import numpy as np
import scipy.io as sio
from scipy.ndimage import imread
from scipy.spatial import distance as scipydist
import argparse


class RDM:
    __metaclass__ = ABCMeta

    #: Paths
    DATADIR = '../../Data'
    CODEDIR = '../../Code'
    OUTDIR = None

    #: The distance metric
    distance = None

    #: Flag whether to shuffle or not
    shuffle = None

    #: The featureset we are working on
    featureset = None

    #: Matrix where data samples are stored
    representation = abstractproperty()

    #: Resulting dissimilarity matrix
    dsm = abstractproperty()

    #: Reordering of the images from the order of DNN into ordering by categories
    reorder_dnn_to_categories = []

    #: Reordering of the images from the order of stimulation into ordering by categories
    reorder_stimulation_to_categories = []

    def __init__(self, distance, featureset, shuffle):
        self.distance = distance
        self.shuffle = shuffle
        self.featureset = featureset

        # list of stimuli used for human stimulation
        stimulation_stimuli = np.loadtxt('../Intracranial/stimsequence.txt', dtype='string')

        # create the reordering from stimulation order to order by category
        self.reorder_stimulation_to_categories = []
        for s in sorted(set(stimulation_stimuli)):
            for i in np.where(stimulation_stimuli == s)[0]:
                self.reorder_stimulation_to_categories.append(i)

        # list of stimuli used to extract DNN activations
        self.dnn_stimuli = np.loadtxt('%s/DNN/imagesdone.txt' % self.DATADIR, dtype={'names': ('stimulus', 'class'), 'formats': ('S10', 'i1')})
        self.dnn_stimuli = np.array([x[0].split('.')[0] for x in self.dnn_stimuli])

        # create the reordering from dnn order to order by category
        self.reorder_dnn_to_categories = []
        for s in sorted(stimulation_stimuli):
            for i in np.where(self.dnn_stimuli == s)[0]:
                self.reorder_dnn_to_categories.append(i)

        # create the directory to store results
        self.OUTDIR = '%s/RSA/%s.%s' % (self.DATADIR, self.featureset, self.distance)
        try:
            os.mkdir(self.OUTDIR)
            os.mkdir('%s/numbers' % self.OUTDIR)
        except:
            #print 'WARNING: directory %s already exists, make sure we are not overwriting something important there.' % self.OUTDIR
            pass
        

    @abstractmethod
    def compute_dsm(self):
        pass

    @abstractmethod
    def save_dsm(self):
        pass

    @abstractmethod
    def load_dsm(self):
        pass

    @abstractmethod
    def plot_dsm(self):
        pass

class RDMPixel(RDM):
    representation = None
    dsm = None

    def __init__(self, distance, featureset, shuffle, load_representation=True):
        RDM.__init__(self, distance, featureset, shuffle)
        self.representation = np.zeros((419, 51529))
        if load_representation:
            for i, fname in enumerate(self.dnn_stimuli):
                self.representation[i] = np.ravel(imread('%s/DNN/imagesdone/%s.jpg' % (self.DATADIR, fname)))
            self.representation = self.representation[self.reorder_dnn_to_categories]

            if self.shuffle:
                new_order = np.random.permutation(range(self.representation.shape[0]))
                self.representation = self.representation[new_order]

    def compute_dsm(self):
        self.dsm = scipydist.squareform(scipydist.pdist(self.representation, self.distance))

    def save_dsm(self):
        np.savetxt('%s/numbers/dnn-pixels.txt' % self.OUTDIR, self.dsm, fmt='%.6f')

    def load_dsm(self):
        self.dsm = np.loadtxt('%s/numbers/dnn-pixels.txt' % self.OUTDIR)

    def plot_dsm(self):
        #plt.figure();
        #plt.imshow(self.dsm);
        #plt.colorbar();
        #plt.savefig('%s/RSA/%s/plots/dnn-pixels.png' % (self.DATADIR, self.distance));
        #plt.clf();
        pass


class RDMDNN(RDM):
    representation = None
    dsm = {}
    layers = None
    network = None

    def __init__(self, distance, network, featureset, shuffle, load_representation=True):
        RDM.__init__(self, distance, featureset, shuffle)
        self.network = network

        self.layers = sorted(os.listdir('%s/DNN/activations/%s' % (self.CODEDIR, network)))
        self.representation = {}
        if load_representation:
            for layer in self.layers:
                self.representation[layer] = np.load('%s/DNN/activations/%s/%s/activations.npy' % (self.CODEDIR, network, layer))
                self.representation[layer] = self.representation[layer][self.reorder_dnn_to_categories]

                if self.shuffle:
                    new_order = np.random.permutation(range(self.representation[layer].shape[0]))
                    self.representation[layer] = self.representation[layer][new_order]

    def compute_dsm(self):
        for layer in self.layers:
            print 'Computing the matrix for layer %s...' % layer
            self.dsm[layer] = scipydist.squareform(scipydist.pdist(self.representation[layer], self.distance))

    def save_dsm(self):
        for layer in self.layers:
            np.savetxt('%s/numbers/dnn-%s-%s.txt' % (self.OUTDIR, layer, self.network), self.dsm[layer], fmt='%.6f')

    def load_dsm(self):
        for layer in self.layers:
            self.dsm[layer] = np.loadtxt('%s/numbers/dnn-%s-%s.txt' % (self.OUTDIR, layer, self.network))

    def plot_dsm(self):
        for layer in self.layers:
            #plt.figure();
            #plt.imshow(self.dsm);
            #plt.colorbar();
            #plt.savefig('%s/RSA/%s/plots/dnn-%s.png' % (self.DATADIR, dist, layer));
            #plt.clf();
            pass


class RDMBrain(RDM):
    representation = None
    dsm = None
    subject = {}
    suffix = ''

    def __init__(self, distance, featureset, sid, shuffle):
        print 'WARNING: For brain response distances we use Euclidean distance because brain responses are scalars'
        RDM.__init__(self, distance, featureset, shuffle)
        subjects = sorted(os.listdir('%s/Intracranial/Processed/%s/' % (self.DATADIR, featureset)))
        sfile = subjects[sid]
        s = sio.loadmat('%s/Intracranial/Processed/%s/%s' % (self.DATADIR, featureset, sfile))
        self.subject['data'] = s['s']['data'][0][0]
        self.subject['name'] = s['s']['name'][0][0][0]
        print self.subject['name']
        self.representation = self.subject['data'][self.reorder_stimulation_to_categories]

        # disable the poison pill
        self.representation[self.representation == -123456] = 0.0

        if self.shuffle:
            new_order = np.random.permutation(range(self.representation.shape[0]))
            self.representation = self.representation[new_order]

    def compute_and_save_batch_dsm(self):
        print 'Processing %s' % self.subject['name']
        nstim = self.representation.shape[0]
        nprobes = self.representation.shape[1]

        if nprobes == 0:
            sm = np.zeros((nstim, nstim))
            np.savetxt('%s%s/numbers/brain-%s-%d.txt' % (self.OUTDIR, self.suffix, self.subject['name'], 0), sm, fmt='%.3f')
            return None

        for p in range(nprobes):
            #sm = scipydist.squareform(scipydist.pdist(self.representation[:, p].reshape((nstim, 1)), self.distance))
            sm = scipydist.squareform(scipydist.pdist(self.representation[:, p].reshape((nstim, 1)), 'euclidean'))
            np.savetxt('%s%s/numbers/brain-%s-%d.txt' % (self.OUTDIR, self.suffix, self.subject['name'], p), sm, fmt='%.3f')

    def compute_dsm(self, pid):
        if self.shuffle:
            new_order = np.random.permutation(range(self.representation.shape[0]))
            self.representation = self.representation[new_order]
        nstim = self.representation.shape[0]
        #return scipydist.squareform(scipydist.pdist(self.representation[:, pid].reshape((nstim, 1)), self.distance))
        return scipydist.squareform(scipydist.pdist(self.representation[:, pid].reshape((nstim, 1)), 'euclidean'))

    def save_dsm(self):
        raise Exception("save_dsm() is not in use for Brain RDM, use compute_and_save_batch_dsm() instead")

    def load_dsm(self):
        raise Exception("load_dsm() is not in use for Brain RDM")

    def return_dsm(self, pid):
        if self.shuffle:
            raise Exception("return_dsm() for Brain RDM cannot be used in shuffle=True mode, use compute_dsm() instead")
        else:
            return np.loadtxt('%s/RSA/%s.%s%s/numbers/brain-%s-%d.txt' % (self.DATADIR, self.featureset, self.distance,
                                                                         self.suffix, self.subject['name'], pid))

    def plot_dsm(self):
        raise Exception("plot_dsm() is not in use for Brain RDM")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Compute RDM matrices')
    parser.add_argument('-t', '--type', dest='datatype', type=str, required=True, help='The data source: pixels, dnn or brain')
    parser.add_argument('-d', '--distance', dest='distance', type=str, required=True, help='The distance metric to use')
    parser.add_argument('-n', '--network', dest='network', type=str, required=False, help='DNN activations for DNN RDMs')
    parser.add_argument('-i', '--sid', dest='sid', type=int, required=False, help='Subject ID for Brain RDM')
    parser.add_argument('-f', '--featureset', dest='featureset', type=str, required=True, help='Directory with brain features (Processed/?)')
    parser.add_argument('-s', '--shuffle', dest='shuffle', type=str, required=False, default=False, help='Whether to shuffle data for a permutation test')
    args = parser.parse_args()
    datatype = str(args.datatype)
    distance = str(args.distance)
    network = str(args.network)
    sid = int(args.sid) if args.sid is not None else None
    featureset = str(args.featureset)
    shuffle = bool(args.shuffle == 'True')

    if datatype == 'pixels':
        rdm = RDMPixel(distance, featureset, shuffle)
        rdm.compute_dsm()
        rdm.save_dsm()

    elif datatype == 'dnn':
        if network == 'None':
            raise Exception("Activation (-a) is a required argument for DNN RDM")
        rdm = RDMDNN(distance, network, featureset, shuffle)
        rdm.compute_dsm()
        rdm.save_dsm()

    elif datatype == 'brain':
        if sid is None:
            raise Exception("Subject ID (-i) is a required argument for Brain RDM")
        rdm = RDMBrain(distance, featureset, sid, shuffle)
        rdm.compute_and_save_batch_dsm()

    else:
        print 'ERROR: Unknown data source %s' % source

