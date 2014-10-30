'''
Check that the features of `NeuronGroup` are available and correct.
'''
from brian2 import *
from brian2.tests.features import FeatureTest, InaccuracyError

class NeuronGroupIntegrationLinear(FeatureTest):
    
    category = "NeuronGroup"
    name = "Linear integration"
    tags = ["NeuronGroup", "Network", "Network.run"]
    
    def run(self):
        self.tau = tau = 1*second
        self.v_init = linspace(0.1, 1, 10)
        self.duration = 100*ms
        self.G = NeuronGroup(10, 'dv/dt=-v/tau:1')
        self.G.v = self.v_init
        self.net = Network(self.G)
        self.net.run(self.duration)
        
    def results(self):
        return self.G.v[:]
            
    def check(self, maxrelerr, v_end):
        v_correct = self.v_init*exp(-self.duration/self.tau)
        err = amax(abs(v_end-v_correct)/v_correct)
        if err>maxrelerr:
            raise InaccuracyError(err)
            
    
class NeuronGroupIntegrationEuler(FeatureTest):
    
    category = "NeuronGroup"
    name = "Euler integration"
    tags = ["NeuronGroup", "Network", "Network.run"]
    
    def run(self):
        self.tau = tau = 1*second
        self.v_init = linspace(0.1, 1, 10)
        self.duration = 100*ms
        self.G = NeuronGroup(10, 'dv/dt=-v**1.1/tau:1')
        self.G.v = self.v_init
        self.net = Network(self.G)
        self.net.run(self.duration)
        
    def results(self):
        return self.G.v[:]
    
    compare = FeatureTest.compare_arrays


class NeuronGroupLIF(FeatureTest):
    
    category = "NeuronGroup"
    name = "Leaky integrate and fire"
    tags = ["NeuronGroup", "Threshold", "Reset",
            "Network", "Network.run",
            "SpikeMonitor"]
    
    def run(self):
        self.tau = tau = 10*ms
        self.duration = 1000*ms
        self.G = NeuronGroup(1, 'dv/dt=(1.2-v)/tau:1',
                             threshold='v>1', reset='v=0')
        self.M = SpikeMonitor(self.G)
        self.net = Network(self.G, self.M)
        self.net.run(self.duration)
        
    def results(self):
        return self.M.t[:]
    
    compare = FeatureTest.compare_arrays


class NeuronGroupLIFRefractory(FeatureTest):
    
    category = "NeuronGroup"
    name = "Refractory leaky integrate and fire"
    tags = ["NeuronGroup", "Threshold", "Reset", "Refractory",
            "Network", "Network.run",
            "SpikeMonitor"]
    
    def run(self):
        self.tau = tau = 10*ms
        self.duration = 1000*ms
        self.G = NeuronGroup(1, 'dv/dt=(1.2-v)/tau:1 (unless refractory)',
                             threshold='v>1', reset='v=0', refractory=1*ms)
        self.M = SpikeMonitor(self.G)
        self.net = Network(self.G, self.M)
        self.net.run(self.duration)
        
    def results(self):
        return self.M.t[:]
    
    compare = FeatureTest.compare_arrays

        
if __name__=='__main__':
#    ft = NeuronGroupIntegrationLinear()
#    ft.run()
#    res = ft.results()
#    ft.check(res)
    
    ft = NeuronGroupIntegrationEuler()
    ft.run()
    res = ft.results()
    