// RC Agent Package
`ifndef PCIE_TLP_RC_PKG_SVH
`define PCIE_TLP_RC_PKG_SVH

package pcie_tlp_rc_pkg;
    `include "uvm_macros.svh"
    import uvm_pkg::*;
    import pcie_tlp_globals_pkg::*;

    `include "pcie_tlp_rc_agent_config.sv"
    `include "pcie_tlp_rc_tx.sv"
    `include "pcie_tlp_rc_seq_item_converter.sv"
    `include "pcie_tlp_rc_covernter_config.sv"
    `include "pcie_tlp_rc_write_sequencer.sv"
    `include "pcie_tlp_rc_read_sequencer.sv"
    `include "pcie_tlp_rc_driver_proxy.sv"
    `include "pcie_tlp_rc_monitor_proxy.sv"
    //`include "pcie_tlp_rc_coverage.sv"
    `include "pcie_tlp_rc_agent.sv"
endpackage

`endif
