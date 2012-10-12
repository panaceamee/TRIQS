/*******************************************************************************
 *
 * TRIQS: a Toolbox for Research in Interacting Quantum Systems
 *
 * Copyright (C) 2011 by O. Parcollet
 *
 * TRIQS is free software: you can redistribute it and/or modify it under the
 * terms of the GNU General Public License as published by the Free Software
 * Foundation, either version 3 of the License, or (at your option) any later
 * version.
 *
 * TRIQS is distributed in the hope that it will be useful, but WITHOUT ANY
 * WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
 * details.
 *
 * You should have received a copy of the GNU General Public License along with
 * TRIQS. If not, see <http://www.gnu.org/licenses/>.
 *
 ******************************************************************************/
#ifndef TRIQS_ARRAYS_ALL_H
#define TRIQS_ARRAYS_ALL_H

// First the lazy expression lib
#include <triqs/clef/core.hpp>

// The basic classes
#include <triqs/arrays/array.hpp>
#include <triqs/arrays/matrix.hpp>
#include <triqs/arrays/vector.hpp>

// Adaptation to lazy
#include <triqs/clef/adapters/array.hpp>

// Proto expression
#include <triqs/arrays/proto/array_algebra.hpp>
#include <triqs/arrays/proto/matrix_algebra.hpp>

//
//#include <triqs/arrays/functional/map.hpp>
#include <triqs/arrays/mapped_functions.hpp>

// HDF5 interface
#include <triqs/arrays/h5/simple_read_write.hpp>

// Linear algebra ?? Keep here ?
//#include <triqs/arrays/linalg/inverse.hpp>
//#include <triqs/arrays/linalg/determinant.hpp>

#endif

