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
indices, times = gen_spike_trains(tau, num_ticks, [0.1, 0.2])
input_group = SpikeGeneratorGroup(2, indices, times)

# Max-subtractor neuron
G1, S1 = create_max_subtractor(tau, input_group, [0, 1])
G2, S2 = create_max_subtractor(tau, input_group, [1, 0])

input_mon = SpikeMonitor(input_group)
output_mon1 = SpikeMonitor(G1)
output_mon2 = SpikeMonitor(G2)

run(num_ticks * tau)

idx = find_idx(input_mon.i, lambda x : x == 0)
freq = len(idx) / num_ticks * (1 / tau)
plt.plot(filter_idx(input_mon.t, idx), filter_idx(input_mon.i, idx), '.r', label=("Input A (%fHz)" % freq))
idx = find_idx(input_mon.i, lambda x : x == 1)
freq = len(idx) / num_ticks * (1 / tau)
plt.plot(filter_idx(input_mon.t, idx), filter_idx(input_mon.i, idx), '.b', label=("Input B (%fHz)" % freq))
freq = len(output_mon1.i) / num_ticks * (1 / tau)
plt.plot(output_mon1.t, output_mon1.i + 2, '.g', label=("Output C (%fHz)" % freq))
plt.xlabel('Time (s)')
plt.ylabel('Spikes')
plt.title('Simulation Results for A - B')
plt.legend()
plt.grid(True, which='both')
frame = plt.gca()
frame.axes.get_yaxis().set_ticks([])
plt.show()

idx = find_idx(input_mon.i, lambda x : x == 0)
freq = len(idx) / num_ticks * (1 / tau)
plt.plot(filter_idx(input_mon.t, idx), filter_idx(input_mon.i, idx), '.r', label=("Input A (%fHz)" % freq))
idx = find_idx(input_mon.i, lambda x : x == 1)
freq = len(idx) / num_ticks * (1 / tau)
plt.plot(filter_idx(input_mon.t, idx), filter_idx(input_mon.i, idx), '.b', label=("Input B (%fHz)" % freq))
freq = len(output_mon2.i) / num_ticks * (1 / tau)
plt.plot(output_mon2.t, output_mon2.i + 2, '.g', label=("Output C (%fHz)" % freq))
plt.xlabel('Time (s)')
plt.ylabel('Spikes')
plt.title('Simulation Results for B - A')
plt.legend()
plt.grid(True, which='both')
frame = plt.gca()
frame.axes.get_yaxis().set_ticks([])
plt.show()