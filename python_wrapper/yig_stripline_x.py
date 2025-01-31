import mumax_python_helpers
import os
os.environ['PATH'] += ":/work/sglabfiles/software/mumax"
import time
import sys

index = int(sys.argv[1])
freq  = float(sys.argv[2])
print("index = '{}'".format(index))
print("freq = '{}'".format(freq))

job_name = os.environ['SLURM_JOB_NAME']
print("SLURM_JOB_NAME = '{}'".format(job_name))

working_dir = "/work/sglabfiles/nathaniel/mumax3-simulations/yig_stripline_x_out/06_yig"
os.makedirs(working_dir, exist_ok=True)
os.chdir(working_dir)
simname = "yig_isofreq_{:03d}".format(index)


# MATERIAL/SYSTEM PARAMETERS
#freq  = 9.0e9     # [Hz] excitation frequency
Bx    = 327e-4     # [T] Bias field along the x direction
Aex   = 4.15e-12   # [J/m] exchange constant
Msat  = 1.6e5      # [A/m] saturation magnetization
alpha = 0.005      # [dimensionless] Gilbert damping parameter
Ku1   = 0.0        # uniaxial anisotropy
amp   = 2e-4       # [T] excitation amplitude
t     = 130e-9       # [m] thickness of film

# Note that this is a format string, this means that the statements inside the
# curly brackets get evaluated by python. In this way, we insert the values of
# the variables above in the script.
script=f"""
// Based on Copus, et al. 2022
// https://doi.org/10.1063/5.0101394
f := {freq}      // excitation freq       [Hz]
bstat := {Bx}    // static field          [T]
amp := {amp}     // excitation amplitude  [T_p]

// Already defined, so don't use :=
alpha   = {alpha}
Ku1     = {Ku1}
Aex     = {Aex}
Msat    = {Msat}

Nx := 1024       // number of cells in x-direction
Ny := 1024       // number of cells in y-direction
Nz := 1          // number of cells in z-direction
c := 5e-9        // cell width           [m]
d := {t}         // cell height          [m]

setgridsize(Nx, Ny, Nz)
setcellsize(c, c, d)

//save starting conditions
save(regions)
save(Msat)
save(exchCoupling)

// relax to static field
// static field in x direction
B_ext = vector(bstat, 0, 0)
m = uniform(1,0,0)

// Remove surface charges from left (mx=+1) and right (mx=+1) sides.
// Do this before running relax().
BoundaryRegion := 0
MagLeft        := 1
MagRight       := 1
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

j_0 := (Ny/2)-1
k_0 := 0
for i := 0; i < Nx; i++ {{
  for j := 0; j < 2; j++ {{
    for k := 0; k < 1; k++ {{
      ii := i
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
points    := 20
// time step, recall f_Nyquist = 1/(2 dt)
tstep     := 210e-12
simtime   := tstep * points

//save m_full as .ovf
autosave(m_full, tstep)

// limit max solver timestep
maxdt = 1.0e-12
// limit max solver error (default 1e-5)
MaxErr = 1e-8

// run simulation
run(simtime)
"""

start_time = time.perf_counter()
table, fields = mumax_python_helpers.run_mumax3(script,simname)
end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time} seconds")
