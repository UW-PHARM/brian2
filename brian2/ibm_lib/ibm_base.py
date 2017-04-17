from brian2.only import NeuronGroup
from brian2.units import *

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