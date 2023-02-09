SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES += $(PWD)/wrappers/acc_test.v
VERILOG_SOURCES += $(PWD)/../hdl/dut.v
VERILOG_SOURCES += $(PWD)/../hdl/FIFO2.v

acc:
	rm -rf sim_build
	$(MAKE) sim MODULE=acc_test TOPLEVEL=acc_test
	
include $(shell cocotb-config --makefiles)/Makefile.sim
