from brian2.only import NeuronGroup
from brian2.only import Synapses
from brian2.units import *
from .ibm_base import *

def create_decorrelator(tau, input_group, input_idx):
	# Decorrelator neuron parameters
	Vr = 0 * volt
	epsilon = 1
	lmda = 0 * volt
	alpha = 1 * volt
	beta = 0 * volt
	kappa = 1
	gamma = 2
	thr_mask = 255

	# Decorrelator neuron
	decorrelator_group = create_ibm_neuron(tau, 1, Vr, epsilon, lmda, alpha, beta, kappa, gamma, thr_mask=thr_mask)

	# Create synapse connections
	weights = '''
	w : volt
	w_fb : volt
	'''
	synapse = Synapses(input_group, decorrelator_group, weights, on_pre='v_post += w', on_post='v_post += w_fb')
	synapse.connect(i = input_idx, j = 0)
	synapse.w = '16 * volt'
	synapse.w_fb = '-16 * volt'
	synapse.post.delay = tau

	return decorrelator_group, synapse