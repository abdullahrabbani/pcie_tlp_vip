// EP Agent Package
`ifndef PCIE_TLP_EP_PKG_SVH
`define PCIE_TLP_EP_PKG_SVH

package pcie_tlp_ep_pkg;
    `include "uvm_macros.svh"
    import uvm_pkg::*;
    import pcie_tlp_globals_pkg::*;

    `include "pcie_tlp_ep_memory.sv"
    `include "pcie_tlp_ep_tx.sv"
    `include "pcie_tlp_ep_agent_config.sv"
    `include "pcie_tlp_ep_seq_item_converter.sv"
    `include "pcie_tlp_ep_convernter_config.sv"
    //`include "pcie_tlp_ep_coverage.sv"
    `include "pcie_tlp_ep_write_sequencer.sv"
    `include "pcie_tlp_ep_read_sequencer.sv"
    `include "pcie_tlp_ep_driver_proxy.sv"
    `include "pcie_tlp_ep_monitor_proxy.sv"
    `include "pcie_tlp_ep_agent.sv"
endpackage

`endif
