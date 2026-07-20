// EP Configuration Converter
`ifndef PCIE_TLP_EP_COVERNTER_CONFIG_SVH
`define PCIE_TLP_EP_COVERNTER_CONFIG_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*; import pcie_tlp_ep_pkg::*;

typedef struct {
    int min_address;
    int max_address;
    int memory_size;
    int wait_states;
    int outstanding_limit;
    int response_mode;
    bit flow_control_enabled;
    bit is_active;
} pcie_tlp_ep_cfg_s;

class pcie_tlp_ep_cfg_converter extends uvm_object;
    `uvm_object_utils(pcie_tlp_ep_cfg_converter)

    function new(string name = "pcie_tlp_ep_cfg_converter");
        super.new(name);
    endfunction

    static function void from_class(input pcie_tlp_ep_agent_config cfg_in,
                                    output pcie_tlp_ep_cfg_s cfg_out);
        cfg_out.min_address       = cfg_in.min_address;
        cfg_out.max_address       = cfg_in.max_address;
        cfg_out.memory_size       = cfg_in.memory_size;
        cfg_out.wait_states       = cfg_in.wait_states;
        cfg_out.outstanding_limit = cfg_in.outstanding_limit;
        cfg_out.response_mode     = cfg_in.response_mode;
        cfg_out.flow_control_enabled = cfg_in.flow_control_enabled;
        cfg_out.is_active         = (cfg_in.is_active == UVM_ACTIVE);
    endfunction

    static function void to_class(input pcie_tlp_ep_cfg_s cfg_in,
                                  output pcie_tlp_ep_agent_config cfg_out);
        cfg_out.min_address       = cfg_in.min_address;
        cfg_out.max_address       = cfg_in.max_address;
        cfg_out.memory_size       = cfg_in.memory_size;
        cfg_out.wait_states       = cfg_in.wait_states;
        cfg_out.outstanding_limit = cfg_in.outstanding_limit;
        cfg_out.response_mode     = cfg_in.response_mode;
        cfg_out.flow_control_enabled = cfg_in.flow_control_enabled;
        cfg_out.is_active         = cfg_in.is_active ? UVM_ACTIVE : UVM_PASSIVE;
    endfunction

    function void do_print(uvm_printer printer);
        pcie_tlp_ep_cfg_s cfg;
        printer.print_field("min_address", cfg.min_address, $bits(cfg.min_address), UVM_HEX);
        printer.print_field("max_address", cfg.max_address, $bits(cfg.max_address), UVM_HEX);
        printer.print_field("memory_size", cfg.memory_size, $bits(cfg.memory_size), UVM_DEC);
        printer.print_field("wait_states", cfg.wait_states, $bits(cfg.wait_states), UVM_DEC);
        printer.print_field("outstanding_limit", cfg.outstanding_limit, $bits(cfg.outstanding_limit), UVM_DEC);
        printer.print_field("response_mode", cfg.response_mode, $bits(cfg.response_mode), UVM_DEC);
        printer.print_field("flow_control_enabled", cfg.flow_control_enabled, 1, UVM_BIN);
        printer.print_field("is_active", cfg.is_active, 1, UVM_BIN);
    endfunction

endclass

`endif
