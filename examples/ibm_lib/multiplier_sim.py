from brian2 import *
import matplotlib.pyplot as plt
from brian2.ibm_lib import *

start_scope()

# Timing parameters
num_ticks = 3000
tau = 1 * ms

# Setup Brian with IBM lib
setup_brian(tau)

# Input spike train neurons
indices, times = gen_spike_trains(tau, num_ticks, [0.2, 0.2])
input_group = SpikeGeneratorGroup(2, indices, times)

# Adder neuron
G, S = create_multiplier(tau, input_group, [0, 1])

input_mon = SpikeMonitor(input_group)
output_mon = SpikeMonitor(G)

run(num_ticks * tau)

# Plot the output of the multiplication
idx = find_idx(input_mon.i, lambda x : x == 0)
freq = len(idx) / num_ticks * (1 / tau)
plt.plot(filter_idx(input_mon.t, idx), filter_idx(input_mon.i, idx), '.r', label=("Input A (%fHz)" % freq))
idx = find_idx(input_mon.i, lambda x : x == 1)
freq = len(idx) / num_ticks * (1 / tau)
plt.plot(filter_idx(input_mon.t, idx), filter_idx(input_mon.i, idx), '.b', label=("Input B (%fHz)" % freq))
freq = len(output_mon.i) / num_ticks * (1 / tau)
plt.plot(output_mon.t, output_mon.i + 2, '.g', label=("Output C (%fHz)" % freq))
plt.xlabel('Time (s)')
plt.ylabel('Spikes')
plt.title('Simulation Results')
plt.legend()
plt.grid(True, which='both')
frame = plt.gca()
frame.axes.get_yaxis().set_ticks([])
plt.show()
