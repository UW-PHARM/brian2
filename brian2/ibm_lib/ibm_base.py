from brian2.only import NeuronGroup
from brian2.core.functions import Function, DEFAULT_FUNCTIONS
from brian2.only import CPPCodeGenerator, NumpyCodeGenerator
# from brian2.codegen.generators import CythonCodeGenerator
from brian2.units import *

def lfsr_rand(lfsr_reg):
	# XNOR taps from 32, 22, 2, 1
	bit32 = (lfsr_reg >> 31) & 1
	bit22 = (lfsr_reg >> 21) & 1
	bit2 = (lfsr_reg >> 1) & 1
	bit1 = lfsr_reg & 1
	shift_in = (((bit32 ^ bit22) ^ bit2) ^ bit1) & 1
	lfsr_reg = ((lfsr_reg << 1) & (2 ** 32 - 1)) | shift_in

	return lfsr_reg
lfsr_rand_cpp = {'support_code': '''
	uint32_t _lfsr_rand(uint32_t lfsr_reg) {
		uint8_t bit32 = (lfsr_reg >> 31) & 1;
		uint8_t bit22 = (lfsr_reg >> 31) & 1;
		uint8_t bit2 = (lfsr_reg >> 1) & 1;
		uint8_t bit1 = lfsr_reg & 1;
		uint8_t shift_in = (((bit32 ^ bit22) ^ bit2) ^ bit1) & 1;
		lfsr_reg = (lfsr_reg << 1) | shift_in;

		return lfsr_reg;
	}
	'''}
lfsr_rand_cython = {'support_code': '''
	cdef uint32_t _lfsr_rand(cdef uint32_t lfsr_reg):
		cdef uint8_t bit32 = (lfsr_reg >> 31) & 1
		cdef uint8_t bit22 = (lfsr_reg >> 21) & 1
		cdef uint8_t bit2 = (lfsr_reg >> 1) & 1
		cdef uint8_t bit1 = lfsr_reg & 1
		cdef uint8_t shift_in = (((bit32 ^ bit22) ^ bit2) ^ bit1) & 1
		lfsr_reg = (lfsr_reg << 1) | shift_in

		return lfsr_reg
	'''}
lfsr_rand_obj = Function(lfsr_rand, arg_units=[1], return_unit=1, arg_types=['integer'], return_type='integer')
lfsr_rand_obj.implementations.add_implementation(NumpyCodeGenerator, code=lfsr_rand)
lfsr_rand_obj.implementations.add_implementation(CPPCodeGenerator, name='_lfsr_rand', code=lfsr_rand_cpp)
# lfsr_rand_obj.implementations.add_implementation(CythonCodeGenerator, name='_lfsr_rand', code=lfsr_rand_cython)
DEFAULT_FUNCTIONS['lfsr_rand'] = lfsr_rand_obj

def get_prn(lfsr_reg, curr_prn):
	# XNOR taps from 32, 22, 2, 1
	return ((lfsr_reg >> 31) & 1) | ((curr_prn << 1) & (2 ** 32 - 1))
get_prn_cpp = {'support_code': '''
	uint32_t _get_prn(uint32_t lfsr_reg, uint32_t curr_prn) {
		return ((lfsr_reg >> 31) & 1) | (curr_prn << 1);
	}
	'''}
get_prn_cython = {'support_code': '''
	cdef uint32_t _lfsr_rand(cdef uint32_t lfsr_reg, cdef uint32_t curr_prn):
		return ((lfsr_reg >> 31) & 1) | (curr_prn << 1)
	'''}
get_prn_obj = Function(get_prn, arg_units=[1, 1], return_unit=1, arg_types=['integer', 'integer'], return_type='integer')
get_prn_obj.implementations.add_implementation(NumpyCodeGenerator, code=get_prn)
get_prn_obj.implementations.add_implementation(CPPCodeGenerator, name='_get_prn', code=get_prn_cpp)
DEFAULT_FUNCTIONS['get_prn'] = get_prn_obj

def bit_and(a, b):
	return a & b
bit_and_obj = Function(bit_and, arg_units=[1, 1], return_unit=1, arg_types=['integer', 'integer'], return_type='integer')
bit_and_obj.implementations.add_implementation(NumpyCodeGenerator, code=bit_and)
bit_and_obj.implementations.add_implementation(CPPCodeGenerator, name='operator&', code=None)
DEFAULT_FUNCTIONS['bit_and'] = bit_and_obj

def create_ibm_neuron(tau, N, Vr, epsilon, lmda, alpha, beta, kappa, gamma, lmda_prob=False, thr_mask=0, seed=(2 ** 32 - 1)):
	namespace = {
		'tau' : tau
	}

	eqs = '''
	dv/dt = (omega * ((1 - c_lmda) * lmda + (c_lmda * Fb * sign(lmda)) * volt)) / tau : volt
	omega = (1 - epsilon) + epsilon * sign(v) : 1
	c_lmda = int(lmda_prob) : 1
	Fb = int(abs(lmda) >= rho_lmda) : 1
	eta = bit_and(rho_thr, thr_mask) * volt : volt
	rho_lmda = bit_and(prn, int(255)) * volt : volt
	rho_thr = bit_and(prn, int(262143)) : integer # Masked with 2 ** 18 - 1
	Vr : volt
	epsilon : 1
	lmda : volt
	alpha : volt
	beta : volt
	kappa : 1
	gamma : 1
	lmda_prob : boolean
	thr_mask : integer
	prn : integer
	lfsr : integer
	up_bound : volt
	low_bound : volt
	'''

	thresh = "v > up_bound or v >= (alpha + eta)"
	neg_thresh = "v < low_bound or v < -1 * (beta * kappa + (beta + eta) * (1 - kappa))"

	reset = '''
	a = int(gamma == 0) * (Vr)
	b = int(gamma == 1) * (v - (alpha + eta))
	c = int(gamma == 2) * (v)
	p = a + b + c
	v = int(v > up_bound) * up_bound + int(v <= up_bound) * p
	'''
	neg_reset = '''
	d = int(gamma == 0) * (-1 * Vr)
	e = int(gamma == 1) * (v + beta + eta)
	f = int(gamma == 2) * (v)
	n = -beta * kappa + (1 - kappa) * (d + e + f)
	v = int(v < low_bound) * low_bound + int(v >= low_bound) * n
	'''

	prng_update = '''
	prn = get_prn(lfsr, prn)
	lfsr = lfsr_rand(lfsr)
	'''

	# Initialize LFSR
	lfsr_init = seed
	prn_init = 0
	for i in range(100):
		prn_init = get_prn(lfsr_init, prn_init)
		lfsr_init = lfsr_rand(lfsr_init)

	group = NeuronGroup(N, eqs, threshold=thresh, reset=reset, method='euler', namespace=namespace, events={'neg_thresh' : neg_thresh})
	group.Vr = Vr
	group.epsilon = epsilon
	group.lmda = lmda
	group.alpha = alpha
	group.beta = beta
	group.kappa = kappa
	group.gamma = gamma
	group.lmda_prob = lmda_prob
	group.thr_mask = thr_mask
	group.v = 0
	group.prn = prn_init
	group.lfsr = lfsr_init
	if gamma == 2:
		group.up_bound = alpha + thr_mask * volt
		group.low_bound = -1 * (beta + thr_mask * volt)
	else:
		group.up_bound = 393216 * volt
		group.low_bound = -393216 * volt
	group.run_regularly(prng_update, dt=0.01*tau)
	group.run_on_event('neg_thresh', neg_reset)

	return group