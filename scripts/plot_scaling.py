import matplotlib.pyplot as plt
import numpy as np

def read_file(infile):
    ''' Read three column scaling input files'''
    data = np.loadtxt(infile)
    return data[:,0], data[:,1], data[:,2]


# read in cpu scaling and normalize performance
nc, cc, pc = read_file("cpu_scaling")
y0 = np.min(pc)
yc = pc/y0
xc = nc

# read in gpu scaling and normalize performance
ng, cg, pg = read_file("gpu_scaling")
yg = pg/y0
xg = ng

# Convert x-axis to cost
cph_g = 325./24
cph_c = 1.5*3
xg *= cph_g
xc *= cph_c

fig, ax = plt.subplots()

ax.scatter(xc,yc,marker='s',label='CPU')
ax.scatter(xg,yg,marker='o',label='GPU')
ax.set_ylabel('Relative Performance')
#ax.set_xlabel('Node Count')

ax.set_xlabel('Cost (Camber Credits)')
ax.set_yscale('log')
ax.set_xscale('log')
plt.legend()

plt.savefig('scaling.png')

    
