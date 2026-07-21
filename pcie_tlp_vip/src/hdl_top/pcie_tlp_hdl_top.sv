// HDL Top
`ifndef PCIE_TLP_HDL_TOP_SVH
`define PCIE_TLP_HDL_TOP_SVH
module pcie_tlp_hdl_top;
    import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*;
    bit clk, rst_n;
    initial begin clk = 0; forever #5 clk = ~clk; end
    initial begin rst_n = 1; #10 rst_n = 0; repeat(2) @(posedge clk); rst_n = 1; `uvm_info("HDL_TOP", "Reset deasserted", UVM_LOW) end
    pcie_tlp_if intf (.clk(clk), .rst_n(rst_n));
    pcie_tlp_rc_agent_bfm #(.RC_ID(0)) rc_bfm (intf);
    pcie_tlp_ep_agent_bfm #(.EP_ID(0)) ep_bfm (intf);
    initial begin $dumpfile("waveform.vcd"); $dumpvars(0, pcie_tlp_hdl_top); end
endmodule
`endif
