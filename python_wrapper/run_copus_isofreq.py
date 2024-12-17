import numpy as np
import mumax_python_helpers
import os
import shutil
os.environ['PATH'] += ":/work/sglabfiles/software/mumax"
import time
import sys

index = int(sys.argv[1])
freq  = float(sys.argv[2])
print("index = '{}'".format(index))
print("freq = '{}'".format(freq))
#working_dir = "/work/sglabfiles/nathaniel/mumax3-simulations/amp_series_out"
working_dir = "/scratch/n.beaver/17_copus_isofreq_permalloy"
os.makedirs(working_dir, exist_ok=True)
os.chdir(working_dir)
simname = "copus_isofreq_permalloy_{:03d}".format(index)

# Based on Copus, et al. 2022
# https://doi.org/10.1063/5.0101394

# MATERIAL/SYSTEM PARAMETERS
#freq  = 9.0e9     # [Hz] excitation frequency
Bx    = 0.1        # [T] Bias field along the x direction
Aex   = 1.3e-11    # [J/m] exchange constant
Msat  = 8e5        # [A/m] saturation magnetization
alpha = 0.0001     # [dimensionless] Gilbert damping parameter
Ku1   = 0.0        # uniaxial anisotropy
amp   = 20e-4      # [T] excitation amplitude
t     = 30e-9 # [m] thickness of film

# Note that this is a format string, this means that the statements inside the
# curly brackets get evaluated by python. In this way, we insert the values of
# the variables above in the script.
script=f"""
f := {freq}      // excitation freq       [Hz]
bstat := {Bx}    // static field          [T]
amp := 0.0007    // excitation amplitude  [T_p]

Nx := 1024       // number of cells in x-direction
Ny := 1024       // number of cells in y-direction
Nz := 1          // number of cells in z-direction
c := 5e-9        // cell width           [m]
d := {t}         // cell height          [m]
setgridsize(Nx, Ny, Nz)
setcellsize(c, c, d)

// define grains with region number 0-254
grainSize  := 40e-9          // grain size           [m]
randomSeed := 123456789
maxRegion  := 255
ext_makegrains(grainSize, maxRegion, randomSeed)

// Already defined, so don't use :=
alpha   = {alpha}
Ku1     = {Ku1}
Aex     = {Aex}
Msat    = {Msat}

// set uniform parameters for grains
for i:=0; i<maxRegion; i++ {{
  Msat.SetRegion(i, Msat.GetRegion(0))
  alpha.SetRegion(i, alpha.GetRegion(0))
  Aex.SetRegion(i, Aex.GetRegion(0))
}}

//save starting conditions
save(regions)
save(Msat)
save(exchCoupling)

// relax to static field
// static field in x direction
B_ext = vector(bstat, 0, 0)
m = uniform(1,0,0)

// Remove surface charges from left (mx=1) and right (mx=-1) sides.
// Do this before running relax().
BoundaryRegion := 0
MagLeft        := 1
MagRight       := -1
ext_rmSurfaceCharge(BoundaryRegion, MagLeft, MagRight)

// relax M to x direction
relax() // high-energy states best minimized by relax() 
// save starting magnetization
save(m)

Snapshot(alpha)
Snapshot(Ku1)
Snapshot(Msat)
Snapshot(Regions)

// mask for excitation field
mask1 := newVectorMask(Nx, Ny, Nz)

i_0 := 511
j_0 := 511
k_0 := 0
for i := 0; i < 2; i++ {{
  for j := 0; j < 2; j++ {{
    for k := 0; k < 1; k++ {{
      ii := i + i_0
      jj := j + j_0
      kk := k + k_0
      r := index2coord(ii, jj, kk)
      x := r.X()
      y := r.Y()
      print(i, j, k, ii, jj, kk, x, y)
      mask1.setVector(ii, jj, kk, Vector(0.0, 0.0, 1.0))
    }}
  }}
}}
B_ext.add(mask1, amp*sin(2*pi*f*t))

//Simulation Time
points    := 2100
// time step, reqall f_Nyquist = 1/(2 dt)
tstep     := 0.1e-12
simtime   := tstep * points

//save m_full as .ovf
autosave(m_full, tstep)

// limit max solver step to avoid missing points in fft
maxdt = 0.1e-12

// run simulation
run(simtime)
"""

start_time = time.perf_counter()
table, fields = mumax_python_helpers.run_mumax3(script,simname)
end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time} seconds")
