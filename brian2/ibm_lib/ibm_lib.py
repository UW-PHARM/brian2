from brian2 import *

def gen_spike_trains(tick, num_ticks, p):
	times = []
	indices = []
	for i in range(num_ticks):
		for j in range(len(p)):
			r = rand(1)
			if r < p[j]:
				times.append(i * tick)
				indices.append(j)

	return indices, times

def create_ibm_neuron(tau, N, Vr, epsilon, lmda, alpha, beta, kappa, gamma):
	namespace = {
		'tau' : tau
	}

	eqs = '''
	dv/dt = (omega * lmda) / tau : volt
	omega = (1 - epsilon) + epsilon * sign(v) : 1
	Vr : volt
	epsilon : 1
	lmda : volt
	alpha : volt
	beta : volt
	kappa : 1
	gamma : 1
	'''

	thresh = "(v >= alpha) or (v < -beta * kappa)"

	reset = '''
	a = int(gamma == 0) * (-1 * Vr)
	b = int(gamma == 1) * (v + beta)
	c = int(gamma == 2) * (v)
	d = int(gamma == 0) * (Vr)
	e = int(gamma == 1) * (v - alpha)
	f = int(gamma == 2) * (v)
	p = d + e + f
	n = -beta * kappa + (1 - kappa) * (a + b + c)
	v = int(v >= alpha) * p + int(v < -beta * kappa) * n
	'''

	group = NeuronGroup(N, eqs, threshold=thresh, reset=reset, method='euler', namespace=namespace)
	group.Vr = Vr
	group.epsilon = epsilon
	group.lmda = lmda
	group.alpha = alpha
	group.beta = beta
	group.kappa = kappa
	group.gamma = gamma

	return group

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
	synapse = Synapses(input_group, output_group, 'w : 1', on_pre='v_post += alpha')
	synapse.connect(i = input_idx, j = 0)
	synapse.w = '1'

	return output_group, synapse