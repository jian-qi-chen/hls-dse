#! /bin/bash
cd quartus
rm -rf ./db/ ./incremental_db/
rm -f ./output_files/*
rm -f ./simulation/*
# Analysis & Synthesis
quartus_map --read_settings_files=on --write_settings_files=off one_module -c one_module
# Fitter
quartus_fit --read_settings_files=on --write_settings_files=off one_module -c one_module
# Timing Analysis
quartus_sta one_module -c one_module
# EDA writer
quartus_eda --read_settings_files=on --write_settings_files=off one_module -c one_module
# generate .do file for modelsim
quartus_sh -t /eda/altera/quartus_17/quartus/common/tcl/internal/nativelink/qnativesim.tcl --no_gui one_module one_module

# run modelsim for gate-level simulation
cd ./simulation
vsim -c -do 'do one_module_run_msim_gate_verilog.do;quit -f'
cd ..

# bitstream generation
quartus_asm --read_settings_files=on --write_settings_files=off one_module -c one_module
# power estimation
quartus_pow --read_settings_files=off --write_settings_files=off one_module -c one_module

cd ..