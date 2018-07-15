#include "attribute.h"
#include "fir.h"
#define MAX 255 
/* funcCyber2 func=ATTR2 */
void fir::fir_main ( void ) {
	sc_uint<24> filter_output_function;
	sc_uint<8> in_data_read;
	sc_int<8> coeff_read[FILTER_TAPS]/* arrayCyber0 array = ATTR0, rw_port=RW8 */;
	sc_uint<8> data_buffer[FILTER_TAPS]/* arrayCyber1 array = ATTR1, rw_port=RW8 */;
	int i,j;
/* unroll_foldingCyber4 ATTR4 */
	for(i=0;i<FILTER_TAPS-1;i++)
		data_buffer[i] = 0;
	wait();
	while (1){		
		in_data_read = in_data.read();
/* unroll_foldingCyber5 ATTR5 */
		for(i=0;i<FILTER_TAPS;i++){
			coeff_read[i] = coeff[i].read();
		}
/* unroll_foldingCyber6 ATTR6 */
		for(j=FILTER_TAPS-1;j>0;j--){
			data_buffer[j] = data_buffer[j-1];
		}
		data_buffer[0] = in_data_read;
		filter_output_function = filter(data_buffer, coeff_read);
		filter_output.write(filter_output_function) ;
		wait();
	}
}
/* funcCyber3 func=ATTR3 */
sc_uint<24> fir::filter( sc_uint<8>  *ary, sc_int<8>  *coeff)
{
	sc_int<25> sop=0;
	sc_uint <16> filter_result ;
	int i ;
/* unroll_foldingCyber7 ATTR7 */
	for(i=0;i<FILTER_TAPS;i++){
		sop += sc_int<25>(coeff[i]) * ary[i];
	}
	if ( sop < 0 ){
		sop = 0 ;
	}
	filter_result = sc_uint<24>(sop);
	return filter_result;
}

