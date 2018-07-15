
#ifndef FIR_H_
#define FIR_H_
#include "attribute.h"
#include "define.h"
SC_MODULE (fir) {
	public:
	sc_in_clk clk;
	sc_in<bool> rst;
	sc_in<sc_uint<8> > in_data;
	sc_in<sc_int<8> > coeff[FILTER_TAPS] ;
	sc_out< sc_uint<24> > filter_output ;
	void fir_main ( void );
	sc_uint<24> filter(sc_uint<8> *, sc_int<8> *);
	SC_CTOR (fir) {
	   SC_CTHREAD (fir_main, clk.pos() );
	   reset_signal_is(rst, false) ;
	   sensitive << clk.pos();
	}
	~fir() {}
};
#endif

