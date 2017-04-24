from brian2 import *
import matplotlib.pyplot as plt
from brian2.ibm_lib import *
from numpy import dot

start_scope()

# Timing parameters
num_ticks = 3000
tau = 1 * ms

# Setup Brian with IBM lib
setup_brian(tau)

# Input spike train neurons
input_vector = [0.1, 0.2]
indices, times = gen_spike_trains(tau, num_ticks, input_vector)
input_group = SpikeGeneratorGroup(2, indices, times)

# Weights
weights = [0.2, 0.3]

# Fixed-gain dot product neuron
G, S = create_fixed_gain_dot_product(tau, input_group, [0, 1], weights)

input_mon = SpikeMonitor(input_group)
output_mon = SpikeMonitor(G)

run(num_ticks * tau)

idx = find_idx(input_mon.i, lambda x : x == 0)
freq = len(idx) / num_ticks * (1 / tau)
plt.plot(filter_idx(input_mon.t, idx), filter_idx(input_mon.i, idx), '.r', label=("Input Index 0 (%fHz)" % freq))
idx = find_idx(input_mon.i, lambda x : x == 1)
freq = len(idx) / num_ticks * (1 / tau)
plt.plot(filter_idx(input_mon.t, idx), filter_idx(input_mon.i, idx), '.b', label=("Input Index 1 (%fHz)" % freq))
freq = len(output_mon.i) / num_ticks * (1 / tau)
plt.plot(output_mon.t, output_mon.i + 2, '.g', label=("Output Dot Product (%fHz)" % freq))
plt.xlabel('Time (s)')
plt.ylabel('Spikes')
plt.title('Simulation Results')
plt.legend()
plt.grid(True, which='both')
frame = plt.gca()
frame.axes.get_yaxis().set_ticks([])
plt.show()

print("Actual dot product is %.2f" % dot(input_vector, weights))
print("Simulated dot product is %.2f" % (freq * tau))