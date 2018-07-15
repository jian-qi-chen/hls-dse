module tb_fir(
	input clk,
	input rst,
	output reg [7:0] in_data
);
	//8 bit LFSR
	reg [7:0] lfsr;
	wire feedback;
	assign feedback = lfsr[7] ^ lfsr[5] ^ lfsr[4] ^ lfsr[3];
	
	always @(posedge clk or negedge rst)
	begin
		if (!rst)
		begin
			lfsr <= 8'hFF;
			in_data <= 0;
		end
		else
		begin
			lfsr <= {lfsr[6:0],feedback};
			in_data <= lfsr;
		end		
	end
	
endmodule	