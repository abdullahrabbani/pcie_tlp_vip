// RC Agent Configuration
`ifndef PCIE_TLP_RC_AGENT_CONFIG_SVH
`define PCIE_TLP_RC_AGENT_CONFIG_SVH

import uvm_pkg::*; `include "uvm_macros.svh"
import pcie_tlp_globals_pkg::*;

class pcie_tlp_rc_agent_config extends uvm_object;
    `uvm_object_utils(pcie_tlp_rc_agent_config)
    uvm_active_passive_enum is_active = UVM_ACTIVE;
    bit has_coverage = 1'b0;
    int num_transactions = 10;
    int max_payload_size = PCIE_TLP_MAX_PAYLOAD;
    bit flow_control_enabled = 1'b1;
    int wait_states = 0;
    int outstanding_write_tx = 4;
    int outstanding_read_tx  = 4;
    int address_range_min[int];
    int address_range_max[int];

    function new(string name = "pcie_tlp_rc_agent_config");
        super.new(name);
    endfunction

    function void set_min_address_range(int target_id, int min_addr);
        address_range_min[target_id] = min_addr;
    endfunction

    function void set_max_address_range(int target_id, int max_addr);
        address_range_max[target_id] = max_addr;
    endfunction

    function int get_min_address_range(int target_id);
        if (address_range_min.exists(target_id))
            return address_range_min[target_id];
        else
            return 0;
    endfunction

    function int get_max_address_range(int target_id);
        if (address_range_max.exists(target_id))
            return address_range_max[target_id];
        else
            return 0;
    endfunction

    function void do_print(uvm_printer printer);
        super.do_print(printer);
        printer.print_string("is_active", is_active.name());
        printer.print_field("has_coverage", has_coverage, $bits(has_coverage), UVM_BIN);
        printer.print_field("num_transactions", num_transactions, $bits(num_transactions), UVM_DEC);
        printer.print_field("max_payload_size", max_payload_size, $bits(max_payload_size), UVM_DEC);
        printer.print_field("flow_control_enabled", flow_control_enabled, $bits(flow_control_enabled), UVM_BIN);
        printer.print_field("wait_states", wait_states, $bits(wait_states), UVM_DEC);
        printer.print_field("outstanding_write_tx", outstanding_write_tx, $bits(outstanding_write_tx), UVM_DEC);
        printer.print_field("outstanding_read_tx", outstanding_read_tx, $bits(outstanding_read_tx), UVM_DEC);
        foreach (address_range_min[i]) begin
            printer.print_field($sformatf("address_range_min[%0d]", i),
                                address_range_min[i],
                                $bits(address_range_min[i]), UVM_HEX);
        end
        foreach (address_range_max[i]) begin
            printer.print_field($sformatf("address_range_max[%0d]", i),
                                address_range_max[i],
                                $bits(address_range_max[i]), UVM_HEX);
        end
    endfunction

endclass

`endif
