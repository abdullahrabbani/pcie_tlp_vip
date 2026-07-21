// EP Monitor BFM
`ifndef PCIE_TLP_EP_MONITOR_BFM_SVH
`define PCIE_TLP_EP_MONITOR_BFM_SVH

import pcie_tlp_globals_pkg::*;
import uvm_pkg::*;
import pcie_tlp_ep_pkg::*;
`include "uvm_macros.svh"

interface pcie_tlp_ep_monitor_bfm (
    input logic clk,
    input logic rst_n,
    input  logic [63:0] tx_data,
    input  logic [7:0]  tx_keep,
    input  logic        tx_valid,
    input  logic        tx_ready,
    input  logic        tx_sop,
    input  logic        tx_eop,
    input  logic [2:0]  tx_empty,
    input  logic [3:0]  tx_seq_num,
    input  logic [1:0]  tx_vc_id,
    input  logic [2:0]  tx_tc,
    input  logic [63:0] rx_data,
    input  logic [7:0]  rx_keep,
    input  logic        rx_valid,
    input  logic        rx_ready,
    input  logic        rx_sop,
    input  logic        rx_eop,
    input  logic [2:0]  rx_empty,
    input  logic [3:0]  rx_seq_num,
    input  logic [1:0]  rx_vc_id,
    input  logic [2:0]  rx_tc
);

    string name = "PCIE_TLP_EP_MONITOR_BFM";
    pcie_tlp_ep_monitor_proxy ep_mon_proxy_h;

    initial begin
        `uvm_info(name, $sformatf("%s instantiated", name), UVM_LOW)
    end

    task wait_for_reset();
        @(negedge rst_n);
        `uvm_info(name, "Reset detected", UVM_HIGH)
        default_values();
        @(posedge rst_n);
        `uvm_info(name, "Reset deactivated", UVM_HIGH)
    endtask

    clocking mon_cb @(posedge clk);
        default input #1step output #1step;
        input  tx_data, tx_keep, tx_valid, tx_ready, tx_sop, tx_eop, tx_empty,
               tx_seq_num, tx_vc_id, tx_tc,
               rx_data, rx_keep, rx_valid, rx_ready, rx_sop, rx_eop, rx_empty,
               rx_seq_num, rx_vc_id, rx_tc;
    endclocking

    task default_values();
        // Monitor is a passive observer and must never drive tx_ready/rx_ready;
        // those are owned by the driver BFMs on each side of the link.
    endtask

    task automatic sample_request(output tlp_t req);
        automatic int payload_dwords;
        `uvm_info(name, "Sampling request TLP", UVM_HIGH)

        do begin
            @(mon_cb);
        end while (!(mon_cb.rx_valid && mon_cb.rx_sop));

        `uvm_info(name, "Request SOP detected", UVM_HIGH)

        req.header.dw0 = mon_cb.rx_data[31:0];
        req.header.dw1 = mon_cb.rx_data[63:32];
        @(mon_cb);
        req.header.dw2 = mon_cb.rx_data[31:0];
        req.header.dw3 = mon_cb.rx_data[63:32];

        payload_dwords = req.header.dw0[9:0];
        if (payload_dwords > 1) begin
            for (int i = 0; i < payload_dwords; i++) begin
                @(mon_cb);
                req.payload[i*8 +: 32] = mon_cb.rx_data[31:0];
                req.payload[i*8 + 32 +: 32] = mon_cb.rx_data[63:32];
            end
        end

        req.payload_size = payload_dwords * 4;
        req.transaction_id = mon_cb.rx_seq_num;
        req.timestamp = $time;

        `uvm_info(name, $sformatf("Sampled request TLP ID %0d, size %0d bytes",
                   req.transaction_id, req.payload_size), UVM_HIGH)
    endtask

    task automatic sample_completion(output tlp_t comp);
        automatic int payload_dwords;
        `uvm_info(name, "Sampling completion TLP", UVM_HIGH)

        do begin
            @(mon_cb);
        end while (!(mon_cb.tx_valid && mon_cb.tx_sop));

        `uvm_info(name, "Completion SOP detected", UVM_HIGH)

        comp.header.dw0 = mon_cb.tx_data[31:0];
        comp.header.dw1 = mon_cb.tx_data[63:32];
        @(mon_cb);
        comp.header.dw2 = mon_cb.tx_data[31:0];
        comp.header.dw3 = mon_cb.tx_data[63:32];

        payload_dwords = comp.header.dw0[9:0];
        if (payload_dwords > 1) begin
            for (int i = 0; i < payload_dwords; i++) begin
                @(mon_cb);
                comp.payload[i*8 +: 32] = mon_cb.tx_data[31:0];
                comp.payload[i*8 + 32 +: 32] = mon_cb.tx_data[63:32];
            end
        end

        comp.payload_size = payload_dwords * 4;
        comp.transaction_id = mon_cb.tx_seq_num;
        comp.timestamp = $time;

        `uvm_info(name, $sformatf("Sampled completion TLP ID %0d, size %0d bytes",
                   comp.transaction_id, comp.payload_size), UVM_HIGH)
    endtask

endinterface : pcie_tlp_ep_monitor_bfm

`endif
