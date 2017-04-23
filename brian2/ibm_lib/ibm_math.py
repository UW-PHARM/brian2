from brian2.only import NeuronGroup
from brian2.only import Synapses
from brian2.units import *
from .ibm_base import *

def create_adder(tau, input_group, input_idx):
	# Adder neuron parameters
	Vr = 0 * volt
	epsilon = 1
	lmda = 0 * volt
	alpha = 1 * volt
	beta = 0 * volt
	kappa = 1
	gamma = 1

	# Adder neuron
	output_group = create_ibm_neuron(tau, 1, Vr, epsilon, lmda, alpha, beta, kappa, gamma)

	# Create synapse connections
	synapse = Synapses(input_group, output_group, 'w : volt', on_pre='v_post += w')
	synapse.connect(i = input_idx, j = 0)
	synapse.w = '1 * volt'

	return output_group, synapse