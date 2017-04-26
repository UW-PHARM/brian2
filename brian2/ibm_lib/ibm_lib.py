from numpy.random import rand
from brian2.only import defaultclock
from numpy import zeros, ones, arange
from matplotlib.pyplot import figure, plot, subplot, plot, xticks, xlim, ylim, xlabel, ylabel, show

def setup_brian(tau):
	defaultclock.dt = tau

def find_idx(a, func):
	return [i for (i, val) in enumerate(a) if func(val)]

def filter_idx(a, idx):
	return [a[i] for i in idx]

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

def visualise_connectivity(S, showPlot=True):
    Ns = len(S.source)
    Nt = len(S.target)
    figure(figsize=(10, 4))
    subplot(121)
    plot(zeros(Ns), arange(Ns), 'ok', ms=10)
    plot(ones(Nt), arange(Nt), 'ok', ms=10)
    for i, j in zip(S.i, S.j):
        plot([0, 1], [i, j], '-k')
    xticks([0, 1], ['Source', 'Target'])
    ylabel('Neuron index')
    xlim(-0.1, 1.1)
    ylim(-1, max(Ns, Nt))
    subplot(122)
    plot(S.i, S.j, 'ok')
    xlim(-1, Ns)
    ylim(-1, Nt)
    xlabel('Source neuron index')
    ylabel('Target neuron index')
    if showPlot:
    	show()