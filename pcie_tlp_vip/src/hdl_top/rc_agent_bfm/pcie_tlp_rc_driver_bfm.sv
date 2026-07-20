// RC Driver BFM
`ifndef PCIE_TLP_RC_DRIVER_BFM_SVH
`define PCIE_TLP_RC_DRIVER_BFM_SVH

import pcie_tlp_globals_pkg::*;
import uvm_pkg::*;
`include "uvm_macros.svh"

interface pcie_tlp_rc_driver_bfm (
    input logic clk,
    input logic rst_n,
    output logic [63:0] tx_data,
    output logic [7:0]  tx_keep,
    output logic        tx_valid,
    input  logic        tx_ready,
    output logic        tx_sop,
    output logic        tx_eop,
    output logic [2:0]  tx_empty,
    output logic [3:0]  tx_seq_num,
    output logic [1:0]  tx_vc_id,
    output logic [2:0]  tx_tc,
    input  logic [63:0] rx_data,
    input  logic [7:0]  rx_keep,
    input  logic        rx_valid,
    output logic        rx_ready,
    input  logic        rx_sop,
    input  logic        rx_eop,
    input  logic [2:0]  rx_empty,
    input  logic [3:0]  rx_seq_num,
    input  logic [1:0]  rx_vc_id,
    input  logic [2:0]  rx_tc
);

    string name = "PCIE_TLP_RC_DRIVER_BFM";

    initial begin
        `uvm_info(name, $sformatf("%s instantiated", name), UVM_LOW)
    end

    task wait_for_reset();
        @(negedge rst_n);
        `uvm_info(name, "Reset detected (active low)", UVM_HIGH)
        default_values();
        @(posedge rst_n);
        `uvm_info(name, "Reset deactivated", UVM_HIGH)
    endtask

    clocking drv_cb @(posedge clk);
        default input #1step output #1step;
        output tx_data, tx_keep, tx_valid, tx_sop, tx_eop, tx_empty,
               tx_seq_num, tx_vc_id, tx_tc, rx_ready;
        input  tx_ready, rx_data, rx_keep, rx_valid, rx_sop, rx_eop,
               rx_empty, rx_seq_num, rx_vc_id, rx_tc;
    endclocking

    task default_values();
        drv_cb.tx_data    <= '0;
        drv_cb.tx_keep    <= '0;
        drv_cb.tx_valid   <= 1'b0;
        drv_cb.tx_sop     <= 1'b0;
        drv_cb.tx_eop     <= 1'b0;
        drv_cb.tx_empty   <= 3'b0;
        drv_cb.tx_seq_num <= 4'b0;
        drv_cb.tx_vc_id   <= 2'b0;
        drv_cb.tx_tc      <= 3'b0;
        drv_cb.rx_ready   <= 1'b0;
    endtask

    task automatic send_tlp(
        input tlp_t tlp,
        input int wait_states = 0
    );
        automatic int payload_words;
        automatic int total_beats;
        payload_words = (tlp.payload_size + 3) / 4;
        total_beats = 1 + payload_words;

        `uvm_info(name, $sformatf("Sending TLP ID %0d, %0d beats",
                    tlp.transaction_id, total_beats), UVM_HIGH)

        wait_for_reset();
        repeat (wait_states) @(drv_cb);

        @(drv_cb);
        drv_cb.tx_data    <= {tlp.header.dw3, tlp.header.dw2,
                              tlp.header.dw1, tlp.header.dw0};
        drv_cb.tx_keep    <= 8'hFF;
        drv_cb.tx_valid   <= 1'b1;
        drv_cb.tx_sop     <= 1'b1;
        drv_cb.tx_eop     <= 1'b0;
        drv_cb.tx_empty   <= 3'b0;
        drv_cb.tx_seq_num <= tlp.transaction_id[3:0];
        drv_cb.tx_vc_id   <= 2'b0;
        drv_cb.tx_tc      <= 3'b0;

        do begin
            @(drv_cb);
        end while (drv_cb.tx_ready !== 1'b1);

        if (payload_words > 0) begin
            for (int i = 0; i < payload_words; i++) begin
                logic [31:0] word;
                word = tlp.payload[i*4 +: 32];
                @(drv_cb);
                drv_cb.tx_data    <= {32'h0, word};
                drv_cb.tx_keep    <= 8'h0F;
                drv_cb.tx_valid   <= 1'b1;
                drv_cb.tx_sop     <= 1'b0;
                drv_cb.tx_eop     <= (i == payload_words-1) ? 1'b1 : 1'b0;
                drv_cb.tx_empty   <= 3'b0;
                drv_cb.tx_seq_num <= tlp.transaction_id[3:0];
                drv_cb.tx_vc_id   <= 2'b0;
                drv_cb.tx_tc      <= 3'b0;

                `uvm_info(name, $sformatf("Sending payload beat %0d", i), UVM_HIGH)
                do begin
                    @(drv_cb);
                end while (drv_cb.tx_ready !== 1'b1);
            end
        end else begin
            @(drv_cb);
            drv_cb.tx_eop <= 1'b1;
            do begin
                @(drv_cb);
            end while (drv_cb.tx_ready !== 1'b1);
        end

        @(drv_cb);
        default_values();

        `uvm_info(name, $sformatf("TLP ID %0d sent successfully", tlp.transaction_id), UVM_HIGH)
    endtask

endinterface : pcie_tlp_rc_driver_bfm

`endif
