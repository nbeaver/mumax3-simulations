import numpy as np
from mumax_python_helpers import *
import os
import shutil
os.environ['PATH'] += ":/work/sglabfiles/software/mumax"
import time

## THIS IS WHERE THE DATA WILL BE MOVED TO AFTER SAVING
savedir = "."
simname = "spinwave_testing"

# NUMERICAL PARAMETERS
fmax = 20e9        # maximum frequency (in Hz) of the sinc pulse
T    = 1e-8        # simulation time (longer -> better frequency resolution)
dt   = 1/(2*fmax)  # the sample time
dx   = 10e-9        # cellsize
nx   = 1024        # number of cells

# MATERIAL/SYSTEM PARAMETERS
Bx    = 0.2        # Bias field along the z direction
A     = 13e-12     # exchange constant
Ms    = 800e3      # saturation magnetization
alpha = 0.05       # damping parameter
gamma = 1.76e11    # gyromagnetic ratio

# Note that this is a format string, this means that the statements inside the 
# curly brackets get evaluated by python. In this way, we insert the values of 
# the variables above in the script.
script=f"""
setgridsize({nx},{nx},1)
setcellsize({dx},{dx},{dx})

enabledemag = false
Aex = {A}
Msat = {Ms}
alpha = {alpha}

Bx := {Bx}
B_ext = vector({Bx},0, 0)
defregion(1,rect(5*{dx},5*{dx}))
B_ext.setregion(1, vector({Bx}, 0, 0.01 * sinc( 2*pi*{fmax}*(t-{T}/2))))

m = uniform(1,0,0) 
autosave(m,{dt})
tableautosave({dt})
run({T})
"""
start_time = time.perf_counter() 
table, fields = run_mumax3(script,simname)
end_time = time.perf_counter()

if savedir is not '.':
    shutil.move(simname + '.out', savedir)

elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time} seconds")
