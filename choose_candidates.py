#!/usr/bin/env python3
import sys, os, getopt

candidates = []

def usage():
    print('This program reads ./[module_name]_info.csv and get Pareto-optimal designs from it. Pareto-optimal means that no other designs have fewer resource usage( fewer LAB AND fewer RAM AND fewer DSP blocks), lower latency and also lower power consumption. The Pareto-optimal designs will be write into the file ./[module_name]_candidate_designs.csv. To run the program for module "aes", please enter:')
    print('\t./choose_candidates.py aes')

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
        
    ChooseCandidates(module_name)
    
def ChooseCandidates(module_name):
    designs = open(module_name+'_info.csv').read().splitlines()[1:]
    designs_split = [ a.split(',') for a in designs ]
    
    # 0 - index, 1 - ALMs, 2 - latency, 5 - LABs, 6 - RAM blocks, 7 - DSP blocks, 8 - u0 power(mW), 9 - total power(mW)
    choose_list = [ (int(a[0]),int(a[2]),int(a[5]),int(a[6]),int(a[7]),float(a[8])) for a in designs_split ]
    check_list = [ (int(a[2]),int(a[5]),int(a[6]),int(a[7]),float(a[8])) for a in designs_split ]
    check_cand = []
    # search Pareto-optimal designs - can be done in O(n), O(n^2) here just for convenience, n is small(~30)
    for i in range(len(choose_list)):
        flag = 1
        for j in range(len(choose_list)):
            if (choose_list[i][1] >= choose_list[j][1]) and (choose_list[i][2] >= choose_list[j][2]) and (choose_list[i][3] >= choose_list[j][3]) and (choose_list[i][4] >= choose_list[j][4]) and (choose_list[i][5] > choose_list[j][5]):
                flag = 0
                break
        
        if (flag == 1) and (check_list[i] not in check_cand):
            candidates.append(choose_list[i])
            check_cand.append(check_list[i])
            
    # write to [module_name]_candidate_designs.csv
    cand_file = open(module_name+'_candidate_designs.csv','w')
    cand_file.write('index, latency, LABs, RAM blocks, DSP blocks, power (mW)\n')
    for candidate in candidates:
        for param in candidate:
            cand_file.write(str(param)+',')
         
        cand_file.write('\n')
        
    cand_file.close()
   
if __name__ == "__main__":
	main(sys.argv[1:])   