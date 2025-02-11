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

working_dir = "/work/sglabfiles/nathaniel/mumax3-simulations/yig_isofreq_out/10_yig"
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
// setpbc(1,1,0) // periodic boundary conditions in x and y

// absorbing boundary layers.
ABL_alpha1 := {alpha} // alpha at start of ABL
ABL_alpha2 := 1.0 // alpha at stop of ABL
ABL_c := c // Cellsize along x and y
ABL_pow := 2 // polynomial order
ABL_Nstep := 40 // steps to use on edge, usually 200 nm
ABL_range := ABL_Nstep * ABL_c
ABL_coeff := (ABL_alpha2 - ABL_alpha1)/Pow(ABL_range, ABL_pow) // Polynomial coefficient
ABL_region_index_start := 1 // change as needed
ABL_xmax := (Nx/2) * ABL_c
ABL_ymax := (Ny/2) * ABL_c
ABL_x0 := ABL_xmax - (ABL_c * ABL_Nstep)
ABL_y0 := ABL_ymax - (ABL_c * ABL_Nstep)
// Set the damping with nesting rectangular borders.
for i := 0; i < ABL_Nstep; i++ {{
  x_i := ABL_x0 + (i+1)*ABL_c
  y_i := ABL_y0 + (i+1)*ABL_c
  // rectangular borders
  border_i := Rect(x_i*2,y_i*2).Sub(Rect( (x_i-ABL_c)*2, (y_i-ABL_c)*2 ))
  // alpha = a*(x-x0)**2
  alpha_i := ABL_coeff*Pow(x_i - ABL_x0, ABL_pow)
  region_i := ABL_region_index_start + i
  DefRegion(region_i, border_i)
  alpha.setregion(region_i, alpha_i)
}}

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
BoundaryRegion := ABL_region_index_start + ABL_Nstep - 1
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

i_0 := (Nx/2)-1
j_0 := (Ny/2)-1
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
      mask1.setVector(ii, jj, kk, Vector(0.0, 0.0, 1.0))
    }}
  }}
}}
B_ext.add(mask1, amp*sin(2*pi*f*t))



//Simulation Time
points    := 20
// time step, recall f_Nyquist = 1/(2 dt)
tstep     := 420e-12
simtime   := tstep * points

//save m_full as .ovf
autosave(m_full, tstep)

// limit max solver timestep TODO: what is the default?
print("default maxdt = ",maxdt)
print("default EdgeSmooth = ",EdgeSmooth)
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
