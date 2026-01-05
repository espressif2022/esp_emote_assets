idf_component_register()

# Function to get component path
function(get_component_path component_name output_var)
    # Get the exact component name
    idf_build_get_property(build_components BUILD_COMPONENTS)
    set(TARGET_COMPONENT "")
    foreach(COMPONENT ${build_components})
        if(COMPONENT MATCHES "${component_name}" OR COMPONENT MATCHES ".*__${component_name}")
            set(TARGET_COMPONENT ${COMPONENT})
            break()
        endif()
    endforeach()

    # Get the component path
    if(TARGET_COMPONENT STREQUAL "")
        message(FATAL_ERROR "Component '${component_name}' not found.")
    else()
        idf_component_get_property(COMPONENT_PATH ${TARGET_COMPONENT} COMPONENT_DIR)
        set(${output_var} ${COMPONENT_PATH} PARENT_SCOPE)
    endif()
endfunction()

# Function to validate partition size
function(validate_partition_size partition_name output_file)
    # Get actual partition size using ESP-IDF API
    partition_table_get_partition_info(partition_size "--partition-name ${partition_name}" "size")

    # Get file size
    if(EXISTS ${output_file})
        file(SIZE ${output_file} file_size)

        # Convert to KB for display
        math(EXPR partition_size_kb "${partition_size} / 1024")
        math(EXPR file_size_kb "${file_size} / 1024")
        math(EXPR recommended_size_kb "${file_size} / 1024 + 1")

        message(STATUS "Partition '${partition_name}' size validation:")
        message(STATUS "  File size: ${file_size_kb}K (${file_size} bytes)")
        message(STATUS "  Partition size: ${partition_size_kb}K (${partition_size} bytes)")

        if(file_size GREATER partition_size)
            message(FATAL_ERROR
                "ERROR: Binary size exceeds partition size!\n"
                "  File size: ${file_size_kb}K (${file_size} bytes)\n"
                "  Partition size: ${partition_size_kb}K (${partition_size} bytes)\n"
                "  Recommended partition size: ${recommended_size_kb}K\n"
                "  Please increase partition size in partitions.csv or reduce asset content.")
        else()
            message(STATUS "  ✓ Partition size validation passed")
        endif()
    else()
        message(WARNING "Output file not found for size validation: ${output_file}")
    endif()
endfunction()

# Function to build default assets based on configuration
# Usage: build_speaker_assets_bin(partition_name resolution output_path [name_length] [external_path])
function(build_speaker_assets_bin partition_name resolution output_path)
    get_component_path("esp_emote_assets" component_path)
    
    # Check if name_length is provided (4th argument)
    set(BUILD_ARGS
        "--resolution" "${resolution}"
        "--output" "${output_path}"
    )
    
    if(ARGC GREATER 3)
        list(APPEND BUILD_ARGS "--name_length" "${ARGV3}")
    endif()
    
    # Check if external_path is provided (5th argument)
    if(ARGC GREATER 4)
        list(APPEND BUILD_ARGS "--external_path" "${ARGV4}")
    endif()

    # Create custom command to build assets
    add_custom_command(
        OUTPUT ${output_path}
        COMMAND python ${component_path}/scripts/spiffs_assets/build_all.py ${BUILD_ARGS}
        DEPENDS
            ${component_path}/scripts/spiffs_assets/build_all.py
        COMMENT "Building emote_assets.bin based on configuration"
        VERBATIM
    )

    # Create target for generated assets
    add_custom_target(generated_speaker_assets ALL
        DEPENDS ${output_path}
    )

    # Add flash dependency
    add_dependencies(flash generated_speaker_assets)

    add_custom_command(
        OUTPUT ${output_path}.validated
        COMMAND ${CMAKE_COMMAND} -E echo "Validating speaker assets partition size..."
        COMMAND ${CMAKE_COMMAND} -E touch ${output_path}.validated
        DEPENDS ${output_path}
        COMMENT "Validating speaker assets partition size"
    )

    # Add validation target
    add_custom_target(validate_speaker_assets ALL
        DEPENDS ${output_path}.validated
    )

    # Validate partition size after build
    validate_partition_size(${partition_name} ${output_path})
endfunction()

# Function to build boot assets
# Usage: build_boot_assets_bin(partition_name boot_src output_path [name_length])
function(build_boot_assets_bin partition_name boot_src output_path)
    get_component_path("esp_emote_assets" component_path)

    set(BUILD_ARGS
        "--src" "${boot_src}"
        "--output" "${output_path}"
    )
    
    # Check if name_length is provided (4th argument)
    if(ARGC GREATER 3 AND NOT "${ARGV3}" STREQUAL "")
        list(APPEND BUILD_ARGS "--name_length" "${ARGV3}")
    endif()
    
    # Check if external_path is provided (5th argument)
    if(ARGC GREATER 4)
        list(APPEND BUILD_ARGS "--external_path" "${ARGV4}")
    endif()

    # Create custom command to build assets
    add_custom_command(
        OUTPUT ${output_path}
        COMMAND python ${component_path}/scripts/spiffs_assets/build_boot.py ${BUILD_ARGS}
        DEPENDS
            ${component_path}/scripts/spiffs_assets/build_boot.py
        COMMENT "Building boot_assets.bin based on configuration"
        VERBATIM
    )

    # Create target for generated assets
    add_custom_target(generated_boot_assets ALL
        DEPENDS ${output_path}
    )

    # Add flash dependency
    add_dependencies(flash generated_boot_assets)

    add_custom_command(
        OUTPUT ${output_path}.validated
        COMMAND ${CMAKE_COMMAND} -E echo "Validating boot assets partition size..."
        COMMAND ${CMAKE_COMMAND} -E touch ${output_path}.validated
        DEPENDS ${output_path}
        COMMENT "Validating boot assets partition size"
    )

    # Add validation target
    add_custom_target(validate_boot_assets ALL
        DEPENDS ${output_path}.validated
    )

    # Validate partition size after build
    validate_partition_size(${partition_name} ${output_path})
endfunction()
