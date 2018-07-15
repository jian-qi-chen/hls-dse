// verilog_out version 6.89.1
// options:  veriloggen -lic_wait=30 fir_E.IFF
// bdlpars options:  -lic_wait=30 fir.cpp
// bdltran options:  -c1600 -s -Zresource_fcnt=GENERATE -Zresource_mcnt=GENERATE -Zdup_reset=YES -tcio -EE -lb /eda/cwb/cyber_61/LINUX/packages/cycloneV.BLIB -lfl /eda/cwb/cyber_61/LINUX/packages/cycloneV.FLIB -lic_wait=30 fir.IFF -tcio 
// timestamp_0: 20180710175728_27062_96552
// timestamp_5: 20180710175729_27085_36091
// timestamp_9: 20180710175731_27085_23219
// timestamp_C: 20180710175731_27085_54164
// timestamp_E: 20180710175732_27085_51514
// timestamp_V: 20180710175732_27098_15632

module fir ( clk ,rst ,in_data ,coeff_a00 ,coeff_a01 ,coeff_a02 ,coeff_a03 ,coeff_a04 ,
	coeff_a05 ,coeff_a06 ,coeff_a07 ,coeff_a08 ,filter_output );
input		clk ;	// line#=fir.h:8
input		rst ;	// line#=fir.h:9
input	[7:0]	in_data ;	// line#=fir.h:10
input	[7:0]	coeff_a00 ;	// line#=fir.h:11
input	[7:0]	coeff_a01 ;	// line#=fir.h:11
input	[7:0]	coeff_a02 ;	// line#=fir.h:11
input	[7:0]	coeff_a03 ;	// line#=fir.h:11
input	[7:0]	coeff_a04 ;	// line#=fir.h:11
input	[7:0]	coeff_a05 ;	// line#=fir.h:11
input	[7:0]	coeff_a06 ;	// line#=fir.h:11
input	[7:0]	coeff_a07 ;	// line#=fir.h:11
input	[7:0]	coeff_a08 ;	// line#=fir.h:11
output	[23:0]	filter_output ;	// line#=fir.h:12
wire		ST1_01d ;
wire		ST1_02d ;
wire		JF_01 ;

fir_fsm INST_fsm ( .clk(clk) ,.rst(rst) ,.ST1_02d(ST1_02d) ,.ST1_01d(ST1_01d) ,.JF_01(JF_01) );
fir_dat INST_dat ( .clk(clk) ,.rst(rst) ,.in_data(in_data) ,.coeff_a00(coeff_a00) ,
	.coeff_a01(coeff_a01) ,.coeff_a02(coeff_a02) ,.coeff_a03(coeff_a03) ,.coeff_a04(coeff_a04) ,
	.coeff_a05(coeff_a05) ,.coeff_a06(coeff_a06) ,.coeff_a07(coeff_a07) ,.coeff_a08(coeff_a08) ,
	.filter_output(filter_output) ,.ST1_02d(ST1_02d) ,.ST1_01d(ST1_01d) ,.JF_01(JF_01) );

endmodule

module fir_fsm ( clk ,rst ,ST1_02d ,ST1_01d ,JF_01 );
input		clk ;	// line#=fir.h:8
input		rst ;	// line#=fir.h:9
output		ST1_02d ;
output		ST1_01d ;
input		JF_01 ;
reg	B01_streg ;

parameter	ST1_01 = 1'h0 ;
parameter	ST1_02 = 1'h1 ;

assign	ST1_01d = ( ( B01_streg == ST1_01 ) ? 1'h1 : 1'h0 ) ;
assign	ST1_02d = ( ( B01_streg == ST1_02 ) ? 1'h1 : 1'h0 ) ;
always @ ( posedge clk )
	if ( !rst )
		B01_streg <= ST1_01 ;
	else
		case ( B01_streg )
		ST1_01 :
			B01_streg <= ST1_02 ;
		ST1_02 :
			if ( ( JF_01 != 1'h0 ) )
				B01_streg <= ST1_01 ;
			else
				B01_streg <= ST1_02 ;
		default :
			B01_streg <= ST1_01 ;
		endcase

endmodule

module fir_dat ( clk ,rst ,in_data ,coeff_a00 ,coeff_a01 ,coeff_a02 ,coeff_a03 ,
	coeff_a04 ,coeff_a05 ,coeff_a06 ,coeff_a07 ,coeff_a08 ,filter_output ,ST1_02d ,
	ST1_01d ,JF_01 );
input		clk ;	// line#=fir.h:8
input		rst ;	// line#=fir.h:9
input	[7:0]	in_data ;	// line#=fir.h:10
input	[7:0]	coeff_a00 ;	// line#=fir.h:11
input	[7:0]	coeff_a01 ;	// line#=fir.h:11
input	[7:0]	coeff_a02 ;	// line#=fir.h:11
input	[7:0]	coeff_a03 ;	// line#=fir.h:11
input	[7:0]	coeff_a04 ;	// line#=fir.h:11
input	[7:0]	coeff_a05 ;	// line#=fir.h:11
input	[7:0]	coeff_a06 ;	// line#=fir.h:11
input	[7:0]	coeff_a07 ;	// line#=fir.h:11
input	[7:0]	coeff_a08 ;	// line#=fir.h:11
output	[23:0]	filter_output ;	// line#=fir.h:12
input		ST1_02d ;
input		ST1_01d ;
output		JF_01 ;
wire		U_02 ;
wire	[3:0]	incr4s1i1 ;
wire	[3:0]	incr4s1ot ;
wire	[3:0]	lop4u_11i2 ;
wire	[3:0]	lop4u_11i1 ;
wire		lop4u_11ot ;
wire	[8:0]	mul12s1i2 ;
wire	[15:0]	mul12s1ot ;
wire	[15:0]	add28s_251i2 ;
wire	[24:0]	add28s_251i1 ;
wire	[24:0]	add28s_251ot ;
wire		JF_01 ;
wire		RG_data_buffer_en ;
wire		RG_data_buffer_1_en ;
wire		RG_data_buffer_2_en ;
wire		RG_data_buffer_3_en ;
wire		RG_data_buffer_4_en ;
wire		RG_data_buffer_5_en ;
wire		RG_data_buffer_6_en ;
wire		RG_data_buffer_7_en ;
wire		RG_data_buffer_8_en ;
wire		filter_output_r_en ;
wire		coeff_read_rg00_en ;
wire		coeff_read_rg01_en ;
wire		coeff_read_rg02_en ;
wire		coeff_read_rg03_en ;
wire		coeff_read_rg04_en ;
wire		coeff_read_rg05_en ;
wire		coeff_read_rg06_en ;
wire		coeff_read_rg07_en ;
wire		coeff_read_rg08_en ;
reg	[7:0]	coeff_read_rg08 ;	// line#=fir.cpp:8
reg	[7:0]	coeff_read_rg07 ;	// line#=fir.cpp:8
reg	[7:0]	coeff_read_rg06 ;	// line#=fir.cpp:8
reg	[7:0]	coeff_read_rg05 ;	// line#=fir.cpp:8
reg	[7:0]	coeff_read_rg04 ;	// line#=fir.cpp:8
reg	[7:0]	coeff_read_rg03 ;	// line#=fir.cpp:8
reg	[7:0]	coeff_read_rg02 ;	// line#=fir.cpp:8
reg	[7:0]	coeff_read_rg01 ;	// line#=fir.cpp:8
reg	[7:0]	coeff_read_rg00 ;	// line#=fir.cpp:8
reg	[7:0]	RG_data_buffer ;	// line#=fir.cpp:9
reg	[7:0]	RG_data_buffer_1 ;	// line#=fir.cpp:9
reg	[7:0]	RG_data_buffer_2 ;	// line#=fir.cpp:9
reg	[7:0]	RG_data_buffer_3 ;	// line#=fir.cpp:9
reg	[7:0]	RG_data_buffer_4 ;	// line#=fir.cpp:9
reg	[7:0]	RG_data_buffer_5 ;	// line#=fir.cpp:9
reg	[7:0]	RG_data_buffer_6 ;	// line#=fir.cpp:9
reg	[7:0]	RG_data_buffer_7 ;	// line#=fir.cpp:9
reg	[24:0]	RG_sop ;	// line#=fir.cpp:34
reg	[7:0]	RG_data_buffer_8 ;	// line#=fir.cpp:9
reg	[3:0]	RG_i ;	// line#=fir.cpp:36
reg	[23:0]	filter_output_r ;	// line#=fir.h:12
reg	[7:0]	mul12s1i1 ;
reg	[7:0]	M_21 ;
reg	[24:0]	RG_sop_t ;
reg	[3:0]	RG_i_t ;
reg	[15:0]	sop_11_t1 ;
reg	sop_11_t1_c1 ;

fir_incr4s INST_incr4s_1 ( .i1(incr4s1i1) ,.o1(incr4s1ot) );	// line#=fir.cpp:38
fir_lop4u_1 INST_lop4u_1_1 ( .i1(lop4u_11i1) ,.i2(lop4u_11i2) ,.o1(lop4u_11ot) );	// line#=fir.cpp:38
fir_mul12s INST_mul12s_1 ( .i1(mul12s1i1) ,.i2(mul12s1i2) ,.o1(mul12s1ot) );	// line#=fir.cpp:39
fir_add28s_25 INST_add28s_25_1 ( .i1(add28s_251i1) ,.i2(add28s_251i2) ,.o1(add28s_251ot) );	// line#=fir.cpp:39
assign	filter_output = filter_output_r ;	// line#=fir.h:12
assign	add28s_251i1 = RG_sop ;	// line#=fir.cpp:39
assign	add28s_251i2 = mul12s1ot ;	// line#=fir.cpp:39
always @ ( coeff_read_rg08 or coeff_read_rg07 or coeff_read_rg06 or coeff_read_rg05 or 
	coeff_read_rg04 or coeff_read_rg03 or coeff_read_rg02 or coeff_read_rg01 or 
	coeff_read_rg00 or RG_i )	// line#=fir.cpp:39
	case ( RG_i )
	4'h0 :
		mul12s1i1 = coeff_read_rg00 ;	// line#=fir.cpp:39
	4'h1 :
		mul12s1i1 = coeff_read_rg01 ;	// line#=fir.cpp:39
	4'h2 :
		mul12s1i1 = coeff_read_rg02 ;	// line#=fir.cpp:39
	4'h3 :
		mul12s1i1 = coeff_read_rg03 ;	// line#=fir.cpp:39
	4'h4 :
		mul12s1i1 = coeff_read_rg04 ;	// line#=fir.cpp:39
	4'h5 :
		mul12s1i1 = coeff_read_rg05 ;	// line#=fir.cpp:39
	4'h6 :
		mul12s1i1 = coeff_read_rg06 ;	// line#=fir.cpp:39
	4'h7 :
		mul12s1i1 = coeff_read_rg07 ;	// line#=fir.cpp:39
	4'h8 :
		mul12s1i1 = coeff_read_rg08 ;	// line#=fir.cpp:39
	default :
		mul12s1i1 = 8'hx ;
	endcase
always @ ( RG_data_buffer_7 or RG_data_buffer_6 or RG_data_buffer_5 or RG_data_buffer_4 or 
	RG_data_buffer_3 or RG_data_buffer_2 or RG_data_buffer_1 or RG_data_buffer or 
	RG_data_buffer_8 or RG_i )	// line#=fir.cpp:39
	case ( RG_i )
	4'h0 :
		M_21 = RG_data_buffer_8 ;	// line#=fir.cpp:39
	4'h1 :
		M_21 = RG_data_buffer ;	// line#=fir.cpp:39
	4'h2 :
		M_21 = RG_data_buffer_1 ;	// line#=fir.cpp:39
	4'h3 :
		M_21 = RG_data_buffer_2 ;	// line#=fir.cpp:39
	4'h4 :
		M_21 = RG_data_buffer_3 ;	// line#=fir.cpp:39
	4'h5 :
		M_21 = RG_data_buffer_4 ;	// line#=fir.cpp:39
	4'h6 :
		M_21 = RG_data_buffer_5 ;	// line#=fir.cpp:39
	4'h7 :
		M_21 = RG_data_buffer_6 ;	// line#=fir.cpp:39
	4'h8 :
		M_21 = RG_data_buffer_7 ;	// line#=fir.cpp:39
	default :
		M_21 = 8'hx ;
	endcase
assign	mul12s1i2 = { 1'h0 , M_21 } ;	// line#=fir.cpp:39
assign	lop4u_11i1 = incr4s1ot ;	// line#=fir.cpp:38
assign	lop4u_11i2 = 4'h9 ;	// line#=fir.cpp:38
assign	incr4s1i1 = RG_i ;	// line#=fir.cpp:38
assign	U_02 = ( ST1_02d & ( ~lop4u_11ot ) ) ;	// line#=fir.cpp:38
assign	RG_data_buffer_en = U_02 ;
always @ ( posedge clk )
	if ( !rst )
		RG_data_buffer <= 8'h00 ;
	else if ( RG_data_buffer_en )
		RG_data_buffer <= RG_data_buffer_8 ;
assign	RG_data_buffer_1_en = U_02 ;
always @ ( posedge clk )
	if ( !rst )
		RG_data_buffer_1 <= 8'h00 ;
	else if ( RG_data_buffer_1_en )
		RG_data_buffer_1 <= RG_data_buffer ;
assign	RG_data_buffer_2_en = U_02 ;
always @ ( posedge clk )
	if ( !rst )
		RG_data_buffer_2 <= 8'h00 ;
	else if ( RG_data_buffer_2_en )
		RG_data_buffer_2 <= RG_data_buffer_1 ;
assign	RG_data_buffer_3_en = U_02 ;
always @ ( posedge clk )
	if ( !rst )
		RG_data_buffer_3 <= 8'h00 ;
	else if ( RG_data_buffer_3_en )
		RG_data_buffer_3 <= RG_data_buffer_2 ;
assign	RG_data_buffer_4_en = U_02 ;
always @ ( posedge clk )
	if ( !rst )
		RG_data_buffer_4 <= 8'h00 ;
	else if ( RG_data_buffer_4_en )
		RG_data_buffer_4 <= RG_data_buffer_3 ;
assign	RG_data_buffer_5_en = U_02 ;
always @ ( posedge clk )
	if ( !rst )
		RG_data_buffer_5 <= 8'h00 ;
	else if ( RG_data_buffer_5_en )
		RG_data_buffer_5 <= RG_data_buffer_4 ;
assign	RG_data_buffer_6_en = U_02 ;
always @ ( posedge clk )
	if ( !rst )
		RG_data_buffer_6 <= 8'h00 ;
	else if ( RG_data_buffer_6_en )
		RG_data_buffer_6 <= RG_data_buffer_5 ;
assign	RG_data_buffer_7_en = U_02 ;
always @ ( posedge clk )
	if ( !rst )
		RG_data_buffer_7 <= 8'h00 ;
	else if ( RG_data_buffer_7_en )
		RG_data_buffer_7 <= RG_data_buffer_6 ;
always @ ( ST1_02d or add28s_251ot or ST1_01d )
	case ( { ST1_01d , ST1_02d } )
	2'b10 :
		RG_sop_t = 25'h0000000 ;	// line#=fir.cpp:34
	2'b01 :
		RG_sop_t = add28s_251ot ;
	default :
		RG_sop_t = 25'hx ;
	endcase
always @ ( posedge clk )
	RG_sop <= RG_sop_t ;	// line#=fir.cpp:34
assign	RG_data_buffer_8_en = ST1_01d ;
always @ ( posedge clk )	// line#=fir.cpp:14,25,28
	if ( RG_data_buffer_8_en )
		RG_data_buffer_8 <= in_data ;
always @ ( ST1_02d or incr4s1ot or ST1_01d )
	case ( { ST1_01d , ST1_02d } )
	2'b10 :
		RG_i_t = 4'h0 ;	// line#=fir.cpp:38
	2'b01 :
		RG_i_t = incr4s1ot ;	// line#=fir.cpp:38
	default :
		RG_i_t = 4'hx ;
	endcase
always @ ( posedge clk )
	RG_i <= RG_i_t ;	// line#=fir.cpp:38
always @ ( add28s_251ot )	// line#=fir.cpp:41
	begin
	sop_11_t1_c1 = ~add28s_251ot [24] ;
	case ( { add28s_251ot [24] , sop_11_t1_c1 } )
	2'b10 :
		sop_11_t1 = 16'h0000 ;	// line#=fir.cpp:42
	2'b01 :
		sop_11_t1 = add28s_251ot [15:0] ;
	default :
		sop_11_t1 = 16'hx ;
	endcase
	end
assign	JF_01 = ~lop4u_11ot ;	// line#=fir.cpp:38
assign	filter_output_r_en = U_02 ;
always @ ( posedge clk )	// line#=fir.cpp:27,28,44,45
	if ( filter_output_r_en )
		filter_output_r <= { 8'h00 , sop_11_t1 } ;
assign	coeff_read_rg00_en = ST1_01d ;
always @ ( posedge clk )	// line#=fir.cpp:14,19,28
	if ( !rst )
		coeff_read_rg00 <= 8'h00 ;
	else if ( coeff_read_rg00_en )
		coeff_read_rg00 <= coeff_a00 ;
assign	coeff_read_rg01_en = ST1_01d ;
always @ ( posedge clk )	// line#=fir.cpp:14,19,28
	if ( !rst )
		coeff_read_rg01 <= 8'h00 ;
	else if ( coeff_read_rg01_en )
		coeff_read_rg01 <= coeff_a01 ;
assign	coeff_read_rg02_en = ST1_01d ;
always @ ( posedge clk )	// line#=fir.cpp:14,19,28
	if ( !rst )
		coeff_read_rg02 <= 8'h00 ;
	else if ( coeff_read_rg02_en )
		coeff_read_rg02 <= coeff_a02 ;
assign	coeff_read_rg03_en = ST1_01d ;
always @ ( posedge clk )	// line#=fir.cpp:14,19,28
	if ( !rst )
		coeff_read_rg03 <= 8'h00 ;
	else if ( coeff_read_rg03_en )
		coeff_read_rg03 <= coeff_a03 ;
assign	coeff_read_rg04_en = ST1_01d ;
always @ ( posedge clk )	// line#=fir.cpp:14,19,28
	if ( !rst )
		coeff_read_rg04 <= 8'h00 ;
	else if ( coeff_read_rg04_en )
		coeff_read_rg04 <= coeff_a04 ;
assign	coeff_read_rg05_en = ST1_01d ;
always @ ( posedge clk )	// line#=fir.cpp:14,19,28
	if ( !rst )
		coeff_read_rg05 <= 8'h00 ;
	else if ( coeff_read_rg05_en )
		coeff_read_rg05 <= coeff_a05 ;
assign	coeff_read_rg06_en = ST1_01d ;
always @ ( posedge clk )	// line#=fir.cpp:14,19,28
	if ( !rst )
		coeff_read_rg06 <= 8'h00 ;
	else if ( coeff_read_rg06_en )
		coeff_read_rg06 <= coeff_a06 ;
assign	coeff_read_rg07_en = ST1_01d ;
always @ ( posedge clk )	// line#=fir.cpp:14,19,28
	if ( !rst )
		coeff_read_rg07 <= 8'h00 ;
	else if ( coeff_read_rg07_en )
		coeff_read_rg07 <= coeff_a07 ;
assign	coeff_read_rg08_en = ST1_01d ;
always @ ( posedge clk )	// line#=fir.cpp:14,19,28
	if ( !rst )
		coeff_read_rg08 <= 8'h00 ;
	else if ( coeff_read_rg08_en )
		coeff_read_rg08 <= coeff_a08 ;

endmodule

module fir_incr4s ( i1 ,o1 );
input	[3:0]	i1 ;
output	[3:0]	o1 ;

assign	o1 = ( i1 + 1'h1 ) ;

endmodule

module fir_lop4u_1 ( i1 ,i2 ,o1 );
input	[3:0]	i1 ;
input	[3:0]	i2 ;
output		o1 ;
wire		M_01 ;

assign	M_01 = ( i1 < i2 ) ;
assign	o1 = M_01 ;

endmodule

module fir_mul12s ( i1 ,i2 ,o1 );
input	[7:0]	i1 ;
input	[8:0]	i2 ;
output	[15:0]	o1 ;
wire	signed	[15:0]	so1 ;

assign	so1 = ( $signed( i1 ) * $signed( i2 ) ) ;
assign	o1 = $unsigned( so1 ) ;

endmodule

module fir_add28s_25 ( i1 ,i2 ,o1 );
input	[24:0]	i1 ;
input	[15:0]	i2 ;
output	[24:0]	o1 ;

assign	o1 = ( i1 + { { 9{ i2 [15] } } , i2 } ) ;

endmodule
