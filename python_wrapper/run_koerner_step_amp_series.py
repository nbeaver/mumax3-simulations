import numpy as np
import mumax_python_helpers
import os
import shutil
os.environ['PATH'] += ":/work/sglabfiles/software/mumax"
import time
import sys

index = int(sys.argv[1])
amp = float(sys.argv[2])
#amp = 7e-4
print("index = '{}'".format(index))
print("amp = '{}'".format(amp))
#working_dir = "/work/sglabfiles/nathaniel/mumax3-simulations/amp_series_out"
working_dir = "/scratch/n.beaver/amp_series_02_out"
os.makedirs(working_dir, exist_ok=True)
os.chdir(working_dir)
simname = "FeGaB_koerner_02_amp_series_{:03d}".format(index)


# MATERIAL/SYSTEM PARAMETERS
freq = 1425.0e6
Bx    = 12.0e-4        # Bias field along the x direction
Aex    = 14.9e-12     # exchange constant
Msat  = 1030e3      # saturation magnetization
alpha = 0.02       # damping parameter
Ku1   = 1035 # uniaxial anisotropy

# Note that this is a format string, this means that the statements inside the 
# curly brackets get evaluated by python. In this way, we insert the values of 
# the variables above in the script.
script=f"""
f 		:= {freq}												// excitation freq				[Hz]
bstat 	:= {Bx}												// static field					[T]
amp 	:= {amp}												// excitation amplitude 		[T_p]

N := 256														// number of cells
c := 20e-9														// cell width					[m]
d := 20e-9														// cell height					[m]
setgridsize(N, N, 1)	
setcellsize(c, c, d)
//setpbc(50,50,0)

// average FeGaB magnetic parameters set for region 0
alpha 	= {alpha}
Ku1   	= {Ku1}													// uniaxial anisotropy			[J/m^3]
Aex   	= {Aex}												// exchange energy				[J/m]		http://www.cwscholz.net/projects/diss/html/node58.html
Msat  	= {Msat}													// saturation magnetization 	[A/m]

// define regions
defregion(1, xrange(0, inf))  // left half
defregion(2, xrange(-inf, 0)) // right half

// set parameters for region 1
Ku1.setregion(1, Ku1.GetRegion(0))
anisU.setRegion(1, vector(1, 0, 0))
Msat.SetRegion(1, Msat.GetRegion(0)*0.8)
alpha.SetRegion(1, alpha.GetRegion(0))	
Aex.SetRegion(1, Aex.GetRegion(0))	

// set parameters for region 2
Ku1.setregion(2, Ku1.GetRegion(0))
anisU.setRegion(2, vector(1, 0, 0))
Msat.SetRegion(2, Msat.GetRegion(0))
alpha.SetRegion(2, alpha.GetRegion(0))	
Aex.SetRegion(2, Aex.GetRegion(0))	
			
// save starting conditions as .ovf
save(regions)
save(Ku1)
save(AnisU)
save(Msat)
save(exchCoupling)


// save starting conditions as .png
Snapshotas(regions,"regions_init.png")
Snapshotas(AnisU,"AnisU_init.png")
Snapshotas(alpha,"alpha_init.png")
Snapshotas(Ku1,"Ku1_init.png")
Snapshotas(Msat,"Msat_init.png")


// relax to static field
// static field in x direction
B_ext = vector(bstat, 0, 0)			

m = uniform(1,0,0)		//.Add(0.1, randomMag());

// remove surface charges left/right
BoundaryRegion := 0
MagLeft        := 1
MagRight       := 1
ext_rmSurfaceCharge(BoundaryRegion, MagLeft, MagRight)

// relax M to x direction											
run(10e-9)		

saveas(m,"m_relax.ovf")
Snapshotas(m,"m_relax.png")

// static + excitation field
B_ext = vector(bstat, amp*sin(2*pi*f*t), 0)
// settling time
run(200e-9)														

//Simulation Time
points 		:= 8192								
tstep 		:= 12.5e-12											// 10ns -> largest fft-freq = 5GHz					12.5e-12s -> 40GHz
simtime 	:= tstep * points

//TableAdd(Crop(B_ext, 64, 65, 64, 65, 0, 1))					// cols 11,12,13 = B_ext
//TableAutoSave(tstep)

//save m_full as .ovf
save_step := 50e-12
autosave(m_full, save_step)	

// limit max solver step to avoid missing points in fft
maxdt = 1e-12												

// run simulation
run(simtime)
"""

start_time = time.perf_counter() 
table, fields = mumax_python_helpers.run_mumax3(script,simname)
end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time} seconds")
