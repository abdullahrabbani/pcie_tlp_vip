// RC Configuration Converter
`ifndef PCIE_TLP_RC_COVERNTER_CONFIG_SVH
`define PCIE_TLP_RC_COVERNTER_CONFIG_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*; import pcie_tlp_rc_pkg::*;

typedef struct {
    int num_transactions;
    int start_address;
    int end_address;
    bit is_active;
    int max_payload_size;
    int wait_states;
    bit flow_control_enabled;
    int outstanding_limit;
} pcie_tlp_rc_cfg_s;

class pcie_tlp_rc_cfg_converter extends uvm_object;
    `uvm_object_utils(pcie_tlp_rc_cfg_converter)

    function new(string name = "pcie_tlp_rc_cfg_converter");
        super.new(name);
    endfunction

    static function void from_class(input pcie_tlp_rc_agent_config cfg_in,
                                    output pcie_tlp_rc_cfg_s cfg_out);
        cfg_out.num_transactions  = cfg_in.num_transactions;
        cfg_out.start_address     = cfg_in.address_range_min[0];
        cfg_out.end_address       = cfg_in.address_range_max[0];
        cfg_out.is_active         = (cfg_in.is_active == UVM_ACTIVE);
        cfg_out.max_payload_size  = PCIE_TLP_MAX_PAYLOAD;
        cfg_out.wait_states       = cfg_in.wait_states;
        cfg_out.flow_control_enabled = cfg_in.flow_control_enabled;
        cfg_out.outstanding_limit = cfg_in.outstanding_write_tx;
    endfunction

    static function void to_class(input pcie_tlp_rc_cfg_s cfg_in,
                                  output pcie_tlp_rc_agent_config cfg_out);
        cfg_out.num_transactions = cfg_in.num_transactions;
        cfg_out.wait_states      = cfg_in.wait_states;
        cfg_out.flow_control_enabled = cfg_in.flow_control_enabled;
    endfunction

    function void do_print(uvm_printer printer);
        pcie_tlp_rc_cfg_s cfg;
        printer.print_field("num_transactions", cfg.num_transactions, $bits(cfg.num_transactions), UVM_DEC);
        printer.print_field("start_address", cfg.start_address, $bits(cfg.start_address), UVM_HEX);
        printer.print_field("end_address", cfg.end_address, $bits(cfg.end_address), UVM_HEX);
        printer.print_field("is_active", cfg.is_active, $bits(cfg.is_active), UVM_BIN);
        printer.print_field("max_payload_size", cfg.max_payload_size, $bits(cfg.max_payload_size), UVM_DEC);
        printer.print_field("wait_states", cfg.wait_states, $bits(cfg.wait_states), UVM_DEC);
        printer.print_field("flow_control_enabled", cfg.flow_control_enabled, $bits(cfg.flow_control_enabled), UVM_BIN);
        printer.print_field("outstanding_limit", cfg.outstanding_limit, $bits(cfg.outstanding_limit), UVM_DEC);
    endfunction

endclass

`endif
