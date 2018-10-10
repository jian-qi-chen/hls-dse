#!/usr/bin/env python3
import sys, getopt, re, os, random, heapq, time, math
from numpy.random import choice 
import matplotlib.pyplot as plt

## parameters for HLS_DSE ##
HLS_POP = 30 #population of the pool
HLS_ALPHA = [0.33,0.85,0.075,0.075] #coefficient of area
HLS_BETA = [0.33,0.075,0.85,0.075] #coefficient of latency
HLS_GAMMA = [0.33,0.075,0.075,0.85] #coefficient of power, cost_function = HLS_ALPHA * area + HLS_BETA * latency + HLS_GAMMA * power
HLS_GEN_LIMIT = 3 #continue searching until not getting better results for HLS_GEN_LIMIT consecutive generations

## area and power parameters for CycloneV components ##
RAM1K_AREA = 2 #1K bits of RAM consume about 2 ALUTs' area
DSP9_AREA = 13 # 9 bit multiplier use 1/3 DSP block which is 13 ALUTs' area
DSP18_AREA = 20 # 18 bit multiplier use 1/2 DSP block
DSP27_AREA = 40 # 27 bit multiplier use 1 DSP block

ALUT_PWR = 0.00326 # 1 ALUT consumes 0.00326 mW
REG_PWR = 0.00238 # 1 Register(FF) consumes 0.00238mW
RAM10K_PWR = 0.473 # 1 M10K block, including 10K bits
DSP9_PWR = 0.255
DSP18_PWR = 0.526
DSP27_PWR = 1.134

src_name=['./fir/fir.cpp','./fir/fir.h'] #list of source file names
array_flg = 1 #enable array detection
array_ro_flg = 1
func_flg = 1
unroll_flg = 1 #unroll and folding flag

#table of all attributes
attr_val_table = {'array':['RAM','REG','EXPAND, array_index=const'],'array_ro':['RAM','REG','EXPAND, array_index=const','ROM','LOGIC'],'func':['inline','goto'],'unroll_folding':['unroll_times=0','unroll_times=all','folding=1'],'empty':['no_attr']}

attr_count = 0
attr_val = []  #list of attribute value for attrbute i is stored in attr_val[i] e.g. assume attr0 is array, then attr_val[0]=['RAM','REG']
attr_name = [] #list of attribute names corresponding to attr_val.
attr_num_list = [] #number of choice for each attribute

solution_list = [] #store all indices of solutions whose thermal map is generated (synthsized and simulated)
solution_attr_val_list = {} #store all the lists of attrbute values for each design in solution_list, e.g. for the 5th design: 5:[0,1,0,...,2]
area_list = [] #list of number of ALMs from quartus report. The area_list[x] is the area of solution_list[x] th design
latency_list = [] #list of latency index given by CWB. The latency_list[x] is the latency of solution_list[x] th design
hash_list = [] #list of thermal map hashes. The hash_list[x] is the hash of solution_list[x] th design
cost_list = [] #store all known cost. e.g. cost of 0th and 5th design is 10, and hamming distance between them is 12, then if (10,(0,5),12) exist, and there is no (10,(5,0),12). need search twice for a design pair. We use min heap to manage this. 

OFFSET = 311 #degrees subtracted firstly from kelvin temperature in image. Used in thermal_map_analyzer.py when generating hashes
SCALAR = 300 # pixel value(0-255) = (tmep_k - OFFSET) * SCALAR
cycle_period = 2000 # cycle period for HLS '2000' means 20ns (4000 - 25MHz, 2000 - 50MHz, 1333 - 75MHz, 1000 - 100MHz, 667 - 150MHz, 500 - 200MHz)

def main(argv): 
	global src_name
	global array_flg
	global func_flg
	global unroll_flg
	global cycle_period
	
	os.system('mkdir -p output_files attr_headers hls')
	os.system('mkdir -p SOFs')
	os.system('rm -f ./output_files/log.txt ./output_files/error.txt')
	logfile = open('./output_files/log.txt','w')
	logfile.write('Starting at '+time.strftime("%a,%d %b %Y %H:%M:%S", time.localtime())+'\n')
	logfile.close()
	start = time.time()
	
	try:
		opts, args = getopt.getopt(argv,"hn:f:",["help"])
	except getopt.GetoptError:
		sys.exit(2)
		
	for opt, arg in opts: #handle arguments
		if opt in ("-h","--help"):
			sys.exit()
		elif opt == "-n":
			if arg == "array":
				array_flg = 0
				array_ro_flg = 0
			elif arg == "func":
				func_flg = 0
			elif arg == "unroll":
				unroll_flg = 0
			elif arg == "array_ro":
				array_ro_flg = 0
			else:
				sys.exit(2)
		elif opt == "-f":
			cycle_period = int(arg)   
		
	for arg in args:
		src_name.append(arg)

	### HLS DSE ###	
#	add_attributes()
#	write_attr_list('./output_files/attr_list.txt')
#	if input('Would you like to edit attribute list ? (enter 1 or 0,1=yes,0=no):'):
#		tmp = input('Please edit ./output_files/attr_list.txt, enter any number when you are done.')
#		read_attr_list('./output_files/attr_list.txt')
	read_attr_list('./output_files/attr_list.txt')
	
	(solution_list,solution_attr_val_list,area_latency_power_list) = HLS_DSE()
	(solution_list,solution_attr_val_list,area_latency_power_list) = ReadHLSResults('./output_files/HLS_DSE_results.csv')
	ref_designs = HLS_DSE_ResultAnalysis( solution_list, solution_attr_val_list, area_latency_power_list )

	### Read Reference Designs ###
#	ref_designs = ReadRefDesigns(['./output_files/HLS_pareto_optimal_attr_indices.txt','./output_files/HLS_good_design_indices.txt'], 100)
	
	end = time.time()
#	logfile = open('./output_files/log.txt','a+')
#	logfile.write('\nWhole flow finished at '+time.strftime("%a,%d %b %Y %H:%M:%S", time.localtime())+', the total runing time is '+str(int(end-start)/3600)+' hours '+str((int(end-start)%3600)/60)+' minutes '+str(int(end-start)%60)+' seconds\n')
#	logfile.close()


#get single index of design, index_list = index of all attr in a list 
#suppose array={ram,reg}, unroll={0,1,all}
#if we have attr list ['ram'(1),'reg'(0),'all'(3),'2'(1)], index = 1+3*3+0*3*3+1*3*3*2 = 28
def get_index(index_list):
	global attr_num_list
	a_num = list(attr_num_list)
	a_num.append(1)
	index = 0
	total_num = 1
	
	for i in reversed(range(len(index_list))):
		total_num = total_num * a_num[i+1]
		index = index + index_list[i] * total_num
	
	return index
	
# the reverse operation of get_index: when the index is known, return the indices of every attribute.
# For example array={ram,reg}, unroll={0,1,all}, the attribute list is (array,array,unroll,unroll),we have index = 28
# 28/(2*3*3) = 1...10
# 10/(3*3)   = 0...10
# 10/3       = 3...1
# 1/1        = 1
# so attribute list is [1,0,3,1]
def get_index_list(index):
	global attr_num_list
	a_num = list(attr_num_list)
	a_num.append(1)
	index_list = [ 0 for i in range( len(attr_num_list) ) ]
	#build total_num list
	total_num =  [ 1 for i in range( len(attr_num_list)+1 ) ]
	for i in reversed(range(len(attr_num_list))):
		total_num[i] = total_num[i+1] * a_num[i+1] 
	
	reminder = index
	for i in range(len(attr_num_list)):
		index_list[i] = int( int(reminder)/int(total_num[i]) )
		reminder = int(reminder)%int(total_num[i])
	
	return index_list
		
	
def add_attributes():
	global src_name
	global array_flg
	global array_ro_flg
	global func_flg
	global unroll_flg
	global attr_name
	global attr_val
	global attr_count
	global attr_val_table
	global attr_num_list
	
	logfile = open('./output_files/log.txt','a+')
	os.system('rm -f ./hls/*')
	os.system('mkdir -p hls')
	os.system('cp ./fir/define.h ./hls/')
	for src in src_name:
		os.system('cp '+src+' ./hls/')
		
	#### add pragma to source code #### can escape using "\* $ *\". e.g. for(i=0; i<10; i++ /*$*/);   array[10]/*$*/;   function(x,y,z/*$*/){}

	if array_flg:
		arr_name = [] # array names for those arrays may be read only
		arr_attr_index = [] # which attribute correspond to this array
		
	if func_flg:
		func_name = [] # function names
		func_attr_index = [] # attribute index corresponding to this function

	content_all = ''	
	for file_name in os.listdir('./hls'):
		file = open('hls/'+file_name,'r')
		content = file.read()
		
		content_real =  re.sub(r'\n[ \t\r\n]*\n','\n', re.sub(r'[ \t]*(//(?![ \t]*\bCyber\b).*?\n|/\*(?![ \t]*\bCyber\b)[^$]*?\*/)','',content) ) # remove comments except /*$*/ and /* Cyber xxx */ and //Cyber xxx
	#	content_real = content
		content_all = content_all+'\n'+content_real
		content_l = re.split(r';|\)\s*?\{',content_real)

		file.close()
		
		## add pragma for 'array' phase 1 ##
		if array_flg:
			target_lines_arr = [] # lines contain array declaration
			for i in range(len(content_l)):
				tmp = re.findall(r'^[^=\+\-/#]*?(?:\bint\b|\bchar\b|\bfloat\b|\bdouble\b|\bsc_int\b|\bsc_uint\b|\bsc_fixed\b|\bsc_ufixed\b)[^=\+\-]+?\[[^\[\]]*\][^$\)/]*$',content_l[i]) #regex finds "(int|float|double|char|sc_xxx)xxxx[xxxx]xxx ;"
				if len(tmp) != 0:
					# make sure tmp[0] is not I/O
					if not (re.search(r'sc_(in|out)\b',tmp[0]) or re.search(r'(\bin\b|\bout\b)[\s\t]+(\bter|\bvar)',tmp[0]) ):
						if re.search(r'=',tmp[0]): 
							if re.search(r'\bint\b',tmp[0]):
								array_name = re.findall(r'\w+',re.findall(r'(?<=\bint\b)\s*\w+',tmp[0])[0])[0]
							elif re.search(r'\bfloat\b',tmp[0]):
								array_name = re.findall(r'\w+',re.findall(r'(?<=\bfloat\b)\s*\w+',tmp[0])[0])[0]
							elif re.search(r'\bchar\b',tmp[0]):
								array_name = re.findall(r'\w+',re.findall(r'(?<=\bchar\b)\s*\w+',tmp[0])[0])[0]
							elif re.search(r'\bdouble\b',tmp[0]):
								array_name = re.findall(r'\w+',re.findall(r'(?<=\bdouble\b)\s*\w+',tmp[0])[0])[0]
							elif re.search(r'sc_.*>',tmp[0]):
								array_name = re.findall(r'\w+',re.findall(r'(?<=>)\s*\w+',tmp[0])[0])[0]
							else:
								print ('cannot find arrayname in'+tmp[0])
								logfile.write('Error: cannot find arrayname in'+tmp[0])
								logfile.close()
								sys.exit(1)
							
							arr_name.append(array_name)
							arr_attr_index.append( attr_count + len(target_lines_arr) )

						target_lines_arr.append(tmp[0])


			print( 'array:')
			print (target_lines_arr) #for debug
			
			for target_arr in target_lines_arr:
				add = "/* arrayCyber"+str(attr_count)+" array = ATTR"+str(attr_count)+", rw_port=RW8 */"
				content_real = content_real.replace(target_arr, target_arr+add)
				if content_real.count(target_arr) > 1: #same piece of code in different location, need to be modified manually 
					print ("Error: multiple location: pragma of attr"+str(attr_count)+" need to be modified in "+file_name)
					file = open(file_name,'w')
					file.write(content_real)
					file.close()
					logfile.write("Error: multiple location: pragma of attr"+str(attr_count)+" need to be modified in "+file_name+'\n')
					logfile.close()
					sys.exit(1)
				attr_val.append(attr_val_table['array'])
				attr_name.append('array')
				attr_count =  attr_count+1
			
		## add pragma for 'func' (function) phase 1 ##
		if func_flg:
			target_lines_func = re.findall(r'\r?\n[^=\+\-;\{\}\r\n/#]*?(?:\bvoid\b|\bint\b|\bchar\b|\bfloat\b|\bdouble\b|\bsc_int\b|\bsc_uint\b|\bsc_fixed\b|\bsc_ufixed\b)[\w<>:\s]+?\([^$;]*?\)\s*\{',content_real) # regex find " int xxx(xx){"
			
			print( 'func:')
			print( target_lines_func )#for debug
			
			for target_func in target_lines_func:
				if re.search('::',target_func):
					func_name.append( re.findall(r'(?<=::)\w+',target_func)[0] )
				else:
					func_name.append( re.findall(r'\w+',re.findall(r'w+\s*\(',target_func)[0])[0] )
				
				func_attr_index.append( attr_count + target_lines_func.index( target_func ) )
							
				add = "\n/* funcCyber"+str(attr_count)+" func=ATTR"+str(attr_count)+" */"
				content_real = content_real.replace(target_func, add+target_func)
				if content_real.count(target_func) > 1:
					print( "Error: multiple location: pragma of attr"+str(attr_count)+" need to be modified in "+file_name)
					file = open(file_name,'w')
					file.write(content_real)
					file.close()
					logfile.write("Error: multiple location: pragma of attr"+str(attr_count)+" need to be modified in "+file_name+'\n')
					logfile.close()
					sys.exit(1)
				attr_val.append(attr_val_table['func'])
				attr_name.append('func')
				attr_count = attr_count+1
		
		## add pragma for 'unroll_times' and 'folding' (for loop) ##
		target_lines_unroll = []
		#don't unroll for loops in headers, for loop may used to connect I/Os in headers
		match = re.search(r'\.cp{0,2}',file_name) # regex finds "x.c" & "x.cpp"
		if match and unroll_flg:
			tmp = re.findall(r'\r?\n[ \t]*for[^\r\n\$]*\([^\r\n\$]*;[^\r\n\$]*;[^\r\n\$]*\)',content_real) # regex finds "  for (xxx;xxx;xxx)"
			for key_word in tmp:
				target_lines_unroll.append(key_word)
				if len(re.findall(r'for',key_word)) > 1:  #no more than 1 "for" in a line in source code
					print( "Please add newline between two 'for' in "+file_name+": "+key_word)
					logfile.write("Please add newline between two 'for' in "+file_name+": "+key_word+'\n')
					logfile.close()
					sys.exit(1)	
		
			print( 'unroll:')
			print( target_lines_unroll )#for debug
			
			for target_unroll in target_lines_unroll:
				add = "\n/* unroll_foldingCyber"+str(attr_count)+" ATTR"+str(attr_count)+" */"
				content_real = content_real.replace(target_unroll, add+target_unroll)
				if content_real.count(target_unroll) > 1:
					print ("Error: multiple location: pragma of attr"+str(attr_count)+" need to be modified in "+file_name)
					file = open(file_name,'w')
					file.write(content_real)
					file.close()
					logfile.write("Error: multiple location: pragma of attr"+str(attr_count)+" need to be modified in "+file_name+'\n')
					logfile.close()
					sys.exit(1)
				attr_val.append(attr_val_table['unroll_folding'])
				attr_name.append('unroll_folding')
				attr_count = attr_count+1
		
		file = open('hls/'+file_name,'w')
		file.write(content_real+'\n')
		file.close()
		
	## add pragma for 'array' phase 2: check read only arrays ##
	if array_ro_flg:
		tmp = []
		for i in range(len(arr_name)):
			if len(re.findall(arr_name[i]+r'[^\=!<>;]*?\=[^\=][\s\S]*?;',content_all)) == 1: #find assignment operations
				attr_val[ arr_attr_index[i] ] = attr_val_table['array_ro']
				attr_name[ arr_attr_index[i] ] = 'array'
				tmp.append(arr_name[i])

		print( 'read only array:')
		print( tmp) #for debug

	## add pragma for 'func phase 2: check whether the function is main function ##
	if func_flg:
		tmp = []
		for i in range(len(func_name)):
			if re.search(r'SC_(CTHREAD|THREAD|METHOD)\s*\(\s*'+func_name[i],content_all):
				attr_val[ func_attr_index[i] ] = attr_val_table['empty']
				attr_name[ func_attr_index[i] ] = 'empty'
				
				print( 'main function of thread:')
				print( func_name[i]) #for debug
		
	attr_num_list = [ len(attr_val[i]) for i in range(len(attr_val)) ]
	logfile.write('total number of attributes = '+str(attr_count)+'\nAttribute names: '+str(attr_name)+'\nAttribute values: '+str(attr_val)+'\n')
	logfile.close()

def write_attr_list(attr_list):
	global attr_name
	global attr_val
	file = open(attr_list,'w')
	for i in range(len(attr_name)):
		file.write('ATTR'+str(i)+' ')
		file.write(attr_name[i]+' [')
		for j in range(len(attr_val[i])):
			file.write(attr_val[i][j])
			if j != len(attr_val[i])-1:
				file.write(';')
				
		file.write(']\n')
		
	file.close()
		
def read_attr_list(attr_list):
	global attr_name
	global attr_val
	global attr_num_list
	attr_name = []
	attr_val = []
	attr_num_list = []
	file = open(attr_list,'r')
	
	attributes = file.read().splitlines()
	file.close()
	
	attr_count = 0
	for attr_line in attributes:
		if not re.match(r'^\s*$',attr_line):
			attr_count = attr_count+1
			attr_name.append( attr_line.split(' ')[1] )
			attr_val.append( re.findall(r'(?<=\[).*(?=\])',attr_line)[0].split(';') )
			
	attr_num_list = [ len(attr_val[i]) for i in range(len(attr_val)) ]
	
	logfile = open('./output_files/log.txt','a+')
	logfile.write('\nUser changed the attribute list, here is the new list:\n')
	logfile.write('number of attributes:'+str(attr_count)+'\nattribute names:'+str(attr_name)+'\nattribute values:'+str(attr_val)+'\n')
	logfile.close()
	print( 'number of attributes:')
	print( attr_count)
	print( 'attribute names:')
	print( attr_name)
	print( 'attribute values:')
	print( attr_val)

def RunHLS(ind_list, new_index):
	global attr_name
	global attr_val
	logfile = open('./output_files/log.txt','a+')
	errorfile = open('./output_files/error.txt','a+')
	
	#write attribute.h
	file = open('./attr_headers/attribute'+str(new_index)+'.h','w')
	file.write('#ifndef ATTRIBUTE_H_\n')
	file.write('#define ATTRIBUTE_H_\n\n')
	
	for a in range(len(attr_name)):
		if attr_val[a][ind_list[a]] != 'no_attr':
			file.write('#define '+attr_name[a]+'Cyber'+str(a)+' Cyber\n')
			file.write('#define ATTR'+str(a)+' '+attr_val[a][ind_list[a]]+'\n')
			
	file.write('\n#endif\n')
	file.close()
	
	os.system('cp ./attr_headers/attribute'+str(new_index)+'.h ./hls/attribute.h')
	# high level synthesis
	os.chdir('hls')
	ret = os.system('scpars -lic_wait=30 fir.cpp')
	if ret != 0:
		logfile.write('scpars error in '+str(new_index)+' th design\n')
		errorfile.write('\n\n*** scpars error in '+str(new_index)+' th design ***\n')
		errorfile.write(open('scpars.sperr').read())
		os.chdir('..')
		return 1
		
	ret = os.system('timeout 20m bdltran -c'+str(cycle_period)+' -s -Zresource_fcnt=GENERATE -Zresource_mcnt=GENERATE -Zdup_reset=YES -tcio -EE -lb /eda/cwb/cyber_61/LINUX/packages/cycloneV.BLIB -lfl /eda/cwb/cyber_61/LINUX/packages/cycloneV.FLIB -lic_wait=30 fir.IFF')
	if ret != 0:
		logfile.write('bdltran error in '+str(new_index)+' th design\n')
		errorfile.write('\n\n*** bdltran error in '+str(new_index)+' th design ***\n')
		errorfile.write(open('fir.err').read())
		os.chdir('..')
		return 1
		
	os.system('veriloggen -lic_wait=30 fir_E.IFF')
	os.chdir('..')
	
	return 0
	

def HLS_DSE():
	global attr_name
	global attr_val
	global HLS_ALPHA, HLS_BETA
	
	os.system('rm -f ./output_files/HLS_DSE_results.csv ./output_files/HLS_DSE_result.png')
	os.system('rm -f ./output_files/HLS_pareto_optimal_attr_indices.txt ./output_files/HLS_good_design_indices.txt')
	
	def AddNewHLS(ind_list,new_index):
		# nonlocal solution_list,solution_attr_val_list,area_latency_power_list,new_solution_pool,new_area_pool,new_latency_pool,new_power_pool #only for python3
		if new_index in solution_list: #the new design is synthesized before
			new_solution_pool.append(new_index)
			sol_location = solution_list.index(new_index)
			new_area_pool.append(area_latency_power_list[sol_location][0])
			new_latency_pool.append(area_latency_power_list[sol_location][1])
			new_power_pool.append(area_latency_power_list[sol_location][2])
			
		else: #synthesize it now
			if RunHLS(ind_list,new_index): #run HLS here
				return 1 #get error during HLS
			
			results = open('./hls/fir.CSV').read().splitlines()[1]
			resultfile = open('./output_files/HLS_DSE_results.csv','a+')
			resultfile.write(str(new_index)+','+results+',')
			
			#find DSP, RAM, and total Area & Power
			mul9 = 0
			mul18 = 0
			mul27 = 0
			auto_fnct = open('./hls/fir-auto.FCNT').read()
			mult_content = re.findall(r'NAME\tmul\d+[\s\S]+AUTO',auto_fnct) #list contains info of multipliers
			for cur_mult in mult_content:
				mul_bw = int( re.findall(r'(?<=NAME\tmul)\d+',cur_mult)[0] ) #bitwidth
				mul_num = int( re.findall(r'(?<=LIMIT\t)\d+',cur_mult)[0] ) #number of multipliers
				if mul_bw <= 9:
					mul9 = mul9 + mul_num
				elif mul_bw <= 18:
					mul18 = mul18 + mul_num
				else:
					mul27 = mul27 + mul_num
					
			alut_count = int( results.split(',')[0] )
			reg_count = int( results.split(',')[3] )
			mem_bits_count = int( results.split(',')[19] )
			
			cur_area = mul9 * DSP9_AREA + mul18 * DSP18_AREA + mul27 * DSP27_AREA + alut_count + math.ceil(mem_bits_count/1000.0) * RAM1K_AREA # area in equivalent number of ALUTs
			cur_power = mul9 * DSP9_PWR + mul18 * DSP18_PWR + mul27 * DSP27_PWR + alut_count * ALUT_PWR + math.ceil(mem_bits_count/10000.0) * RAM10K_PWR # power (mW)
					
			tmp = (cur_area, int(results.split(',')[18]), cur_power, int(results.split(',')[4]), int(results.split(',')[5])) # area(ALUTs), latency, power(mW), MUX(multiplexer), DEC(decoder)
			
			resultfile.write(str(cur_area)+','+str(cur_power)+'\n')
			resultfile.close()
			
			new_solution_pool.append(new_index)
			new_area_pool.append(tmp[0])
			new_latency_pool.append(tmp[1])
			new_power_pool.append(tmp[2])
			area_latency_power_list.append(tmp)
			solution_list.append(new_index)
			solution_attr_val_list[new_index] = ind_list
			
		return 0 #add new design successfully
		#end of AddNewHLS()
	
	logfile = open('./output_files/log.txt','a+')
	resultfile = open('./output_files/HLS_DSE_results.csv','a+')
	os.system('mkdir -p attr_headers')
	os.system('rm -f attr_headers/*')
	
	solution_list = [] #store solution indices
	solution_attr_val_list = {} #index for each attribute for each solution
	area_latency_power_list = [] # e.g. (100,25,10.24,30,40) is append if area=100(equivalent ALUTs), latency=25, power=10.24mW, multiplexer=30, decoder=40 
	
	if len(HLS_ALPHA) != len(HLS_BETA):
		print( 'array HLS_ALPHA and HLS_BETA has to be the same length')
		logfile.write('array HLS_ALPHA and HLS_BETA has to be the same length.\n')
		logfile.close()
		sys.exit(1)
		
	tot = 1
	for j in range(len(attr_val)):
		tot = tot * len(attr_val[j])

	if HLS_POP > 0.1*tot:
		print( 'HLS_POP too large comparing to total number of designs, please adjust HLS_POP')
		sys.exit(1)
		
#	if HLS_POP < 30:
#		print ('HLS_POP should be at least 30')
#		sys.exit(1)
		
	start_HLS = time.time()
	logfile.write('\nStart HLS DSE (Phase 1)\n')
	print( 'total number of designs = '+str(tot))
	logfile.write('total number of designs = '+str(tot)+'\nPopulation of the pool is '+str(HLS_POP)+'\n')
	logfile.write(str(len(HLS_ALPHA))+' rounds will be run using different cost functions\n')
	logfile.close()
	
	resultfile.write('index,AREA,state,FU ,REG,MUX,DEC,pin_pair,net,max,min, ave,MISC,MEM,CP_delay,sim,Pmax,Pmin,Pave,Latency,BlockMemoryBit,DSP,calculated_area(in equivlent ALUTs),power(mW)\n')
	resultfile.close()
	
	round_count = 0
	area_max = 0
	latency_max = 0
	power_max = 0
	
	# run several times using different ALPHA and BETAs
	for i in range(len(HLS_ALPHA)):
		solution_pool = [] #store solution indices which are in the pool
		area_pool = [] # area of solutions in the pool
		latency_pool = [] #latency of solutions in the pool
		power_pool = [] #power of solutions in the pool
		new_solution_pool = [] #pool of the next generation
		new_area_pool = [] # areas of the next generation
		new_latency_pool = [] # latencies of the next generation
		new_power_pool = [] #power of solutions in the pool
		
		round_count = round_count + 1
		logfile = open('./output_files/log.txt','a+')
		logfile.write('\nStart HLS DSE round '+str(i)+': Cost Function = '+str(HLS_ALPHA[i])+' * area + '+str(HLS_BETA[i])+' * latency + '+str(HLS_GAMMA[i])+' * power\n')
		logfile.close()
		
		# generate first generation randomly
		for j in range(HLS_POP):
			while True:
				ind_list = []
				for k in range(len(attr_val)):
					attr_index = random.randint(0,len(attr_val[k])-1)
					ind_list.append(attr_index)
				
				i_index = get_index(ind_list)
				if not i_index in solution_pool:
					if not AddNewHLS(ind_list,i_index): #add new design here
						break

		solution_pool = new_solution_pool
		area_pool = new_area_pool
		latency_pool = new_latency_pool
		power_pool = new_power_pool
		
		if max(area_pool) > area_max:
			area_max = max(area_pool)
		if max(latency_pool) > latency_max:
			latency_max = max(latency_pool)
		if max(power_pool) > power_max:
			power_max = max(power_pool)
		
		gen_count = 0 #count how many consecutive generations that do not generate better design
		generation = 1 # real number of generation
		best_area_latency_power = (0,0,0) # record the area/latency/power of the design with least cost, in case we get lower cost because of larger max area/latency
		cost_min = 999
		
		logfile = open('./output_files/log.txt','a+')
		logfile.write('Generation 1 is ready.\n')
		logfile.close()
		
		while gen_count < HLS_GEN_LIMIT:
			# update cost (according to new max area/latency)
			cost_list = [ 0 for k in range(len(solution_pool))] # cost of solutions in the pool
			fitness_list = [ 0 for k in range(len(solution_pool))] # fitness = 1/cost
			for j in range(len(solution_pool)):
				cost_list[j] = HLS_ALPHA[i] * float(area_pool[j])/area_max + HLS_BETA[i] * float(latency_pool[j])/latency_max + HLS_GAMMA[i] * power_pool[j]/power_max
				fitness_list[j] = 1.0/cost_list[j]
			
			if min(cost_list)<cost_min:
				tmp_index = cost_list.index(min(cost_list))
				if (area_pool[tmp_index],latency_pool[tmp_index],power_pool[tmp_index]) != best_area_latency_power:
					best_area_latency_power = (area_pool[tmp_index],latency_pool[tmp_index],power_pool[tmp_index])
					cost_min = min(cost_list)
					gen_count = 0
				else:
					cost_min = min(cost_list)
					gen_count = gen_count + 1
			else:
				gen_count = gen_count + 1
				
			# selection, crossover & mutation
			new_solution_pool = [] #pool of the next generation
			new_area_pool = [] # areas of the next generation
			new_latency_pool = [] # latencies of the next generation
			fit_s = sum(fitness_list) #sum of fitness
			prob_list = [] # probability list, which is just normalized fitness
			for fitness in fitness_list:
				prob_list.append(fitness/fit_s)
				
			num_sol = 0
			
			#add new designs to the pool of the new generation
			while len(new_solution_pool)<0.75*HLS_POP:
				while True:
					parenta_loc = choice(len(prob_list),1,p=prob_list)[0] #using numpy.random, one of the parent
					parentb_loc = choice(len(prob_list),1,p=prob_list)[0] #the other parent
					if parenta_loc == parentb_loc:
						continue
					
					chromoa = solution_attr_val_list[ solution_pool[parenta_loc] ] #chromosome of parent A
					chromob = solution_attr_val_list[ solution_pool[parentb_loc] ] #chromosome of parent B
					
					# crossover
					crossover_pt = round(random.uniform(0.2,0.8)*len(attr_val)) #crossover point
					child1 = [] #attribute index list of child 1
					child2 = []
					for a in range(len(attr_val)):
						if a < crossover_pt :
							child1.append(chromoa[a])
							child2.append(chromob[a])
						else:
							child1.append(chromob[a])
							child2.append(chromoa[a])
							
					# mutation
					for a in range(3):
						if random.random()<0.07:
							m_index = random.randint(0,len(attr_val)-1)
							child1[m_index] = random.randint(0,len(attr_val[m_index])-1)

						if random.random()<0.07:
							m_index = random.randint(0,len(attr_val)-1)
							child2[m_index] = random.randint(0,len(attr_val[m_index])-1)
					
					child1_index = get_index(child1)
					child2_index = get_index(child2)
					
					if not ( (child1_index in new_solution_pool) and (child2_index in new_solution_pool) ):
						success1 = 0
						success2 = 0
						if not ((child1_index in new_solution_pool) or (child1_index in solution_pool)): # add child1
							if not AddNewHLS(child1,child1_index):
								success1 = 1
									
						if not ((child2_index in new_solution_pool) or (child2_index in solution_pool)): # add child2
							if not AddNewHLS(child2,child2_index):
								success2 = 1
						
						if (success1+success2) > 0:
							break
			
			# add old designs to the pool of the new generation
			while len(new_solution_pool)<HLS_POP:
				while True:
					new_loc = choice(len(prob_list),1,p=prob_list)[0]
					new_index = solution_pool[new_loc]
					if not new_index in new_solution_pool:
						break
				
				new_solution_pool.append( new_index )
				new_area_pool.append( area_pool[new_loc] )
				new_latency_pool.append( latency_pool[new_loc] )
				new_power_pool.append( power_pool[new_loc] )
				
			solution_pool = new_solution_pool
			area_pool = new_area_pool
			latency_pool = new_latency_pool
			power_pool = new_power_pool
			
			if max(area_pool) > area_max:
				area_max = max(area_pool)
			if max(latency_pool) > latency_max:
				latency_max = max(latency_pool)
			if max(power_pool) > power_max:
				power_max = max(power_pool)
			
			generation = generation+1
			logfile = open('./output_files/log.txt','a+')
			logfile.write('Generation '+str(generation)+' is ready.\n')
			logfile.close()
			
	end_HLS = time.time()
	logfile = open('./output_files/log.txt','a+')
	logfile.write('\nHLS_DSE finished at '+time.strftime("%a,%d %b %Y %H:%M:%S", time.localtime())+', Runing time of HLS_DSE is '+str(int(int(end_HLS-start_HLS)/3600))+' hours '+str(int((int(end_HLS-start_HLS)%3600)/60))+' minutes '+str(int(int(end_HLS-start_HLS)%60))+' seconds\n')
	logfile.write('Number of designs synthesized in HLS_DSE: '+str(len(solution_list))+'\n\n')
	logfile.close()
	
	return (solution_list,solution_attr_val_list,area_latency_power_list)
		
	
def HLS_DSE_ResultAnalysis( solution_list, solution_attr_val_list, area_latency_power_list ):
	# plot area-latency graph
	from mpl_toolkits.mplot3d import Axes3D
	area_plot_x = []
	latency_plot_y = []
	power_plot_z = []
	area_latency_power_list_real = [] #area_latency_power_list has (area, latency, power, MUX, DEC), while area_latency_power_list_real only has (area, latency, power)
	for area_latency_power in area_latency_power_list:
		area_plot_x.append(area_latency_power[0])
		latency_plot_y.append(area_latency_power[1])
		power_plot_z.append(area_latency_power[2])
		area_latency_power_list_real.append((area_latency_power[0], area_latency_power[1], area_latency_power[2]))
		
	# get Pareto-optimal designs
	(area_to_x,latency_to_y,power_to_z) = FindTradeOff3D( area_plot_x, 0, latency_plot_y, 0, power_plot_z, 0 )
	
	fig = plt.figure(3)
	ax = fig.add_subplot(111,projection='3d')
	ax.set_xlabel('Area [ALUTs]')
	ax.set_ylabel('Latency [clock cycle]')
	ax.set_zlabel('Power [mW]')
	ax.scatter(area_plot_x, latency_plot_y, power_plot_z, c='b')
	ax.scatter(area_to_x, latency_to_y, power_to_z, c='r')
	
	logfile = open('./output_files/log.txt','a+')
	logfile.write('area vs. latency graph is generated at ./output_files/HLS_DSE_result.png\n')
	
	# write pareto-optimal attribute indices
	po_attr_val_list = []
	file = open('./output_files/HLS_pareto_optimal_attr_indices.txt','w')
	for i in range(len(area_to_x)):
		to_loc = area_latency_power_list_real.index((area_to_x[i],latency_to_y[i],power_to_z[i])) #location of pareto-optimal design
		file.write(str(solution_list[to_loc])+' '+str( solution_attr_val_list[ solution_list[to_loc] ] ).replace(' ','')+'\n')
		po_attr_val_list.append( solution_attr_val_list[ solution_list[to_loc] ] )
		
	file.close()
	
	# get designs with small cost, which may be the real pareto-optimal designs after logic synthesis
	area_max = max(area_plot_x)
	latency_max = max(latency_plot_y)
	
	if len(HLS_ALPHA) != len(HLS_BETA):
		print( 'HLS_ALPHA and HLS_BETA should have the same length')
		sys.exit(1)
		
#	good_area_latency = [] # store (area,latency,MUX,DEC) of low cost designs
#	good_attr_val_list = [] # attribute value list (in indices) of low cost designs
#	good_loc = [] #location of "good designs"(low cost designs) in solution_list
#	area_good_x = []
#	latency_good_y = []
#	for i in range(len(HLS_ALPHA)):
#		cost = []
#		for j in range(len(solution_list)):
#			current_cost = HLS_ALPHA[i] * float(area_plot_x[j]) + HLS_BETA[i] * float(latency_plot_y[j])
#			cost.append(current_cost)
#		
#		cost_min = min(cost)
#		cost_min_loc = cost.index(cost_min)
#		
#		tmp = []
#		for j in range(len(solution_list)):
#			if cost[j] < cost_min * 2.0: #within 100% cost overhead
#				tmp.append(j)
#				
#		for loc in tmp:
#			if not area_latency_power_list[loc] in good_area_latency:
#				good_area_latency.append( area_latency_power_list[loc] )
#				good_attr_val_list.append( solution_attr_val_list[ solution_list[loc] ] )
#				good_loc.append(loc)
#				area_good_x.append( area_plot_x[loc] )
#				latency_good_y.append( latency_plot_y[loc] )
				
	plt.savefig('./output_files/HLS_DSE_result.png', dpi=300)
	plt.show()
	
	# write "good designs" attribute indices
#	file_g = open('./output_files/HLS_good_design_indices.txt','w')
#	for i in range(len(good_loc)):
#		file_g.write(str(solution_list[good_loc[i]])+' '+str( good_attr_val_list[i] ).replace(' ','')+'\n')
#		
#	file_g.close()
	
	return po_attr_val_list 
	
	
# FindTradeOff return all designs on the trade-off curve. Data for x axis is the x_data, which is a list of float data type
# same way for the y data. x_type/y_type/z_type can be either 0 or 1. 0 means the smaller the better, 1 means the larger the better.
# (x_to, y_to) is the trade-off curve.
def FindTradeOff3D( x_data, x_type, y_data, y_type, z_data, z_type):
	x_to = []
	y_to = []
	z_to = []
	rm_flg = 0
	
	def Compare(x_data1, x_data2, y_data1, y_data2, z_data1, z_data2):
		if x_type == 0 and y_type == 0 and z_type == 0:
			return ( x_data1 >= x_data2 and y_data1 >= y_data2 and z_data1 >= z_data2 )
		elif x_type == 0 and y_type == 0 and z_type == 1:
			return ( x_data1 >= x_data2 and y_data1 >= y_data2 and z_data1 <= z_data2 )
		elif x_type == 0 and y_type == 1 and z_type == 0:
			return ( x_data1 >= x_data2 and y_data1 <= y_data2 and z_data1 >= z_data2 )
		elif x_type == 0 and y_type == 1 and z_type == 1:
			return ( x_data1 >= x_data2 and y_data1 <= y_data2 and z_data1 <= z_data2 )
		elif x_type == 1 and y_type == 0 and z_type == 0:
			return ( x_data1 <= x_data2 and y_data1 >= y_data2 and z_data1 >= z_data2 )
		elif x_type == 1 and y_type == 0 and z_type == 1:
			return ( x_data1 <= x_data2 and y_data1 >= y_data2 and z_data1 <= z_data2 )
		elif x_type == 1 and y_type == 1 and z_type == 0:
			return ( x_data1 <= x_data2 and y_data1 <= y_data2 and z_data1 >= z_data2 )
		elif x_type == 1 and y_type == 1 and z_type == 1:
			return ( x_data1 <= x_data2 and y_data1 <= y_data2 and z_data1 <= z_data2 )
		else:
			print( 'x/y/z_type is invalid')
			return
	
	for i in range(0,len(x_data)):			
		# all designs recorded in x_to and y_to are filters, prevent designs worse than it to be added into x/y_to
		for j in range(0,len(x_to)): 
			if Compare(x_data[i],x_to[j],y_data[i],y_to[j],z_data[i],z_to[j]):
				rm_flg = 1
				break

		if rm_flg == 0:
			x_to.append(x_data[i])
			y_to.append(y_data[i])
			z_to.append(z_data[i])
			k = 0
			while k < (len(x_to) - 1):
				if Compare(x_to[k],x_data[i],y_to[k],y_data[i],z_to[k],z_data[i]):
					del x_to[k]
					del y_to[k]
					del z_to[k]
				else:
					k = k+1
			
		rm_flg = 0
		
	return (x_to, y_to, z_to)
	
def ReadHLSResults(file_name):
	solution_list = []
	solution_attr_val_list = {}
	area_latency_power_list = []
	results = open(file_name).read().splitlines()[1:]
	for design in results:
		data_list = design.split(',')
		solution_list.append( int(data_list[0]) )
		solution_attr_val_list[ int(data_list[0]) ] = get_index_list(int(data_list[0]))
		area_latency_power_list.append( (int(float(data_list[22])),int(data_list[19]),float(data_list[23])) )
		
	return (solution_list, solution_attr_val_list, area_latency_power_list)	

# read attribute value list in 'HLS_good_design_indices.txt' and 'HLS_pareto_optimal_attr_indices.txt' into a list
#file_name is an array of file name e.g. ['./output_files/HLS_pareto_optimal_attr_indices.txt','./output_files/HLS_good_design_indices.txt']; limit is the maximum number of designs it will read
def ReadRefDesigns(file_name, limit):
	ref_attr_val_list = []
	for file_n in file_name:
		file = open(file_n,'r')
		designs = file.read().splitlines()
		file.close()
		
		for j in range(len(designs)):
			if len( ref_attr_val_list ) > limit:
				break
				
			attr_vals =  map(int, re.findall('\[.*\]',designs[j])[0][1:-1].split(',') )
			if not attr_vals in ref_attr_val_list:
				ref_attr_val_list.append(attr_vals)
			
	return ref_attr_val_list

		
if __name__ == "__main__":
	main(sys.argv[1:])



