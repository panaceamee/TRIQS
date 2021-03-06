.. index:: install_on_osx_lion

.. _install_on_osx_lion:
.. highlight:: bash

Installation on Mac OS X [Mountain Lion]
==============================================

Previous versions of Mac OS X are not supported.

On Mountain Lion, clang (llvm) is the default C++ compiler, 
instead of the obsolete gcc 4.2 or previous version.

NB: You can install triqs on previous OS X, but only if you install clang (via Apple) or gcc 4.7 (via macports).

Installation of the dependencies
________________________________

#. Install macports (from a binary)
#. Install XCode 4.3 (directly from the Mac store). In Preferences/Downloads, install "Command Line tools"
#. Install the **full** Enthought Python Distribution (EPD) (from a binary)
#. Download the `sources of boost <http://ipht.cea.fr/triqs/download/boost_src.tar.bz2>`_ (1.49) and untar them into a given directory ``BOOST_SRC``
#. Install cmake, git, gfortran, openmpi and fftw::

      sudo port install cmake git-core gcc46 openmpi fftw-3


TRIQS installation
__________________

#. Download the TRIQS sources::

      git clone git@github.com:TRIQS/TRIQS.git TRIQS_src

#. Generate a Makefile using cmake::

      cmake TRIQS_src -DCMAKE_Fortran_COMPILER=/opt/local/bin/gfortran-mp-4.6 \
          -DPYTHON_INTERPRETER=/Library/Frameworks/EPD64.framework/Versions/7.2/bin/python \
          -DBOOST_SOURCE_DIR=BOOST_SRC -DMPI_CXX_COMPILER=openmpic++  \
          -DCMAKE_COMPILER_IS_GNUCXX=1

#. Compile TRIQS, its tests and install it into INSTALL_DIR (default)::

      make -j4 && make test && make install 

#. If you use Wien2TRIQS, please complete the installation as described :ref:`here <wien2k_inst>`.

