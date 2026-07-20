// RC Sequence Package
`ifndef PCIE_TLP_RC_SEQ_PKG_SVH
`define PCIE_TLP_RC_SEQ_PKG_SVH

package pcie_tlp_rc_seq_pkg;
    `include "uvm_macros.svh"
    import uvm_pkg::*;
    import pcie_tlp_rc_pkg::*;
    import pcie_tlp_globals_pkg::*;

    `include "pcie_tlp_rc_base_seq.sv"
endpackage

`endif
