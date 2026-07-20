# PCIe TLP VIP Makefile
# QuestaSim/ModelSim

SIM          = vsim
WORK         = work
UVM_VER      = 1.1d
TEST         = pcie_tlp_base_test
COVER_OPT    = +cover +fcover
SIM_OPT      = -sv -uvm$(UVM_VER) $(COVER_OPT)
TOP          = pcie_tlp_hvl_top

all: compile sim

compile:
	vlib $(WORK)
	vlog -work $(WORK) $(SIM_OPT) -f ../pcie_tlp_compile.f

sim:
	vsim -c -do "run -all; exit" -work $(WORK) $(TOP) +UVM_TESTNAME=$(TEST)

gui:
	vsim -do "run -all" -work $(WORK) $(TOP) +UVM_TESTNAME=$(TEST)

clean:
	rm -rf $(WORK) *.log *.wlf *.vcd transcript

.PHONY: all compile sim gui clean
