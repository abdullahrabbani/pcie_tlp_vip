// TB EP Assertions (DISABLED)
`ifndef PCIE_TLP_TB_EP_ASSERTIONS_SVH
`define PCIE_TLP_TB_EP_ASSERTIONS_SVH

import pcie_tlp_globals_pkg::*;
import uvm_pkg::*;
`include "uvm_macros.svh"

module pcie_tlp_tb_ep_assertions;

    logic clk; logic rst_n;
    logic [63:0] tx_data;
    logic [7:0]  tx_keep;
    logic        tx_valid;
    logic        tx_ready;
    logic        tx_sop;
    logic        tx_eop;
    logic [2:0]  tx_empty;
    logic [3:0]  tx_seq_num;
    logic [1:0]  tx_vc_id;
    logic [2:0]  tx_tc;
    logic [63:0] rx_data;
    logic [7:0]  rx_keep;
    logic        rx_valid;
    logic        rx_ready;
    logic        rx_sop;
    logic        rx_eop;
    logic [2:0]  rx_empty;
    logic [3:0]  rx_seq_num;
    logic [1:0]  rx_vc_id;
    logic [2:0]  rx_tc;

    pcie_tlp_ep_assertions ep_assertions_inst (.*);

    initial begin clk = 1'b0; forever #5 clk = ~clk; end

    task reset_gen();
        rst_n = 1'b0; @(posedge clk); @(posedge clk); rst_n = 1'b1;
        `uvm_info("TB_EP_ASSERT", "Reset deasserted", UVM_LOW)
    endtask

    task automatic drive_rx_tlp(input tlp_header_t header, input int payload_size = 0);
        automatic int words;
        @(posedge clk);
        rx_data   <= {header.dw1, header.dw0};
        rx_keep   <= 8'hFF;
        rx_valid  <= 1'b1;
        rx_ready  <= 1'b0;
        rx_sop    <= 1'b1;
        rx_eop    <= (payload_size == 0) ? 1'b1 : 1'b0;
        #1;
        @(posedge clk);
        rx_data   <= {header.dw3, header.dw2};
        rx_sop    <= 1'b0;
        rx_eop    <= (payload_size == 0) ? 1'b1 : 1'b0;
        #1;
        if (payload_size > 0) begin
            words = (payload_size + 3) / 4;
            for (int i = 0; i < words; i++) begin
                @(posedge clk);
                rx_data   <= {32'h0, 32'hDEAD_BEEF};
                rx_keep   <= 8'h0F;
                rx_sop    <= 1'b0;
                rx_eop    <= (i == words-1) ? 1'b1 : 1'b0;
                #1;
            end
        end
        @(posedge clk);
        rx_valid  <= 1'b0; rx_sop <= 1'b0; rx_eop <= 1'b0; rx_ready <= 1'b0;
    endtask

    task automatic drive_tx_completion(input tlp_header_t header, input int payload_size = 0);
        automatic int words;
        @(posedge clk);
        tx_data   <= {header.dw1, header.dw0};
        tx_keep   <= 8'hFF;
        tx_valid  <= 1'b1;
        tx_ready  <= 1'b0;
        tx_sop    <= 1'b1;
        tx_eop    <= (payload_size == 0) ? 1'b1 : 1'b0;
        #1;
        @(posedge clk);
        tx_data   <= {header.dw3, header.dw2};
        tx_sop    <= 1'b0;
        tx_eop    <= (payload_size == 0) ? 1'b1 : 1'b0;
        #1;
        if (payload_size > 0) begin
            words = (payload_size + 3) / 4;
            for (int i = 0; i < words; i++) begin
                @(posedge clk);
                tx_data   <= {32'h0, 32'hDEAD_BEEF};
                tx_keep   <= 8'h0F;
                tx_sop    <= 1'b0;
                tx_eop    <= (i == words-1) ? 1'b1 : 1'b0;
                #1;
            end
        end
        @(posedge clk);
        tx_valid  <= 1'b0; tx_sop <= 1'b0; tx_eop <= 1'b0; tx_ready <= 1'b0;
    endtask

    initial begin
        `uvm_info("TB_EP_ASSERT", "Starting EP assertions testbench (DISABLED)", UVM_LOW);
        #100;
        `uvm_info("TB_EP_ASSERT", "EP assertions testbench completed", UVM_LOW);
        $finish;
    end

endmodule

`endif
