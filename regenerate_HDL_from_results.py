#!/usr/bin/env python3
import sys, os, re, DSE

max_design_num = 30
good_attr_val_list = []#designs selected
good_area_latency_list = []

def main(argv):
    global good_attr_val_list, good_area_latency_list
    DSE.read_attr_list('./output_files/attr_list.txt')
    (solution_list,solution_attr_val_list,area_latency_power_list) = DSE.ReadHLSResults('./output_files/HLS_DSE_results.csv')
    area_list = [ a[0] for a in area_latency_power_list ]
    latency_list = [ a[1] for a in area_latency_power_list ]
    power_list = [ a[2] for a in area_latency_power_list ]
    area_max = max(area_list)
    latency_max = max(latency_list)
    power_max = max(power_list)
    
    # get Pareto-optimal designs
    (area_po,latency_po,power_po) = DSE.FindTradeOff3D(area_list, 0, latency_list, 0, power_list, 0)

    for i in range(len(area_po)):
        cur_index = area_latency_power_list.index( (area_po[i],latency_po[i],power_po[i]) )
        good_attr_val_list.append( solution_attr_val_list[ solution_list[cur_index] ] )
        good_area_latency_list.append( area_latency_power_list[cur_index] )
        
    # get designs with small cost, except the Pareto-optimal designs
    good_attr_val_list += GetGoodDesigns(solution_list, solution_attr_val_list, area_latency_power_list, area_max, latency_max, power_max, max_design_num - len(good_attr_val_list))
    
    print(str(len(good_attr_val_list))+' designs will be high-level synthesized')
    
    os.system('mkdir -p hdl')
    result_file = open('./hdl/HLS_info.csv','w')
    result_file.write('index,AREA,state,FU,REG,MUX,DEC,pin_pair,net,max,min,ave,MISC,MEM,CP_delay,sim,Pmax,Pmin,Pave,Latency,BlockMemoryBit,DSP\n')
    result_file.close()
    
    for i in range(len(good_attr_val_list)):
        # run HLS
        DSE.RunHLS(good_attr_val_list[i],i)
        os.system('echo '+str(i)+',$(head -2 ./hls/*.CSV | tail -1) >> ./hdl/HLS_info.csv')
        os.system("mv ./hls/*.v ./hdl/$(cd hls && ls *.v | sed 's/.v//')"+str(i)+".v")

    
    
def GetGoodDesigns(solution_list, solution_attr_val_list, area_latency_power_list, area_max, latency_max, power_max, num):
    ret_attr_val_list = []
    cost_list = [ [], [], [] ]
    cost_list[0] = [ 0.33*a[0]/area_max + 0.33*a[1]/latency_max + 0.33*a[2]/power_max for a in area_latency_power_list]
    cost_list[1] = [ 0.9*a[0]/area_max + 0.05*a[1]/latency_max + 0.05*a[2]/power_max for a in area_latency_power_list]
    cost_list[2] = [ 0.05*a[0]/area_max + 0.9*a[1]/latency_max + 0.05*a[2]/power_max for a in area_latency_power_list]
    
    while num > 0 :
        cur_index = cost_list[num%3].index( min(cost_list[num%3]) )
        cost_list[num%3][cur_index] = 999

        if (solution_attr_val_list[solution_list[cur_index]] not in ret_attr_val_list) and (solution_attr_val_list[solution_list[cur_index]] not in good_attr_val_list) and (area_latency_power_list[cur_index] not in good_area_latency_list):
            ret_attr_val_list.append(solution_attr_val_list[solution_list[cur_index]])
            good_area_latency_list.append( area_latency_power_list[cur_index] )
            num = num-1
            
    return ret_attr_val_list

if __name__ == "__main__":
	main(sys.argv[1:])