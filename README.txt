This is an example of DSE for FIR filter (from S2CBench v2.2, systemC source code in ./fir/).
High-level synthesis tool: CyberWorkBench 6.1
logic synthesis, place & route, power analysis tool: Quartus Prime Standard 17.0
target device: CycloneV
HDL simulator: ModelSim - intel fpga starter edition 10.5b

4 steps to find Pareto-optimal designs (in terms of resource(LAB,RAM,DSP) usage, latecy and power) , the outputs of every step are inputs of its following steps.
1. Do HLS design space exploration based on genetic algorithm. 
   command:	./DSE.py
   outputs: ./output_files/attr_list.txt (if add_attributes() is called ), ./output_files/HLS_DSE_results.csv, etc.

2. Regenerate verilog codes for the good designs found during DSE.
   command:	./regenerate_HDL_from_results.py fir
   outputs: ./hdl/*.v, ./hdl/HLS_info.csv

3. Run logic synthesis, placement & routing, power analysis for good designs.
   command:	./logic_synthesis.py fir
   outputs: ./fir_info.csv, ( bitstream(.sof) file generated for every synthesized design, but not saved in this case)

4. Based on accurate resource usage and power(got from the previous step) and latency (got from HLS), choose Pareto-optimal designs.
   command:	./choose_candidates.py fir
   outputs: ./fir_candidate_designs.csv