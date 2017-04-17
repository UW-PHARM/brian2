from numpy.random import rand

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