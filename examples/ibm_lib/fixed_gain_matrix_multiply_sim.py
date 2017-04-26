from brian2 import *
import matplotlib.pyplot as plt
from brian2.ibm_lib import *
import pdb

start_scope()

# Timing parameters
num_ticks = 10000
tau = 1 * ms

# Setup Brian with IBM lib
setup_brian(tau)

# Input spike train neurons
input_matrix = array([[0.1, 0.2], [0.2, 0.1]])
indices, times = gen_spike_trains(tau, num_ticks, reshape(input_matrix, -1))
input_group = SpikeGeneratorGroup(4, indices, times)

# Weights
weights = array([[0.2, 0.3], [0.3, 0.2]])

# Fixed-gain dot product neuron
input_idx = arange(4).reshape((2, 2))
groups, synapses = create_fixed_gain_matrix_multiply(tau, input_group, input_idx, weights)

# pdb.set_trace()

# for S in synapses:
# 	visualise_connectivity(S)

input_mon = SpikeMonitor(input_group)
output_mons = []
for G in groups:
	output_mons.append(SpikeMonitor(G))

# Manually add groups and synapses to network
net = Network(collect())
net.add(groups)
net.add(synapses)
net.add(output_mons)

# Run for the manually created network
net.run(num_ticks * tau)

# Print results
actual_result = dot(weights, input_matrix)
print("Actual result:")
print(actual_result)

estimated_input_matrix = zeros(input_matrix.shape)
measured_result = zeros(actual_result.shape)
for j in range(input_matrix.shape[0]):
	for k in range(input_matrix.shape[1]):
		idx = find_idx(input_mon.i, lambda x : x == (j * 2 + k))
		estimated_input_matrix[j, k] = len(filter_idx(input_mon.i, idx)) / num_ticks
for j in range(actual_result.shape[0]):
	for k in range(actual_result.shape[1]):
		measured_result[j, k] = len(output_mons[j * 2 + k].i) / num_ticks
print("Stochastic input matrix:")
print(estimated_input_matrix)
print("Measured result:")
print(measured_result)

# Print error
print("Stochastic representation error (L2 norm) is %.3f" % norm(estimated_input_matrix - input_matrix, ord=2))
print("Error (L2 norm) is %.3f" % norm(measured_result - actual_result, ord=2))