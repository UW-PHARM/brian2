from brian2.only import NeuronGroup
from brian2.core.functions import Function, DEFAULT_FUNCTIONS
from brian2.only import CPPCodeGenerator, NumpyCodeGenerator
# from brian2.codegen.generators import CythonCodeGenerator
from brian2.units import *

def lfsr_rand(lfsr_reg):
	# XNOR taps from 32, 22, 2, 1
	bit32 = (lfsr_reg >> 32) & 1
	bit22 = (lfsr_reg >> 22) & 1
	bit2 = (lfsr_reg >> 2) & 1
	bit1 = (lfsr_reg >> 1) & 1
	shift_in = ~(((bit32 ^ bit22) ^ bit2) ^ bit1) & 1
	lfsr_reg = ((lfsr_reg << 1) & (2 ** 32 - 1)) | shift_in

	return lfsr_reg
lfsr_rand_cpp = {'support_code': '''
	uint32_t _lfsr_rand(uint32_t lfsr_reg) {
		uint8_t bit32 = (lfsr_reg >> 32) & 1;
		uint8_t bit22 = (lfsr_reg >> 22) & 1;
		uint8_t bit2 = (lfsr_reg >> 2) & 1;
		uint8_t bit1 = (lfsr_reg >> 1) & 1;
		uint8_t shift_in = ~(((bit32 ^ bit22) ^ bit2) ^ bit1) & 1;
		lfsr_reg = (lfsr_reg << 1) | shift_in;

		return lfsr_reg;
	}
	'''}
lfsr_rand_cython = {'support_code': '''
	cdef uint32_t _lfsr_rand(cdef uint32_t lfsr_reg):
		cdef uint8_t bit32 = (lfsr_reg >> 32) & 1
		cdef uint8_t bit22 = (lfsr_reg >> 22) & 1
		cdef uint8_t bit2 = (lfsr_reg >> 2) & 1
		cdef uint8_t bit1 = (lfsr_reg >> 1) & 1
		cdef uint8_t shift_in = ~(((bit32 ^ bit22) ^ bit2) ^ bit1) & 1
		lfsr_reg = (lfsr_reg << 1) | shift_in

		return lfsr_reg
	'''}
lfsr_rand_obj = Function(lfsr_rand, arg_units=[1], return_unit=1, arg_types=['integer', 'integer'], return_type='integer')
lfsr_rand_obj.implementations.add_implementation(NumpyCodeGenerator, code=lfsr_rand)
lfsr_rand_obj.implementations.add_implementation(CPPCodeGenerator, name='_lfsr_rand', code=lfsr_rand_cpp)
# lfsr_rand_obj.implementations.add_implementation(CythonCodeGenerator, name='_lfsr_rand', code=lfsr_rand_cython)
DEFAULT_FUNCTIONS['lfsr_rand'] = lfsr_rand_obj

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
	'''

	thresh = "v >= (alpha + eta)"

	reset = '''
	a = int(gamma == 0) * (-1 * Vr)
	b = int(gamma == 1) * (v + beta + eta)
	c = int(gamma == 2) * (v)
	d = int(gamma == 0) * (Vr)
	e = int(gamma == 1) * (v - (alpha + eta))
	f = int(gamma == 2) * (v)
	p = d + e + f
	n = -beta * kappa + (1 - kappa) * (a + b + c)
	v = int(v >= (alpha + eta)) * p + int(v < -(beta * kappa + (beta + eta) * (1 - kappa))) * n
	'''

	group = NeuronGroup(N, eqs, threshold=thresh, reset=reset, method='euler', namespace=namespace)
	group.Vr = Vr
	group.epsilon = epsilon
	group.lmda = lmda
	group.alpha = alpha
	group.beta = beta
	group.kappa = kappa
	group.gamma = gamma
	group.v = 0
	group.prn = seed
	group.run_regularly('prn = lfsr_rand(prn)')

	return group