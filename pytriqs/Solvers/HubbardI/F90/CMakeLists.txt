find_package(BuildF2pyModule)
BuildF2pyModule( triqs_HubbardI hubbard_I hubbard_I.pyf hubbard_I.f90)
install (FILES ${CMAKE_CURRENT_BINARY_DIR}/hubbard_I.so DESTINATION ${TRIQS_PYTHON_LIB_DEST}/Solvers/HubbardI)
execute_process(COMMAND ln -fs ${CMAKE_CURRENT_BINARY_DIR}/hubbard_I.so  ${CMAKE_CURRENT_BINARY_DIR}/.. )

