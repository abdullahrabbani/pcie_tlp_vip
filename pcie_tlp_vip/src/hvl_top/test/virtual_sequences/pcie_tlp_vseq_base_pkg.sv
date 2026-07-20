// Virtual Sequence Base Package
`ifndef PCIE_TLP_VSEQ_BASE_PKG_SVH
`define PCIE_TLP_VSEQ_BASE_PKG_SVH

package pcie_tlp_vseq_base_pkg;
    `include "uvm_macros.svh"
    import uvm_pkg::*;
    import pcie_tlp_globals_pkg::*;
    import pcie_tlp_env_pkg::*;

    `include "pcie_tlp_virtual_base_seq.sv"
endpackage

`endif
