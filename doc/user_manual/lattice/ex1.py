from pytriqs.Base.Lattice.TightBinding import *

# Define the Bravais Lattice : a square lattice in 2d
BL = bravais_lattice(Units = [(1,0,0) , (0,1,0) ], Orbital_Positions= {"" :  (0,0,0)} ) 

# Prepare a nearest neighbour hopping on BL
t   = -1.00                # First neighbour Hopping
tp  =  0.0*t               # Second neighbour Hopping

# Hopping[ Displacement on the lattice] = [[t11,t12,t13....],[t21,t22,t23....],...,[....,tnn]] 
# where n=Number_Orbitals
hop= {  (1,0)  :  [[ t]],       
        (-1,0) :  [[ t]],     
        (0,1)  :  [[ t]],
        (0,-1) :  [[ t]],
        (1,1)  :  [[ tp]],
        (-1,-1):  [[ tp]],
        (1,-1) :  [[ tp]],
        (-1,1) :  [[ tp]]}

TB = tight_binding ( BL, hop)

# Compute the density of states
d = dos (TB, nkpts= 500, neps = 101, Name = 'dos')[0]

# Plot the dos it with matplotlib
from pytriqs.Base.Plot.MatplotlibInterface import oplot
from matplotlib import pylab as plt
oplot(d,'-o')
plt.xlim ( -5,5 )
plt.ylim ( 0, 0.4)





plt.savefig("./ex1.png") 



