from numpy.random import rand
from brian2.only import defaultclock

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