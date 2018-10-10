#!/usr/bin/env python3
import sys, os, getopt, re, math

def usage():
    print('This program run logic synthesis, placement & route, gate-level simulation, bitstream generation and power estimation for all verilog codes in ./hdl/. The names of the verilog files should be "[module_name]_E[number].v". A table of resource usage and power comsumption for every HDL design will be generated([module_name]_info.csv). To run the program for module "aes", please enter:')
    print('\t./logic_synthesis.py aes')

def main(argv):
    try:
        opts, args = getopt.getopt(argv,'h',['help'])
    except getopt.GetopError:
        usage()
        sys.exit(1)
        
    for opt, arg in opts:
        if opt in ('-h','--help'):
            usage()
            sys.exit(0)
        else:
            usage()
            sys.exit(2)
    
    if len(args) != 1:
        usage()
        sys.exit(2)
    else:
        module_name = args[0]
        
    LogicSynthesis(module_name)

def LogicSynthesis(module_name):
    result_file = open(module_name+'_info.csv','w')
    result_file.write('index,ALMs,latency,Registers,MemoryBits,LABs,RAM blocks,DSP blocks,u0 power(mW),total power(mW),max_frequency(MHz)\n')
    result_file.close()
    i = 0
    while os.path.isfile('./hdl/'+module_name+'_E'+str(i)+'.v'):
        os.system('cp ./hdl/'+module_name+'_E'+str(i)+'.v ./quartus/'+module_name+'_E.v')
        os.system('bash run_quartus.sh')
        WriteResults(module_name, i)
        i += 1
        
def WriteResults(module_name, index):
    result_file = open(module_name+'_info.csv','a')
    result_file.write(str(index)+',')
    
    hls_result_file = open('./hdl/HLS_info.csv','r')
    hls_result = hls_result_file.read().splitlines()
    hls_result_file.close()
    latency = hls_result[index+1].split(',')[19]
        
    fit_file = open('./quartus/output_files/one_module.fit.summary','r')
    fit_summary = fit_file.read()
    fit_file.close()

    ALM = re.findall(r'(?<=Logic utilization \(in ALMs\) : )\d*,?\d+',fit_summary)[0].replace(',','')
    register = re.findall(r'(?<=Total registers : )\d*,?\d+',fit_summary)[0].replace(',','')
    memory_bit = re.findall(r'(?<=Total block memory bits : )\d*,?\d+',fit_summary)[0].replace(',','')
    ram_block = re.findall(r'(?<=Total RAM Blocks : )\d*,?\d+',fit_summary)[0].replace(',','')
    dsp_block = re.findall(r'(?<=Total DSP Blocks : )\d*,?\d+',fit_summary)[0].replace(',','')
    
    LAB = str( math.ceil( int(ALM)/10 ) )
    
    power_file = open('./quartus/output_files/one_module.pow.rpt','r')
    power_rpt = power_file.read()
    power_file.close()
    
    u0_power = re.findall( r'\d+\.\d+' , re.findall(r';\s*\|'+module_name+r':u0\s*; \d+\.\d+ mW',power_rpt)[0] )[0]
    total_power = re.findall( r'\d+\.\d+' , re.findall(r'\+\n;\s*\|one_module\s*; \d+\.\d+ mW',power_rpt)[0] )[0]

    sta_file = open('./quartus/output_files/one_module.sta.rpt','r')
    sta_rpt = sta_file.read()
    sta_file.close()
    
    fmax = re.findall(r'\d+\.\d*(?= MHz)',re.findall(r'; Slow 1100mV 85C Model Fmax Summary.*\n.*\n.*\n.*\n.*\n',sta_rpt)[0])[0].replace(',','')
    
    result_file.write(ALM +','+ latency +','+ register +','+ memory_bit +','+ LAB +','+  ram_block +','+ dsp_block +','+ u0_power +','+ total_power +','+fmax+'\n')
    
    result_file.close()


if __name__ == "__main__":
	main(sys.argv[1:])