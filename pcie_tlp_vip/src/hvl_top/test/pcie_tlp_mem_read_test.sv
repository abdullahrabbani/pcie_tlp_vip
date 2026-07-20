// Memory Read Test
`ifndef PCIE_TLP_MEM_READ_TEST_SVH
`define PCIE_TLP_MEM_READ_TEST_SVH
import uvm_pkg::*; `include "uvm_macros.svh"
class pcie_tlp_mem_read_test extends pcie_tlp_base_test;
    `uvm_component_utils(pcie_tlp_mem_read_test)
    function new(string name, uvm_component parent=null); super.new(name, parent); endfunction
    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        cfg.num_transactions = 20;
        cfg.start_address = 32'h0000_0000;
        cfg.end_address   = 32'h0000_0FFF;
        `uvm_info("TEST", "Memory Read Test configured", UVM_LOW)
    endfunction
endclass
`endif
