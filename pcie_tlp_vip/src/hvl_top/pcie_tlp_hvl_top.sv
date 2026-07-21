// HVL Top module
`ifndef PCIE_TLP_HVL_TOP_SVH
`define PCIE_TLP_HVL_TOP_SVH

module pcie_tlp_hvl_top;

    import uvm_pkg::*;
    `include "uvm_macros.svh"
    import pcie_tlp_globals_pkg::*;
    import pcie_tlp_test_pkg::*;

    logic clk;
    logic rst_n;
    pcie_tlp_if if0 (.clk(clk), .rst_n(rst_n));

    initial begin
        clk = 1'b0;
        forever #5 clk = ~clk;
    end

    initial begin
        rst_n = 1'b0;
        #20;
        rst_n = 1'b1;
        `uvm_info("HVL_TOP", "Reset deasserted", UVM_LOW)
    end

    initial begin
        uvm_config_db#(virtual pcie_tlp_if)::set(null, "*", "pcie_tlp_if", if0);
        `uvm_info("HVL_TOP", "PCIe interface set in config DB", UVM_HIGH)
    end

    initial begin : START_TEST
        run_test("pcie_tlp_base_test");
    end

endmodule : pcie_tlp_hvl_top

`endif
