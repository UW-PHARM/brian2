from brian2.only import NeuronGroup
from brian2.core.functions import Function, DEFAULT_FUNCTIONS
from brian2.only import CPPCodeGenerator
from brian2.units import *

def lfsr_rand():
	# XNOR taps from 32, 22, 2, 1
	max_val = 2 ** 32 - 1
	if "lfsr_reg" not in lfsr_rand.__dict__: lfsr_rand.lfsr_reg = max_val
	bit32 = (lfsr_reg >> 32) & 1
	bit22 = (lfsr_reg >> 22) & 1
	bit2 = (lfsr_reg >> 2) & 1
	bit1 = (lfsr_reg >> 1) & 1
	shift_in = ~(((bit32 ^ bit22) ^ bit2) ^ bit1) & 1
	lfsr_reg = ((lfsr_reg << 1) & max_val) | shift_in

	return lfsr_reg
lfsr_rand_code = {'support_code': '''
	uint32_t _lfsr_rand(void) {
		static uint32_t lfsr_reg = pow(2, 32) - 1;
		uint8_t bit32 = (lfsr_reg >> 32) & 1;
		uint8_t bit22 = (lfsr_reg >> 22) & 1;
		uint8_t bit2 = (lfsr_reg >> 2) & 1;
		uint8_t bit1 = (lfsr_reg >> 1) & 1;
		uint8_t shift_in = ~(((bit32 ^ bit22) ^ bit2) ^ bit1) & 1;
		lfsr_reg = (lfsr_reg << 1) | shift_in;

		return lfsr_reg;
	}
	'''}
lfsr_rand = Function(lfsr_rand, arg_units=[], return_unit=1, stateless=False)
lfsr_rand.implementations.add_implementation(CPPCodeGenerator, name='_lfsr_rand', code=lfsr_rand_code)
DEFAULT_FUNCTIONS['lfsr_rand'] = lfsr_rand

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