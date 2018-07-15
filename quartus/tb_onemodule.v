`timescale 1ns / 100ps
module tb_onemodule;
	reg clk = 0;
	reg rst = 0;
	reg rst_tb = 0;
	
	wire [23:0] filter_output;
	
	one_module one_0(.CLOCK_50(clk),
		.reset(rst),
		.reset_tb(rst_tb),
		.filter_output(filter_output)
	);
	
	always #10 clk = ~clk;
	
	initial begin
	#50
	rst = 0;
	rst_tb = 0;
	#40
	rst_tb = 1;
	#200
	rst = 1;
	#12000
	$stop;
	end
endmodule