// PCIe Environment Package
`ifndef PCIE_TLP_ENV_PKG_SVH
`define PCIE_TLP_ENV_PKG_SVH

package pcie_tlp_env_pkg;
    `include "uvm_macros.svh"
    import uvm_pkg::*;
    import pcie_tlp_globals_pkg::*;
    import pcie_tlp_rc_pkg::*;
    import pcie_tlp_ep_pkg::*;

    `include "pcie_tlp_env_config.sv"
    `include "pcie_tlp_virtual_sequencer.sv"
    `include "pcie_tlp_scoreboard.sv"
    `include "pcie_tlp_env.sv"
endpackage

`endif
