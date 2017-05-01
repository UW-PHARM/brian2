from .ibm_lib import *
from .ibm_base import *
from .ibm_math import *
from .ibm_signal_processing import *
from .ibm_matrix import *

# Automatically set target as Python fallback
from brian2.core.core_preferences import *
prefs.codegen.target = 'cython'