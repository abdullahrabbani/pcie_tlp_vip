// RC Monitor BFM
`ifndef PCIE_TLP_RC_MONITOR_BFM_SVH
`define PCIE_TLP_RC_MONITOR_BFM_SVH

import pcie_tlp_globals_pkg::*;
import uvm_pkg::*;
`include "uvm_macros.svh"

interface pcie_tlp_rc_monitor_bfm (
    input logic clk,
    input logic rst_n,
    input  logic [63:0] tx_data,
    input  logic [7:0]  tx_keep,
    input  logic        tx_valid,
    output logic        tx_ready,
    input  logic        tx_sop,
    input  logic        tx_eop,
    input  logic [2:0]  tx_empty,
    input  logic [3:0]  tx_seq_num,
    input  logic [1:0]  tx_vc_id,
    input  logic [2:0]  tx_tc,
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

    string name = "PCIE_TLP_RC_MONITOR_BFM";

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

    clocking mon_cb @(posedge clk);
        default input #1step output #1step;
        input  tx_data, tx_keep, tx_valid, tx_sop, tx_eop, tx_empty,
               tx_seq_num, tx_vc_id, tx_tc,
               rx_data, rx_keep, rx_valid, rx_sop, rx_eop, rx_empty,
               rx_seq_num, rx_vc_id, rx_tc;
        output tx_ready, rx_ready;
    endclocking

    task default_values();
        mon_cb.tx_ready <= 1'b0;
        mon_cb.rx_ready <= 1'b0;
    endtask

    task automatic sample_tx_tlp(output tlp_t tlp);
        automatic int payload_dwords;
        do begin
            @(mon_cb);
        end while (!(mon_cb.tx_valid && mon_cb.tx_sop));

        `uvm_info(name, "TX TLP start detected", UVM_HIGH)

        tlp.header.dw0 = mon_cb.tx_data[31:0];
        tlp.header.dw1 = mon_cb.tx_data[63:32];
        @(mon_cb);
        tlp.header.dw2 = mon_cb.tx_data[31:0];
        tlp.header.dw3 = mon_cb.tx_data[63:32];

        payload_dwords = tlp.header.dw0[9:0];
        if (payload_dwords > 1) begin
            for (int i = 0; i < payload_dwords; i++) begin
                @(mon_cb);
                tlp.payload[i*8 +: 32] = mon_cb.tx_data[31:0];
                tlp.payload[i*8 + 32 +: 32] = mon_cb.tx_data[63:32];
            end
        end

        tlp.payload_size = payload_dwords * 4;
        tlp.transaction_id = mon_cb.tx_seq_num;
        tlp.timestamp = $time;

        `uvm_info(name, $sformatf("Sampled TX TLP ID %0d, size %0d bytes", 
                   tlp.transaction_id, tlp.payload_size), UVM_HIGH)
    endtask

    task automatic sample_rx_tlp(output tlp_t tlp);
        automatic int payload_dwords;
        do begin
            @(mon_cb);
        end while (!(mon_cb.rx_valid && mon_cb.rx_sop));

        `uvm_info(name, "RX TLP start detected", UVM_HIGH)

        tlp.header.dw0 = mon_cb.rx_data[31:0];
        tlp.header.dw1 = mon_cb.rx_data[63:32];
        @(mon_cb);
        tlp.header.dw2 = mon_cb.rx_data[31:0];
        tlp.header.dw3 = mon_cb.rx_data[63:32];

        payload_dwords = tlp.header.dw0[9:0];
        if (payload_dwords > 1) begin
            for (int i = 0; i < payload_dwords; i++) begin
                @(mon_cb);
                tlp.payload[i*8 +: 32] = mon_cb.rx_data[31:0];
                tlp.payload[i*8 + 32 +: 32] = mon_cb.rx_data[63:32];
            end
        end

        tlp.payload_size = payload_dwords * 4;
        tlp.transaction_id = mon_cb.rx_seq_num;
        tlp.timestamp = $time;

        `uvm_info(name, $sformatf("Sampled RX TLP ID %0d, size %0d bytes", 
                   tlp.transaction_id, tlp.payload_size), UVM_HIGH)
    endtask

endinterface : pcie_tlp_rc_monitor_bfm

`endif
