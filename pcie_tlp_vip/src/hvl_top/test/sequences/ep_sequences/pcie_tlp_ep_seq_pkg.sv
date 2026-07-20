// EP Sequence Package
`ifndef PCIE_TLP_EP_SEQ_PKG_SVH
`define PCIE_TLP_EP_SEQ_PKG_SVH

package pcie_tlp_ep_seq_pkg;
    `include "uvm_macros.svh"
    import uvm_pkg::*;
    import pcie_tlp_ep_pkg::*;
    import pcie_tlp_globals_pkg::*;

    `include "pcie_tlp_ep_base_seq.sv"
endpackage

`endif
