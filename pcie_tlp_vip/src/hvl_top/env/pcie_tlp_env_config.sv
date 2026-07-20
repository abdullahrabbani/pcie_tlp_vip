// PCIe Environment Configuration
`ifndef PCIE_TLP_ENV_CONFIG_SVH
`define PCIE_TLP_ENV_CONFIG_SVH

import uvm_pkg::*; `include "uvm_macros.svh"
import pcie_tlp_globals_pkg::*;
import pcie_tlp_rc_pkg::*;
import pcie_tlp_ep_pkg::*;

class pcie_tlp_env_config extends uvm_object;
    `uvm_object_utils(pcie_tlp_env_config)

    bit has_scoreboard = 1'b1;
    bit has_virtual_seqr = 1'b1;
    bit rc_agent_enabled = 1'b1;
    bit ep_agent_enabled = 1'b1;
    int num_transactions = 10;
    int start_address = 32'h0000_0000;
    int end_address   = 32'h0000_0FFF;
    write_read_data_mode_e write_read_mode_h = WRITE_READ_DATA;
    pcie_tlp_rc_agent_config rc_cfg;
    pcie_tlp_ep_agent_config ep_cfg;

    function new(string name = "pcie_tlp_env_config");
        super.new(name);
    endfunction

    function void do_print(uvm_printer printer);
        super.do_print(printer);
        printer.print_field("has_scoreboard", has_scoreboard, 1, UVM_BIN);
        printer.print_field("has_virtual_seqr", has_virtual_seqr, 1, UVM_BIN);
        printer.print_field("rc_agent_enabled", rc_agent_enabled, 1, UVM_BIN);
        printer.print_field("ep_agent_enabled", ep_agent_enabled, 1, UVM_BIN);
        printer.print_field("num_transactions", num_transactions, $bits(num_transactions), UVM_DEC);
        printer.print_field("start_address", start_address, $bits(start_address), UVM_HEX);
        printer.print_field("end_address", end_address, $bits(end_address), UVM_HEX);
        printer.print_string("write_read_mode_h", write_read_mode_h.name());
        if (rc_cfg != null) printer.print_object("rc_cfg", rc_cfg);
        if (ep_cfg != null) printer.print_object("ep_cfg", ep_cfg);
    endfunction

endclass

`endif
