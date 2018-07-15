module one_module(
	input     CLOCK_50,
	input     reset,
	input     reset_tb,
	output  [23:0]  filter_output
);

	wire  [7:0] in_data;
	wire  [7:0] coeff_a00;
	wire  [7:0] coeff_a01;
	wire  [7:0] coeff_a02;
	wire  [7:0] coeff_a03;
	wire  [7:0] coeff_a04;
	wire  [7:0] coeff_a05;
	wire  [7:0] coeff_a06;
	wire  [7:0] coeff_a07;
	wire  [7:0] coeff_a08;
	
	assign coeff_a00 = 9;
	assign coeff_a01 = 234;
	assign coeff_a02 = 30;
	assign coeff_a03 = 71;
	assign coeff_a04 = 102;
	assign coeff_a05 = 64;
	assign coeff_a06 = 28;
	assign coeff_a07 = 229;
	assign coeff_a08 = 2;

	fir u0(.clk(CLOCK_50),
		.rst(reset),
		.in_data(in_data),
		.coeff_a00(coeff_a00),
		.coeff_a01(coeff_a01),
		.coeff_a02(coeff_a02),
		.coeff_a03(coeff_a03),
		.coeff_a04(coeff_a04),
		.coeff_a05(coeff_a05),
		.coeff_a06(coeff_a06),
		.coeff_a07(coeff_a07),
		.coeff_a08(coeff_a08),
		.filter_output(filter_output)
	);
	
	tb_fir u1(.clk(CLOCK_50),
		.rst(reset_tb),
		.in_data(in_data)
	);
	
endmodule