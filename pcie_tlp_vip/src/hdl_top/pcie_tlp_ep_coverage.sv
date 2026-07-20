// EP Coverage Collector (DISABLED)
`ifndef PCIE_TLP_EP_COVERAGE_SVH
`define PCIE_TLP_EP_COVERAGE_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*; import pcie_tlp_ep_pkg::*;

class pcie_tlp_ep_coverage extends uvm_subscriber #(pcie_tlp_ep_tx);
    `uvm_component_utils(pcie_tlp_ep_coverage)
    pcie_tlp_ep_agent_config cfg;

    function new(string name = "pcie_tlp_ep_coverage", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        if (!uvm_config_db#(pcie_tlp_ep_agent_config)::get(this, "", "cfg", cfg)) begin
            `uvm_info(get_type_name(), "No configuration set, using defaults", UVM_LOW)
        end
    endfunction

    function void write(pcie_tlp_ep_tx t);
        `uvm_info(get_type_name(), $sformatf("Coverage disabled for EP TLP ID %0d", t.transaction_id), UVM_HIGH)
    endfunction

    function void report_phase(uvm_phase phase);
        `uvm_info(get_type_name(), "Coverage disabled", UVM_NONE)
    endfunction

endclass

`endif
