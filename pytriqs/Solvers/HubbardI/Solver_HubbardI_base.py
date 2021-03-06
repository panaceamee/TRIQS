
################################################################################
#
# TRIQS: a Toolbox for Research in Interacting Quantum Systems
#
# Copyright (C) 2011 by M. Ferrero, O. Parcollet
#
# TRIQS is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# TRIQS is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# TRIQS. If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

from types import *
#from pytriqs.Base import DataTestTools
from pytriqs.Solvers import Solver_Base
from pytriqs.Base.GF_Local.GFBloc_ImFreq import *
from pytriqs.Base.GF_Local.GFBloc_ReFreq import *
from pytriqs.Base.GF_Local.GF import GF
from pytriqs.Base.GF_Local import GF_Initializers
from hubbard_I import gf_hi_fullu, sigma_atomic_fullu
import copy
from pytriqs.Base.GF_Local import inverse
import pytriqs.Base.Utility.Parameters as Parameters
import pytriqs.Base.Utility.MPI as MPI
import numpy
from itertools import izip

__add__ =[]

class Solver_HubbardI_base(Solver_Base):
    """
       Python interface to the fortran Hubbard-I Solver.
    """

    Required = {
        "ur" : ("4-index interaction matrix",type(numpy.zeros([1]))),
        "umn" : ("2-index reduced matrix U(m,m',m,m')",type(numpy.zeros([1]))),
        "ujmn" : ("2-index reduced matrix U(m,m',m,m')-U(m,m',m',m)",type(numpy.zeros([1]))),
        #"zmsb" : ("Imaginary energy mesh",type(numpy.zeros([1]))),
        "Nlm" : ("Number of orbitals",IntType)
        }

    Optional = {
        "Nmsb" : ( "Number of frequencies of the Green's functions", 1025, IntType ),
        "Nspin" : ("Number of spin channels used",2,IntType),
        "Nmoments" : ("Number of high frequency moments to be computed",5,IntType),
        "UseSpinOrbit" : ("Use Spin-Orbit coupling?",False,BooleanType),
        "Verbosity" : ("Verbosity level of Fortran output",1,IntType)
        }

    # initialisation:
    def __init__(self,Beta,GFstruct,**param):
        self.Beta = float(Beta)
        Parameters.check_no_parameters_not_in_union_of_dicts (param,self.Required, self.Optional)
        #DataTestTools.EnsureAllParametersMakeSense(self,param)
        if 'Nmsb' not in param : param['Nmsb'] = 1025
        if 'Nspin' not in param : param['Nspin'] = 2

        Solver_Base.__init__(self,GFstruct,param)

        # construct Greens functions:
        self.a_list = [a for a,al in self.GFStruct]
        glist = lambda : [ GFBloc_ImFreq(Indices = al, Beta = self.Beta, NFreqMatsubara = self.Nmsb) for a,al in self.GFStruct]
        self.G = GF(NameList = self.a_list, BlockList = glist(),Copy=False)
        self.G_Old = self.G.copy()
        self.G0 = self.G.copy()
        self.Sigma = self.G.copy()
        self.Sigma_Old = self.G.copy()
        M = [x for x in self.G.mesh]
        self.zmsb = numpy.array([x for x in M],numpy.complex_)
        
        # for the tails:
        self.tailtempl={}
        for sig,g in self.G: 
            self.tailtempl[sig] = copy.deepcopy(g._tail)
            for i in range(11): self.tailtempl[sig][i].array[:] *= 0.0
    
        self.Name=''

        # effective atomic levels:
        if self.UseSpinOrbit: self.NSpin=2

        self.ealmat = numpy.zeros([self.Nlm*self.Nspin,self.Nlm*self.Nspin],numpy.complex_)
        


    def Solve(self,Iteration_Number=1,Test_Convergence=0.0001):
        """Calculation of the impurity Greens function using Hubbard-I"""

        # Test all a parameters before solutions
        print Parameters.check(self.__dict__,self.Required,self.Optional)
       	#Solver_Base.Solve(self,is_last_iteration,Iteration_Number,Test_Convergence)
       
        if self.Converged :
            MPI.report("Solver %(Name)s has already converted: SKIPPING"%self.__dict__)
            return

        self.__save_eal('eal.dat',Iteration_Number)

        MPI.report( "Starting Fortran solver %(Name)s"%self.__dict__)

        self.Sigma_Old <<= self.Sigma
        self.G_Old <<= self.G

        # call the fortran solver:
        temp = 1.0/self.Beta
        gf,tail,self.atocc,self.atmag = gf_hi_fullu(e0f=self.ealmat, ur=self.ur, umn=self.umn, ujmn=self.ujmn, 
                                                    zmsb=self.zmsb, nmom=self.Nmoments, ns=self.Nspin, temp=temp, verbosity = self.Verbosity)

        #self.sig = sigma_atomic_fullu(gf=self.gf,e0f=self.eal,zmsb=self.zmsb,ns=self.Nspin,nlm=self.Nlm)

        if (self.Verbosity==0):
            # No fortran output, so give basic results here
            MPI.report("Atomic occupancy in Hubbard I Solver  : %s"%self.atocc)
            MPI.report("Atomic magn. mom. in Hubbard I Solver : %s"%self.atmag)

        # transfer the data to the GF class:
        if (self.UseSpinOrbit): 
            nlmtot = self.Nlm*2         # only one block in this case!
        else:
            nlmtot = self.Nlm

        M={}
        isp=-1
        for a,al in self.GFStruct:
            isp+=1
            #M[a] = gf[isp*self.Nlm:(isp+1)*self.Nlm,isp*self.Nlm:(isp+1)*self.Nlm,:]
            M[a] = gf[isp*nlmtot:(isp+1)*nlmtot,isp*nlmtot:(isp+1)*nlmtot,:]
            for i in range(min(self.Nmoments,10)):
                self.tailtempl[a][i+1].array[:] = tail[i][isp*nlmtot:(isp+1)*nlmtot,isp*nlmtot:(isp+1)*nlmtot]
                 
        glist = lambda : [ GFBloc_ImFreq(Indices = al, Beta = self.Beta, NFreqMatsubara = self.Nmsb, Data=M[a], Tail=self.tailtempl[a]) 
                           for a,al in self.GFStruct]
        self.G = GF(NameList = self.a_list, BlockList = glist(),Copy=False)
            
        # Self energy:
        self.G0 <<= GF_Initializers.A_Omega_Plus_B(A=1,B=0.0)
        
        M = [ self.ealmat[isp*nlmtot:(isp+1)*nlmtot,isp*nlmtot:(isp+1)*nlmtot] for isp in range((2*self.Nlm)/nlmtot) ] 
        self.G0 -= M
        self.Sigma <<= self.G0 - inverse(self.G)

        # invert G0
        self.G0.invert()
       
        def test_distance(G1,G2, dist) :
            def f(G1,G2) : 
                print abs(G1._data.array - G2._data.array)
                dS = max(abs(G1._data.array - G2._data.array).flatten())  
                aS = max(abs(G1._data.array).flatten())
                return dS <= aS*dist
            return reduce(lambda x,y : x and y, [f(g1,g2) for (i1,g1),(i2,g2) in izip(G1,G2)])

        MPI.report("\nChecking Sigma for convergence...\nUsing tolerance %s"%Test_Convergence)
        self.Converged = test_distance(self.Sigma,self.Sigma_Old,Test_Convergence)

        if self.Converged :
            MPI.report("Solver HAS CONVERGED")
        else :
            MPI.report("Solver has not yet converged")

    def GF_realomega(self,ommin,ommax,N_om,broadening=0.01):
        """Calculates the GF and spectral function on the real axis."""

        delta_om = (ommax-ommin)/(1.0*(N_om-1))
            
        omega = numpy.zeros([N_om],numpy.complex_)
        Mesh = numpy.zeros([N_om],numpy.float_)

        for i in range(N_om): 
            omega[i] = ommin + delta_om * i + 1j * broadening
            Mesh[i] = ommin + delta_om * i

        temp = 1.0/self.Beta
        gf,tail,self.atocc,self.atmag = gf_hi_fullu(e0f=self.ealmat, ur=self.ur, umn=self.umn, ujmn=self.ujmn, 
                                                    zmsb=omega, nmom=self.Nmoments, ns=self.Nspin, temp=temp, verbosity = self.Verbosity)
        
        

        for sig in self.a_list: 
            for i in range(11): self.tailtempl[sig][i].array[:] *= 0.0

        # transfer the data to the GF class:
        if (self.UseSpinOrbit): 
            nlmtot = self.Nlm*2         # only one block in this case!
        else:
            nlmtot = self.Nlm

        M={}
        isp=-1
        for a,al in self.GFStruct:
            isp+=1
            #M[a] = gf[isp*self.Nlm:(isp+1)*self.Nlm,isp*self.Nlm:(isp+1)*self.Nlm,:]
            M[a] = gf[isp*nlmtot:(isp+1)*nlmtot,isp*nlmtot:(isp+1)*nlmtot,:]
            for i in range(min(self.Nmoments,10)):
                self.tailtempl[a][i+1].array[:] = tail[i][isp*nlmtot:(isp+1)*nlmtot,isp*nlmtot:(isp+1)*nlmtot]

        glist = lambda : [ GFBloc_ReFreq(Indices = al, Beta = self.Beta, MeshArray = Mesh, Data=M[a], Tail=self.tailtempl[a]) 
                           for a,al in self.GFStruct]       # Indices for the upfolded G
        self.G = GF(NameList = self.a_list, BlockList = glist(),Copy=False)

        # Self energy:
        self.G0 = self.G.copy()
        self.Sigma = self.G.copy()
        self.G0 <<= GF_Initializers.A_Omega_Plus_B(A=1,B=1j*broadening)
        
        M = [ self.ealmat[isp*nlmtot:(isp+1)*nlmtot,isp*nlmtot:(isp+1)*nlmtot] for isp in range((2*self.Nlm)/nlmtot) ] 
        self.G0 -= M
        self.Sigma <<= self.G0 - inverse(self.G)
        self.Sigma.Note='ReFreq'          # This is important for the put_Sigma routine!!!

        #sigmamat = sigma_atomic_fullu(gf=gf,e0f=self.ealmat,zmsb=omega,nlm=self.Nlm,ns=self.Nspin)

        #return omega,gf,sigmamat


        
    def __save_eal(self,Filename,it):
        f=open(Filename,'a')
        f.write('\neff. atomic levels, Iteration %s\n'%it)
        for i in range(self.Nlm*self.Nspin):
            for j in range(self.Nlm*self.Nspin):
                f.write("%12.8f  "%self.ealmat[i,j])
            f.write("\n")
        f.close()

