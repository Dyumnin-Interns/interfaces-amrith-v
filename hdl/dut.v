//
// Generated by Bluespec Compiler (build d05342e3)
//
// On Tue Jan 10 11:46:54 IST 2023
//
//
// Ports:
// Name                         I/O  size props
// din_rdy                        O     1
// dout_value                     O     8 reg
// dout_rdy                       O     1 reg
// len_rdy                        O     1 const
// cfg_data_out                   O    32
// cfg_rdy                        O     1 const
// CLK                            I     1 clock
// RST_N                          I     1 reset
// din_value                      I     8
// len_value                      I     8
// cfg_address                    I     8
// cfg_data_in                    I    32
// cfg_op                         I     1
// din_en                         I     1
// len_en                         I     1
// dout_en                        I     1
// cfg_en                         I     1
//
// Combinational paths from inputs to outputs:
//   (cfg_address, cfg_op) -> cfg_data_out
//
//

`ifdef BSV_ASSIGNMENT_DELAY
`else
  `define BSV_ASSIGNMENT_DELAY
`endif

`ifdef BSV_POSITIVE_RESET
  `define BSV_RESET_VALUE 1'b1
  `define BSV_RESET_EDGE posedge
`else
  `define BSV_RESET_VALUE 1'b0
  `define BSV_RESET_EDGE negedge
`endif

module dut(CLK,
	   RST_N,

	   din_value,
	   din_en,
	   din_rdy,

	   dout_en,
	   dout_value,
	   dout_rdy,

	   len_value,
	   len_en,
	   len_rdy,

	   cfg_address,
	   cfg_data_in,
	   cfg_op,
	   cfg_en,
	   cfg_data_out,
	   cfg_rdy);
  input  CLK;
  input  RST_N;

  // action method din
  input  [7 : 0] din_value;
  input  din_en;
  output din_rdy;

  // actionvalue method dout
  input  dout_en;
  output [7 : 0] dout_value;
  output dout_rdy;

  // action method len
  input  [7 : 0] len_value;
  input  len_en;
  output len_rdy;

  // actionvalue method cfg
  input  [7 : 0] cfg_address;
  input  [31 : 0] cfg_data_in;
  input  cfg_op;
  input  cfg_en;
  output [31 : 0] cfg_data_out;
  output cfg_rdy;

  // signals for module outputs
  wire [31 : 0] cfg_data_out;
  wire [7 : 0] dout_value;
  wire cfg_rdy, din_rdy, dout_rdy, len_rdy;

  // inlined wires
  wire w_sw_override$whas;

  // register busy
  reg busy;
  wire busy$D_IN, busy$EN;

  // register current_count
  reg [7 : 0] current_count;
  wire [7 : 0] current_count$D_IN;
  wire current_count$EN;

  // register pause
  reg pause;
  wire pause$D_IN, pause$EN;

  // register programmed_length
  reg [7 : 0] programmed_length;
  wire [7 : 0] programmed_length$D_IN;
  wire programmed_length$EN;

  // register sum
  reg [7 : 0] sum;
  wire [7 : 0] sum$D_IN;
  wire sum$EN;

  // register sw_override
  reg sw_override;
  wire sw_override$D_IN, sw_override$EN;

  // ports of submodule dout_ff
  wire [7 : 0] dout_ff$D_IN, dout_ff$D_OUT;
  wire dout_ff$CLR, dout_ff$DEQ, dout_ff$EMPTY_N, dout_ff$ENQ, dout_ff$FULL_N;

  // inputs to muxes for submodule ports
  wire MUX_programmed_length$write_1__SEL_1;

  // remaining internal signals
  reg [31 : 0] CASE_cfg_address_0_0_CONCAT_x69_4_0_CONCAT_sw__ETC__q1;
  wire [16 : 0] x__h969;
  wire [7 : 0] next_count__h523;
  wire current_count_PLUS_1_EQ_programmed_length___d8;
  reg pause_delay;                                                          /* samples pause and makes sure its effect is reflected 
                                                                               only after accumulation has begun (i.e after busy is asserted) */
  

  // action method din
  assign din_rdy = !(programmed_length ==0) && 
                    ((busy || !pause_delay) && dout_ff$FULL_N);             //asserted only after programmed length has been set
                                        
  //assign din_rdy = (busy || !pause) && dout_ff$FULL_N ;
  // actionvalue method dout
  assign dout_value = dout_ff$D_OUT ;
  assign dout_rdy = dout_ff$EMPTY_N ;

  // action method len
  assign len_rdy = 1'd1 ;

  // actionvalue method cfg
  assign cfg_data_out =
	     cfg_op ?
	       32'd0 :
	       CASE_cfg_address_0_0_CONCAT_x69_4_0_CONCAT_sw__ETC__q1 ;
  assign cfg_rdy = 1'd1 ;

  // submodule dout_ff
  FIFO2 #(.width(32'd8), .guarded(1'd1)) dout_ff(.RST(RST_N),
						 .CLK(CLK),
						 .D_IN(dout_ff$D_IN),
						 .ENQ(dout_ff$ENQ),
						 .DEQ(dout_ff$DEQ),
						 .CLR(dout_ff$CLR),
						 .D_OUT(dout_ff$D_OUT),
						 .FULL_N(dout_ff$FULL_N),
						 .EMPTY_N(dout_ff$EMPTY_N));

  // inputs to muxes for submodule ports
  assign MUX_programmed_length$write_1__SEL_1 =
	     len_en && !sw_override && !busy ;

  // inlined wires
  assign w_sw_override$whas = cfg_en && cfg_op && cfg_address == 8'd4 ;

  // register busy
  assign busy$D_IN = !current_count_PLUS_1_EQ_programmed_length___d8 ;
  assign busy$EN = din_en ;

  // register current_count
  assign current_count$D_IN = next_count__h523 ;
  assign current_count$EN =
	     din_en && !current_count_PLUS_1_EQ_programmed_length___d8 ;

  // register pause
  assign pause$D_IN = cfg_data_in[1] ;
  assign pause$EN = w_sw_override$whas;

  // register programmed_length
  assign programmed_length$D_IN =
	     MUX_programmed_length$write_1__SEL_1 ?
	       len_value :
	       cfg_data_in[7:0] ;
  assign programmed_length$EN =
	     (len_en && !sw_override ||                             
	     cfg_en && cfg_op && cfg_address == 8'd8 && sw_override) && 
	     !(busy || current_count_PLUS_1_EQ_programmed_length___d8) ;                                      

  // register sum
  assign sum$D_IN = sum + din_value ;
  assign sum$EN = din_en && !current_count_PLUS_1_EQ_programmed_length___d8 ;

  // register sw_override
  assign sw_override$D_IN = cfg_data_in[0] ;
  assign sw_override$EN = w_sw_override$whas ;

  // submodule dout_ff
  assign dout_ff$D_IN = sum + din_value ;
  assign dout_ff$ENQ = din_en && current_count_PLUS_1_EQ_programmed_length___d8 ; 

  assign dout_ff$DEQ = dout_en ;
  assign dout_ff$CLR = 1'b0 ;

  // remaining internal signals
  assign current_count_PLUS_1_EQ_programmed_length___d8 =
	     next_count__h523 == programmed_length ;                        
	     
  assign next_count__h523 = current_count + 8'd1 ;                                   
  assign x__h969 = { busy, programmed_length, current_count } ;
  always@(cfg_address or programmed_length or x__h969 or sw_override)
  begin
    case (cfg_address)
      8'd0:
	  CASE_cfg_address_0_0_CONCAT_x69_4_0_CONCAT_sw__ETC__q1 =
	      { 15'd0, x__h969 };
      8'd4:
	  CASE_cfg_address_0_0_CONCAT_x69_4_0_CONCAT_sw__ETC__q1 =
	      { 31'd0, sw_override };
      default: CASE_cfg_address_0_0_CONCAT_x69_4_0_CONCAT_sw__ETC__q1 =
		   { 24'd0, programmed_length };
    endcase
  end

  // handling of inlined registers

  always@(posedge CLK or `BSV_RESET_EDGE RST_N)
  if (RST_N == `BSV_RESET_VALUE)
    begin
      busy <= `BSV_ASSIGNMENT_DELAY 1'd0;
      current_count <= `BSV_ASSIGNMENT_DELAY 8'd0;
      pause <= `BSV_ASSIGNMENT_DELAY 1'd0;
      programmed_length <= `BSV_ASSIGNMENT_DELAY 8'd0;
      sum <= `BSV_ASSIGNMENT_DELAY 8'd0;
      sw_override <= `BSV_ASSIGNMENT_DELAY 1'd0;
    end
  else
    begin
      if (busy$EN) busy <= `BSV_ASSIGNMENT_DELAY busy$D_IN;
      if (current_count$EN)
	current_count <= `BSV_ASSIGNMENT_DELAY current_count$D_IN;
      if (pause$EN) pause <= `BSV_ASSIGNMENT_DELAY pause$D_IN;
      if (programmed_length$EN)
	programmed_length <= `BSV_ASSIGNMENT_DELAY programmed_length$D_IN;
      if (sum$EN) sum <= `BSV_ASSIGNMENT_DELAY sum$D_IN;
      if (sw_override$EN)
	sw_override <= `BSV_ASSIGNMENT_DELAY sw_override$D_IN;
	  if (din_en) pause_delay<=pause;
	

	    
    end
    
    

  // synopsys translate_off
  `ifdef BSV_NO_INITIAL_BLOCKS
  `else // not BSV_NO_INITIAL_BLOCKS
  initial
  begin
    busy = 1'h0;
    current_count = 8'hAA;
    pause = 1'h0;
    programmed_length = 8'hAA;
    sum = 8'hAA;
    sw_override = 1'h0;
    pause_delay=1'h0;
  end
  `endif // BSV_NO_INITIAL_BLOCKS
  // synopsys translate_on
endmodule  // dut

