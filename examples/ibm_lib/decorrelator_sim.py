from brian2 import *
import matplotlib.pyplot as plt
from brian2.ibm_lib import *
from numpy import corrcoef

def corr(a, b):
	result = corrcoef(a, b)
	return abs(result[0][1])

start_scope()

# Timing parameters
num_ticks = 3000
tau = 1 * ms

# Setup Brian with IBM lib
setup_brian(tau)

# Input spike train neurons
indices, times = gen_spike_trains(tau, num_ticks, [0.1])
input_group = SpikeGeneratorGroup(1, indices, times)

# Adder neuron
G, S = create_decorrelator(tau, input_group, [0])

input_mon = SpikeMonitor(input_group)
output_mon = SpikeMonitor(G)
v_mon = StateMonitor(G, 'v', record=True)
prn_mon = StateMonitor(G, 'eta', record=True)
input_pop = PopulationRateMonitor(input_group)
output_pop = PopulationRateMonitor(G)

run(num_ticks * tau)

plt.figure(1)
freq = len(input_mon.i) / num_ticks * (1 / tau)
plt.plot(input_mon.t, input_mon.i, '.r', label=("Input (%fHz)" % freq))
freq = len(output_mon.i) / num_ticks * (1 / tau)
plt.plot(output_mon.t, output_mon.i + 1, '.g', label=("Output (%fHz)" % freq))
plt.xlabel('Time (s)')
plt.ylabel('Spikes')
plt.title('Simulation Results')
plt.legend()
plt.grid(True, which='both')
frame = plt.gca()
frame.axes.get_yaxis().set_ticks([])
plt.show()

plt.figure(2)
plt.plot(v_mon.t, v_mon.v[0], label='Membrane Potential')
plt.plot(input_mon.t, input_mon.i, '.r', label=("Input Spikes"))
plt.plot(output_mon.t, output_mon.i + 1, '.g', label=("Output Spikes"))
plt.xlabel('Time (s)')
plt.ylabel('Voltage (V)')
plt.title('Neuron Membrane Potential')
plt.legend()
plt.grid(True, which='both')
plt.show()

print("First 10 masked threshold values for decorrelator neuron")
for i in range(10):
	print("%s \t\t(%d)" % (bin(int(prn_mon.eta_[0][i])), int(prn_mon.eta_[0][i])))

j = 0
k = 0
x = []
y = []
for i in range(num_ticks):
	if (input_mon.t_[j] - i * 0.001 < 0.0001) and (j < len(input_mon.t) - 1):
		x.append(1)
		j += 1
	else:
		x.append(0)

	if (output_mon.t_[k] - i * 0.001 < 0.0001) and (k < len(output_mon.t) - 1):
		y.append(1)
		k += 1
	else:
		y.append(0)
print("The auto-correlation of the input is %.2f" % corr(x, x))
print("The correlation of the input and output is %.2f" % corr(x, y))