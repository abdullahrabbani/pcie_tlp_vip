// EP Agent Configuration
`ifndef PCIE_TLP_EP_AGENT_CONFIG_SVH
`define PCIE_TLP_EP_AGENT_CONFIG_SVH

import uvm_pkg::*; `include "uvm_macros.svh"
import pcie_tlp_globals_pkg::*;

class pcie_tlp_ep_agent_config extends uvm_object;
    `uvm_object_utils(pcie_tlp_ep_agent_config)
    uvm_active_passive_enum is_active = UVM_ACTIVE;
    bit has_coverage = 1'b0;
    int min_address = 32'h0000_0000;
    int max_address = 32'h0000_0FFF;
    int memory_size = 4096;
    int wait_states = 0;
    int outstanding_limit = 8;
    int response_mode = 0;
    bit flow_control_enabled = 1'b1;
    int default_read_data = 32'hDEAD_BEEF;

    function new(string name = "pcie_tlp_ep_agent_config");
        super.new(name);
    endfunction

    function int get_min_address(); return min_address; endfunction
    function int get_max_address(); return max_address; endfunction
    function int get_memory_size(); return memory_size; endfunction
    function int get_wait_states(); return wait_states; endfunction
    function int get_outstanding_limit(); return outstanding_limit; endfunction
    function bit is_in_order(); return (response_mode == 0); endfunction
    function bit is_out_of_order(); return (response_mode == 1); endfunction

    function void do_print(uvm_printer printer);
        super.do_print(printer);
        printer.print_string("is_active", is_active.name());
        printer.print_field("has_coverage", has_coverage, $bits(has_coverage), UVM_BIN);
        printer.print_field("min_address", min_address, $bits(min_address), UVM_HEX);
        printer.print_field("max_address", max_address, $bits(max_address), UVM_HEX);
        printer.print_field("memory_size", memory_size, $bits(memory_size), UVM_DEC);
        printer.print_field("wait_states", wait_states, $bits(wait_states), UVM_DEC);
        printer.print_field("outstanding_limit", outstanding_limit, $bits(outstanding_limit), UVM_DEC);
        printer.print_field("response_mode", response_mode, $bits(response_mode), UVM_DEC);
        printer.print_field("flow_control_enabled", flow_control_enabled, 1, UVM_BIN);
        printer.print_field("default_read_data", default_read_data, $bits(default_read_data), UVM_HEX);
    endfunction

endclass

`endif
