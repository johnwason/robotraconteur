function(RR_SERVICE_TEST_ADD_TEST TARGET_NAME)

    cmake_parse_arguments(RR_ARG "" "" "SRC" ${ARGN})
    rr_test_add_executable(robotraconteur_test_${TARGET_NAME} SRC ${RR_ARG_SRC} DEPS robotraconteur_test_service_lib)
    target_include_directories(robotraconteur_test_${TARGET_NAME} PUBLIC ${CMAKE_CURRENT_BINARY_DIR})
    if(MSVC)
        target_compile_options(robotraconteur_test_${TARGET_NAME} PRIVATE "/bigobj")
    endif()
endfunction()

function(RR_SERVICE_TEST_ADD_EXE TARGET_NAME)
    cmake_parse_arguments(RR_ARG "" "" "SRC" ${ARGN})
    add_executable(robotraconteur_test_${TARGET_NAME} ${RR_ARG_SRC})
    target_link_libraries(robotraconteur_test_${TARGET_NAME} robotraconteur_test_service_lib)
    target_include_directories(robotraconteur_test_${TARGET_NAME} PUBLIC ${CMAKE_CURRENT_BINARY_DIR})
    if(MSVC)
        target_compile_options(robotraconteur_test_${TARGET_NAME} PRIVATE "/bigobj")
    endif()
    rr_set_test_target_dirs(robotraconteur_test_${TARGET_NAME} bin lib)
endfunction()

function(RR_SERVICE_TEST_ADD_LIB TARGET_NAME)
    cmake_parse_arguments(RR_ARG "" "" "SRC" ${ARGN})
    add_library(robotraconteur_test_${TARGET_NAME} STATIC ${RR_ARG_SRC})
    target_link_libraries(robotraconteur_test_${TARGET_NAME} PUBLIC RobotRaconteurCore robotraconteur_test_cpp_common
                                                                    robotraconteur_test_lfsr GTest::Main)
    target_include_directories(robotraconteur_test_${TARGET_NAME} PUBLIC ${CMAKE_CURRENT_BINARY_DIR})
    if(MSVC)
        target_compile_options(robotraconteur_test_${TARGET_NAME} PRIVATE "/bigobj")
    endif()
    rr_set_test_target_dirs(robotraconteur_test_${TARGET_NAME} bin lib)
endfunction()
