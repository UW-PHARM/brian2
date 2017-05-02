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

def create_max_subtractor(tau, input_group, input_idx, input_is_array=False):
	# Check length of input_idx
	if len(input_idx) != 2:
		raise ValueError('create_max_subtractor accepts input_idx of size 2 only.')

	# Max-subtractor neuron parameters
	Vr = 0 * volt
	epsilon = 1
	lmda = 0 * volt
	alpha = 1 * volt
	beta = 100 * volt
	kappa = 1
	gamma = 1

	# Max-subtractor neuron
	output_group = create_ibm_neuron(tau, 1, Vr, epsilon, lmda, alpha, beta, kappa, gamma)

	# Create synapse connections
	if input_is_array:
		synapse1 = Synapses(input_group[0], output_group, 'w : volt', on_pre='v_post += w')
		synapse1.connect(i = input_idx[0], j = 0)
		synapse1.w = '1 * volt'
		synapse2 = Synapses(input_group[1], output_group, 'w : volt', on_pre='v_post += w')
		synapse2.connect(i = input_idx[1], j = 0)
		synapse2.w = '-1 * volt'
		return output_group, [synapse1, synapse2]
	else:
		synapse = Synapses(input_group, output_group, 'w : volt', on_pre='v_post += w')
		synapse.connect(i = input_idx, j = 0)
		synapse.w[input_idx[0], 0] = '1 * volt'
		synapse.w[input_idx[1], 0] = '-1 * volt'
		return output_group, synapse

def create_multiplier(tau, input_group, input_idx):
	# Multiplier neuron parameters
	Vr = 0 * volt
	epsilon = 1
	lmda = -1 * volt
	alpha = 1 * volt
	beta = 0 * volt
	kappa = 1
	gamma = 0

	# Adder neuron
	output_group = create_ibm_neuron(tau, 1, Vr, epsilon, lmda, alpha, beta, kappa, gamma)

	# Create synapse connections
	synapse = Synapses(input_group, output_group, 'w : volt', on_pre='v_post += w')
	synapse.connect(i = input_idx, j = 0)
	synapse.w = '1 * volt'

	return output_group, synapse