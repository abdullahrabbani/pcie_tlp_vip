// RC Coverage Collector (DISABLED)
`ifndef PCIE_TLP_RC_COVERAGE_SVH
`define PCIE_TLP_RC_COVERAGE_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*; import pcie_tlp_rc_pkg::*;

class pcie_tlp_rc_coverage extends uvm_component;
    `uvm_component_utils(pcie_tlp_rc_coverage)

    uvm_analysis_imp #(pcie_tlp_rc_tx, pcie_tlp_rc_coverage) analysis_imp;
    pcie_tlp_rc_agent_config cfg;

    function new(string name = "pcie_tlp_rc_coverage", uvm_component parent = null);
        super.new(name, parent);
        analysis_imp = new("analysis_imp", this);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        if (!uvm_config_db#(pcie_tlp_rc_agent_config)::get(this, "", "cfg", cfg)) begin
            `uvm_info(get_type_name(), "No config set, using default ranges", UVM_LOW)
        end
    endfunction

    function void write(pcie_tlp_rc_tx tx);
        `uvm_info(get_type_name(), $sformatf("Coverage disabled for TLP ID %0d", tx.transaction_id), UVM_HIGH)
    endfunction

endclass

`endif
