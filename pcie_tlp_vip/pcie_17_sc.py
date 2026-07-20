#!/usr/bin/env python3
"""
PCIe TLP VIP Directory Structure Generator
Generates a complete UVM-based verification IP with full code.
All files have the 'pcie_tlp_' prefix for consistency.
"""

import os
import sys
import argparse

# ============================================================================
# FULL CODE FOR ALL FILES
# ============================================================================

# ========================= GLOBAL PACKAGE =============================
PCIE_TLP_GLOBALS_PKG_SV = r'''// PCIe TLP VIP - Global Package
`ifndef PCIE_TLP_GLOBALS_PKG_SVH
`define PCIE_TLP_GLOBALS_PKG_SVH

package pcie_tlp_globals_pkg;

    // TLP Format
    typedef enum logic [2:0] {
        TLP_FMT_MEM_READ  = 3'b000,
        TLP_FMT_MEM_WRITE = 3'b001,
        TLP_FMT_IO_READ   = 3'b010,
        TLP_FMT_IO_WRITE  = 3'b011,
        TLP_FMT_CFG_READ  = 3'b100,
        TLP_FMT_CFG_WRITE = 3'b101,
        TLP_FMT_MSG       = 3'b110,
        TLP_FMT_MSG_DATA  = 3'b111
    } tlp_fmt_e;

    // TLP Type
    typedef enum logic [5:0] {
        TLP_TYPE_MEM_RD   = 6'b000000,
        TLP_TYPE_MEM_WR   = 6'b000001,
        TLP_TYPE_IO_RD    = 6'b000010,
        TLP_TYPE_IO_WR    = 6'b000011,
        TLP_TYPE_CFG_RD   = 6'b000100,
        TLP_TYPE_CFG_WR   = 6'b000101,
        TLP_TYPE_MSG      = 6'b001000,
        TLP_TYPE_MSG_DATA = 6'b001001,
        TLP_TYPE_CMPL     = 6'b001010
    } tlp_type_e;

    // Write/Read data mode
    typedef enum {
        WRITE_READ_DATA,
        WRITE_ONLY,
        READ_ONLY
    } write_read_data_mode_e;

    // TLP Header
    typedef struct packed {
        logic [31:0] dw0;
        logic [31:0] dw1;
        logic [31:0] dw2;
        logic [31:0] dw3;
    } tlp_header_t;

    // TLP Transaction
    typedef struct {
        tlp_header_t    header;
        logic [1023:0]  payload;
        int             payload_size;
        int             transaction_id;
        time            timestamp;
    } tlp_t;

    // Configuration Space
    typedef struct packed {
        logic [15:0] vendor_id;
        logic [15:0] device_id;
        logic [15:0] command;
        logic [15:0] status;
        logic [31:0] class_code;
        logic [31:0] base_address_0;
        logic [31:0] base_address_1;
    } pcie_tlp_config_space_t;

    // Parameters
    parameter PCIE_TLP_MAX_PAYLOAD = 256;
    parameter PCIE_TLP_TIMEOUT     = 1000;

    // Utility functions
    function automatic tlp_fmt_e get_tlp_fmt(tlp_t t);
        return tlp_fmt_e'(t.header.dw0[30:28]);
    endfunction

    function automatic tlp_type_e get_tlp_type(tlp_t t);
        return tlp_type_e'(t.header.dw0[24:19]);
    endfunction

endpackage

`endif
'''

# ========================= INTERFACE ===================================
PCIE_TLP_IF_SV = r'''// PCIe TLP Interface
`ifndef PCIE_TLP_IF_SVH
`define PCIE_TLP_IF_SVH

import pcie_tlp_globals_pkg::*;

interface pcie_tlp_if #(
    parameter DATA_WIDTH = 64,
    parameter KEEP_WIDTH = DATA_WIDTH/8
) (
    input logic clk,
    input logic rst_n
);

    logic [DATA_WIDTH-1:0] tx_data;
    logic [KEEP_WIDTH-1:0] tx_keep;
    logic                  tx_valid;
    logic                  tx_ready;
    logic                  tx_sop;
    logic                  tx_eop;
    logic [2:0]            tx_empty;
    logic [3:0]            tx_seq_num;
    logic [1:0]            tx_vc_id;
    logic [2:0]            tx_tc;

    logic [DATA_WIDTH-1:0] rx_data;
    logic [KEEP_WIDTH-1:0] rx_keep;
    logic                  rx_valid;
    logic                  rx_ready;
    logic                  rx_sop;
    logic                  rx_eop;
    logic [2:0]            rx_empty;
    logic [3:0]            rx_seq_num;
    logic [1:0]            rx_vc_id;
    logic [2:0]            rx_tc;

    clocking driver_cb @(posedge clk);
        default input #1ns output #1ns;
        output tx_data;
        output tx_keep;
        output tx_valid;
        input  tx_ready;
        output tx_sop;
        output tx_eop;
        output tx_empty;
        output tx_seq_num;
        output tx_vc_id;
        output tx_tc;
        input  rx_data;
        input  rx_keep;
        input  rx_valid;
        output rx_ready;
        input  rx_sop;
        input  rx_eop;
        input  rx_empty;
        input  rx_seq_num;
        input  rx_vc_id;
        input  rx_tc;
    endclocking

    clocking monitor_cb @(posedge clk);
        default input #1ns output #1ns;
        input  tx_data;
        input  tx_keep;
        input  tx_valid;
        output tx_ready;
        input  tx_sop;
        input  tx_eop;
        input  tx_empty;
        input  tx_seq_num;
        input  tx_vc_id;
        input  tx_tc;
        input  rx_data;
        input  rx_keep;
        input  rx_valid;
        output rx_ready;
        input  rx_sop;
        input  rx_eop;
        input  rx_empty;
        input  rx_seq_num;
        input  rx_vc_id;
        input  rx_tc;
    endclocking

    modport DRIVER (
        clocking driver_cb,
        input clk,
        input rst_n
    );

    modport MONITOR (
        clocking monitor_cb,
        input clk,
        input rst_n
    );

    modport PASSIVE (
        input clk,
        input rst_n,
        input tx_data,
        input tx_keep,
        input tx_valid,
        output tx_ready,
        input tx_sop,
        input tx_eop,
        input tx_empty,
        input tx_seq_num,
        input tx_vc_id,
        input tx_tc,
        input rx_data,
        input rx_keep,
        input rx_valid,
        output rx_ready,
        input rx_sop,
        input rx_eop,
        input rx_empty,
        input rx_seq_num,
        input rx_vc_id,
        input rx_tc
    );

    task send_tlp(input tlp_t t);
        $display("[%t] Sending TLP via interface", $time);
    endtask

    task receive_tlp(output tlp_t t);
        $display("[%t] Receiving TLP via interface", $time);
    endtask

    initial begin
        tx_data = '0;
        tx_keep = '0;
        tx_valid = 1'b0;
        tx_ready = 1'b0;
        tx_sop = 1'b0;
        tx_eop = 1'b0;
        tx_empty = 3'b0;
        tx_seq_num = 4'b0;
        tx_vc_id = 2'b0;
        tx_tc = 3'b0;
        rx_data = '0;
        rx_keep = '0;
        rx_valid = 1'b0;
        rx_ready = 1'b0;
        rx_sop = 1'b0;
        rx_eop = 1'b0;
        rx_empty = 3'b0;
        rx_seq_num = 4'b0;
        rx_vc_id = 2'b0;
        rx_tc = 3'b0;
    end

endinterface : pcie_tlp_if

`endif
'''

# ========================= RC AGENT BFM FILES =========================
PCIE_TLP_RC_AGENT_BFM_SV = r'''// RC Agent BFM
`ifndef PCIE_TLP_RC_AGENT_BFM_SVH
`define PCIE_TLP_RC_AGENT_BFM_SVH

import uvm_pkg::*;
`include "uvm_macros.svh"
import pcie_tlp_globals_pkg::*;
import pcie_tlp_rc_pkg::*;

module pcie_tlp_rc_agent_bfm #(parameter int RC_ID = 0)(
    pcie_tlp_if intf
);

    pcie_tlp_rc_driver_bfm rc_drv_bfm (
        .clk(intf.clk),
        .rst_n(intf.rst_n),
        .tx_data(intf.tx_data),
        .tx_keep(intf.tx_keep),
        .tx_valid(intf.tx_valid),
        .tx_ready(intf.tx_ready),
        .tx_sop(intf.tx_sop),
        .tx_eop(intf.tx_eop),
        .tx_empty(intf.tx_empty),
        .tx_seq_num(intf.tx_seq_num),
        .tx_vc_id(intf.tx_vc_id),
        .tx_tc(intf.tx_tc),
        .rx_data(intf.rx_data),
        .rx_keep(intf.rx_keep),
        .rx_valid(intf.rx_valid),
        .rx_ready(intf.rx_ready),
        .rx_sop(intf.rx_sop),
        .rx_eop(intf.rx_eop),
        .rx_empty(intf.rx_empty),
        .rx_seq_num(intf.rx_seq_num),
        .rx_vc_id(intf.rx_vc_id),
        .rx_tc(intf.rx_tc)
    );

    pcie_tlp_rc_monitor_bfm rc_mon_bfm (
        .clk(intf.clk),
        .rst_n(intf.rst_n),
        .tx_data(intf.tx_data),
        .tx_keep(intf.tx_keep),
        .tx_valid(intf.tx_valid),
        .tx_ready(intf.tx_ready),
        .tx_sop(intf.tx_sop),
        .tx_eop(intf.tx_eop),
        .tx_empty(intf.tx_empty),
        .tx_seq_num(intf.tx_seq_num),
        .tx_vc_id(intf.tx_vc_id),
        .tx_tc(intf.tx_tc),
        .rx_data(intf.rx_data),
        .rx_keep(intf.rx_keep),
        .rx_valid(intf.rx_valid),
        .rx_ready(intf.rx_ready),
        .rx_sop(intf.rx_sop),
        .rx_eop(intf.rx_eop),
        .rx_empty(intf.rx_empty),
        .rx_seq_num(intf.rx_seq_num),
        .rx_vc_id(intf.rx_vc_id),
        .rx_tc(intf.rx_tc)
    );

    initial begin
        uvm_config_db#(virtual pcie_tlp_rc_driver_bfm)::set(null, "*", "pcie_tlp_rc_driver_bfm", rc_drv_bfm);
        uvm_config_db#(virtual pcie_tlp_rc_monitor_bfm)::set(null, "*", "pcie_tlp_rc_monitor_bfm", rc_mon_bfm);
        `uvm_info("PCIE_TLP_RC_AGENT_BFM", $sformatf("RC Agent BFM instantiated with ID %0d", RC_ID), UVM_LOW)
    end

endmodule : pcie_tlp_rc_agent_bfm

`endif
'''

PCIE_TLP_RC_DRIVER_BFM_SV = r'''// RC Driver BFM
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
'''

PCIE_TLP_RC_MONITOR_BFM_SV = r'''// RC Monitor BFM
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
'''

# ========================= EP AGENT BFM FILES =========================
PCIE_TLP_EP_AGENT_BFM_SV = r'''// EP Agent BFM
`ifndef PCIE_TLP_EP_AGENT_BFM_SVH
`define PCIE_TLP_EP_AGENT_BFM_SVH

import uvm_pkg::*;
`include "uvm_macros.svh"
import pcie_tlp_globals_pkg::*;
import pcie_tlp_ep_pkg::*;

module pcie_tlp_ep_agent_bfm #(parameter int EP_ID = 0)(
    pcie_tlp_if intf
);

    pcie_tlp_ep_driver_bfm ep_drv_bfm (
        .clk(intf.clk),
        .rst_n(intf.rst_n),
        .tx_data(intf.tx_data),
        .tx_keep(intf.tx_keep),
        .tx_valid(intf.tx_valid),
        .tx_ready(intf.tx_ready),
        .tx_sop(intf.tx_sop),
        .tx_eop(intf.tx_eop),
        .tx_empty(intf.tx_empty),
        .tx_seq_num(intf.tx_seq_num),
        .tx_vc_id(intf.tx_vc_id),
        .tx_tc(intf.tx_tc),
        .rx_data(intf.rx_data),
        .rx_keep(intf.rx_keep),
        .rx_valid(intf.rx_valid),
        .rx_ready(intf.rx_ready),
        .rx_sop(intf.rx_sop),
        .rx_eop(intf.rx_eop),
        .rx_empty(intf.rx_empty),
        .rx_seq_num(intf.rx_seq_num),
        .rx_vc_id(intf.rx_vc_id),
        .rx_tc(intf.rx_tc)
    );

    pcie_tlp_ep_monitor_bfm ep_mon_bfm (
        .clk(intf.clk),
        .rst_n(intf.rst_n),
        .tx_data(intf.tx_data),
        .tx_keep(intf.tx_keep),
        .tx_valid(intf.tx_valid),
        .tx_ready(intf.tx_ready),
        .tx_sop(intf.tx_sop),
        .tx_eop(intf.tx_eop),
        .tx_empty(intf.tx_empty),
        .tx_seq_num(intf.tx_seq_num),
        .tx_vc_id(intf.tx_vc_id),
        .tx_tc(intf.tx_tc),
        .rx_data(intf.rx_data),
        .rx_keep(intf.rx_keep),
        .rx_valid(intf.rx_valid),
        .rx_ready(intf.rx_ready),
        .rx_sop(intf.rx_sop),
        .rx_eop(intf.rx_eop),
        .rx_empty(intf.rx_empty),
        .rx_seq_num(intf.rx_seq_num),
        .rx_vc_id(intf.rx_vc_id),
        .rx_tc(intf.rx_tc)
    );

    initial begin
        uvm_config_db#(virtual pcie_tlp_ep_driver_bfm)::set(null, "*", "pcie_tlp_ep_driver_bfm", ep_drv_bfm);
        uvm_config_db#(virtual pcie_tlp_ep_monitor_bfm)::set(null, "*", "pcie_tlp_ep_monitor_bfm", ep_mon_bfm);
        `uvm_info("PCIE_TLP_EP_AGENT_BFM", $sformatf("EP Agent BFM instantiated with ID %0d", EP_ID), UVM_LOW)
    end

endmodule : pcie_tlp_ep_agent_bfm

`endif
'''

PCIE_TLP_EP_DRIVER_BFM_SV = r'''// EP Driver BFM
`ifndef PCIE_TLP_EP_DRIVER_BFM_SVH
`define PCIE_TLP_EP_DRIVER_BFM_SVH

import pcie_tlp_globals_pkg::*;
import uvm_pkg::*;
`include "uvm_macros.svh"

interface pcie_tlp_ep_driver_bfm (
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

    string name = "PCIE_TLP_EP_DRIVER_BFM";

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

    task automatic sample_request(output tlp_t req);
        automatic int payload_dwords;
        `uvm_info(name, "Sampling request", UVM_HIGH)
        drv_cb.rx_ready <= 1'b1;

        do begin
            @(drv_cb);
        end while (!(drv_cb.rx_valid && drv_cb.rx_sop));

        req.header.dw0 = drv_cb.rx_data[31:0];
        req.header.dw1 = drv_cb.rx_data[63:32];
        @(drv_cb);
        req.header.dw2 = drv_cb.rx_data[31:0];
        req.header.dw3 = drv_cb.rx_data[63:32];

        payload_dwords = req.header.dw0[9:0];
        if (payload_dwords > 1) begin
            for (int i = 0; i < payload_dwords; i++) begin
                @(drv_cb);
                req.payload[i*8 +: 32] = drv_cb.rx_data[31:0];
                req.payload[i*8 + 32 +: 32] = drv_cb.rx_data[63:32];
            end
        end

        req.payload_size = payload_dwords * 4;
        req.transaction_id = drv_cb.rx_seq_num;
        req.timestamp = $time;

        @(drv_cb);
        drv_cb.rx_ready <= 1'b0;

        `uvm_info(name, $sformatf("Sampled request TLP ID %0d, size %0d bytes",
                   req.transaction_id, req.payload_size), UVM_HIGH)
    endtask

    task automatic send_completion(
        input tlp_t comp_tlp,
        input int wait_states = 0
    );
        automatic int payload_words;
        automatic int total_beats;
        payload_words = (comp_tlp.payload_size + 3) / 4;
        total_beats = 1 + payload_words;

        `uvm_info(name, $sformatf("Sending completion TLP ID %0d, %0d beats",
                    comp_tlp.transaction_id, total_beats), UVM_HIGH)

        wait_for_reset();
        repeat (wait_states) @(drv_cb);

        @(drv_cb);
        drv_cb.tx_data    <= {comp_tlp.header.dw3, comp_tlp.header.dw2,
                              comp_tlp.header.dw1, comp_tlp.header.dw0};
        drv_cb.tx_keep    <= 8'hFF;
        drv_cb.tx_valid   <= 1'b1;
        drv_cb.tx_sop     <= 1'b1;
        drv_cb.tx_eop     <= 1'b0;
        drv_cb.tx_empty   <= 3'b0;
        drv_cb.tx_seq_num <= comp_tlp.transaction_id[3:0];
        drv_cb.tx_vc_id   <= 2'b0;
        drv_cb.tx_tc      <= 3'b0;

        do begin
            @(drv_cb);
        end while (drv_cb.tx_ready !== 1'b1);

        for (int i = 0; i < payload_words; i++) begin
            logic [31:0] word;
            word = comp_tlp.payload[i*4 +: 32];
            @(drv_cb);
            drv_cb.tx_data    <= {32'h0, word};
            drv_cb.tx_keep    <= 8'h0F;
            drv_cb.tx_valid   <= 1'b1;
            drv_cb.tx_sop     <= 1'b0;
            drv_cb.tx_eop     <= (i == payload_words-1) ? 1'b1 : 1'b0;
            drv_cb.tx_empty   <= 3'b0;
            drv_cb.tx_seq_num <= comp_tlp.transaction_id[3:0];
            drv_cb.tx_vc_id   <= 2'b0;
            drv_cb.tx_tc      <= 3'b0;

            do begin
                @(drv_cb);
            end while (drv_cb.tx_ready !== 1'b1);
        end

        @(drv_cb);
        default_values();

        `uvm_info(name, $sformatf("Completion TLP ID %0d sent", comp_tlp.transaction_id), UVM_HIGH)
    endtask

endinterface : pcie_tlp_ep_driver_bfm

`endif
'''

PCIE_TLP_EP_MONITOR_BFM_SV = r'''// EP Monitor BFM
`ifndef PCIE_TLP_EP_MONITOR_BFM_SVH
`define PCIE_TLP_EP_MONITOR_BFM_SVH

import pcie_tlp_globals_pkg::*;
import uvm_pkg::*;
`include "uvm_macros.svh"

interface pcie_tlp_ep_monitor_bfm (
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

    string name = "PCIE_TLP_EP_MONITOR_BFM";

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

    task automatic sample_request(output tlp_t req);
        automatic int payload_dwords;
        `uvm_info(name, "Sampling request TLP", UVM_HIGH)
        mon_cb.rx_ready <= 1'b1;

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

        @(mon_cb);
        mon_cb.rx_ready <= 1'b0;

        `uvm_info(name, $sformatf("Sampled request TLP ID %0d, size %0d bytes",
                   req.transaction_id, req.payload_size), UVM_HIGH)
    endtask

    task automatic sample_completion(output tlp_t comp);
        automatic int payload_dwords;
        `uvm_info(name, "Sampling completion TLP", UVM_HIGH)
        mon_cb.tx_ready <= 1'b1;

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

        @(mon_cb);
        mon_cb.tx_ready <= 1'b0;

        `uvm_info(name, $sformatf("Sampled completion TLP ID %0d, size %0d bytes",
                   comp.transaction_id, comp.payload_size), UVM_HIGH)
    endtask

endinterface : pcie_tlp_ep_monitor_bfm

`endif
'''

# ========================= HDL TOP =========================
PCIE_TLP_HDL_TOP_SV = r'''// HDL Top
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
    initial begin #1000; `uvm_info("HDL_TOP", "Simulation finished", UVM_LOW); $finish; end
endmodule
`endif
'''

# ========================= ASSERTIONS (DISABLED) =========================
PCIE_TLP_RC_ASSERTIONS_SV = r'''// RC Assertions (DISABLED)
`ifndef PCIE_TLP_RC_ASSERTIONS_SVH
`define PCIE_TLP_RC_ASSERTIONS_SVH

import pcie_tlp_globals_pkg::*;
import uvm_pkg::*;
`include "uvm_macros.svh"

interface pcie_tlp_rc_assertions (
    input logic clk,
    input logic rst_n,
    input logic [63:0] tx_data,
    input logic [7:0]  tx_keep,
    input logic        tx_valid,
    input logic        tx_ready,
    input logic        tx_sop,
    input logic        tx_eop,
    input logic [2:0]  tx_empty,
    input logic [3:0]  tx_seq_num,
    input logic [1:0]  tx_vc_id,
    input logic [2:0]  tx_tc,
    input logic [63:0] rx_data,
    input logic [7:0]  rx_keep,
    input logic        rx_valid,
    input logic        rx_ready,
    input logic        rx_sop,
    input logic        rx_eop,
    input logic [2:0]  rx_empty,
    input logic [3:0]  rx_seq_num,
    input logic [1:0]  rx_vc_id,
    input logic [2:0]  rx_tc
);

    // ALL ASSERTIONS ARE DISABLED
    function automatic tlp_header_t get_tx_header();
        tlp_header_t h;
        h.dw0[30:28] = tx_data[30:28];
        h.dw0[24:19] = tx_data[24:19];
        h.dw0[9:0]   = tx_data[9:0];
        h.dw1        = tx_data[63:32];
        h.dw2        = 32'h0;
        h.dw3        = 32'h0;
        return h;
    endfunction

    function automatic tlp_fmt_e get_tlp_fmt_from_header(tlp_header_t h);
        return tlp_fmt_e'(h.dw0[30:28]);
    endfunction

    function automatic tlp_type_e get_tlp_type_from_header(tlp_header_t h);
        return tlp_type_e'(h.dw0[24:19]);
    endfunction

endinterface : pcie_tlp_rc_assertions

`endif
'''

PCIE_TLP_EP_ASSERTIONS_SV = r'''// EP Assertions (DISABLED)
`ifndef PCIE_TLP_EP_ASSERTIONS_SVH
`define PCIE_TLP_EP_ASSERTIONS_SVH

import pcie_tlp_globals_pkg::*;
import uvm_pkg::*;
`include "uvm_macros.svh"

interface pcie_tlp_ep_assertions (
    input logic clk,
    input logic rst_n,
    input logic [63:0] tx_data,
    input logic [7:0]  tx_keep,
    input logic        tx_valid,
    input logic        tx_ready,
    input logic        tx_sop,
    input logic        tx_eop,
    input logic [2:0]  tx_empty,
    input logic [3:0]  tx_seq_num,
    input logic [1:0]  tx_vc_id,
    input logic [2:0]  tx_tc,
    input logic [63:0] rx_data,
    input logic [7:0]  rx_keep,
    input logic        rx_valid,
    input logic        rx_ready,
    input logic        rx_sop,
    input logic        rx_eop,
    input logic [2:0]  rx_empty,
    input logic [3:0]  rx_seq_num,
    input logic [1:0]  rx_vc_id,
    input logic [2:0]  rx_tc
);

    // ALL ASSERTIONS ARE DISABLED
    function automatic tlp_header_t get_rx_header();
        tlp_header_t h;
        h.dw0[30:28] = rx_data[30:28];
        h.dw0[24:19] = rx_data[24:19];
        h.dw0[9:0]   = rx_data[9:0];
        h.dw1        = rx_data[63:32];
        h.dw2        = 32'h0;
        h.dw3        = 32'h0;
        return h;
    endfunction

    function automatic tlp_fmt_e get_tlp_fmt_from_header(tlp_header_t h);
        return tlp_fmt_e'(h.dw0[30:28]);
    endfunction

    function automatic tlp_type_e get_tlp_type_from_header(tlp_header_t h);
        return tlp_type_e'(h.dw0[24:19]);
    endfunction

endinterface : pcie_tlp_ep_assertions

`endif
'''

PCIE_TLP_TB_RC_ASSERTIONS_SV = r'''// TB RC Assertions (DISABLED)
`ifndef PCIE_TLP_TB_RC_ASSERTIONS_SVH
`define PCIE_TLP_TB_RC_ASSERTIONS_SVH

import pcie_tlp_globals_pkg::*;
import uvm_pkg::*;
`include "uvm_macros.svh"

module pcie_tlp_tb_rc_assertions;

    logic clk;
    logic rst_n;
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

    pcie_tlp_rc_assertions rc_assertions_inst (
        .clk(clk),
        .rst_n(rst_n),
        .tx_data(tx_data),
        .tx_keep(tx_keep),
        .tx_valid(tx_valid),
        .tx_ready(tx_ready),
        .tx_sop(tx_sop),
        .tx_eop(tx_eop),
        .tx_empty(tx_empty),
        .tx_seq_num(tx_seq_num),
        .tx_vc_id(tx_vc_id),
        .tx_tc(tx_tc),
        .rx_data(rx_data),
        .rx_keep(rx_keep),
        .rx_valid(rx_valid),
        .rx_ready(rx_ready),
        .rx_sop(rx_sop),
        .rx_eop(rx_eop),
        .rx_empty(rx_empty),
        .rx_seq_num(rx_seq_num),
        .rx_vc_id(rx_vc_id),
        .rx_tc(rx_tc)
    );

    initial begin clk = 1'b0; forever #5 clk = ~clk; end

    task reset_gen();
        rst_n = 1'b0; @(posedge clk); @(posedge clk); rst_n = 1'b1;
        `uvm_info("TB_RC_ASSERT", "Reset deasserted", UVM_LOW)
    endtask

    task automatic drive_tx_tlp(input tlp_header_t header, input int payload_size = 0);
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

    task automatic drive_rx_completion(input tlp_header_t header, input int payload_size = 0);
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

    initial begin
        `uvm_info("TB_RC_ASSERT", "Starting RC assertions testbench (DISABLED)", UVM_LOW);
        #100;
        `uvm_info("TB_RC_ASSERT", "RC assertions testbench completed", UVM_LOW);
        $finish;
    end

endmodule

`endif
'''

PCIE_TLP_TB_EP_ASSERTIONS_SV = r'''// TB EP Assertions (DISABLED)
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
'''

# ========================= COVERAGE (DISABLED) =========================
PCIE_TLP_RC_COVERAGE_SV = r'''// RC Coverage Collector (DISABLED)
`ifndef PCIE_TLP_RC_COVERAGE_SVH
`define PCIE_TLP_RC_COVERAGE_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*; import pcie_tlp_rc_pkg::*;

class pcie_tlp_rc_coverage extends uvm_component;
    `uvm_component_utils(pcie_tlp_rc_coverage)

    uvm_analysis_imp #(pcie_tlp_rc_tx, pcie_tlp_rc_coverage) analysis_imp;
    pcie_tlp_rc_agent_config cfg;

    function new(string name = "pcie_tlp_rc_coverage", uvm_component parent = null);
        super.new(name, parent);
        analysis_imp = new("analysis_imp", this);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        if (!uvm_config_db#(pcie_tlp_rc_agent_config)::get(this, "", "cfg", cfg)) begin
            `uvm_info(get_type_name(), "No config set, using default ranges", UVM_LOW)
        end
    endfunction

    function void write(pcie_tlp_rc_tx tx);
        `uvm_info(get_type_name(), $sformatf("Coverage disabled for TLP ID %0d", tx.transaction_id), UVM_HIGH)
    endfunction

endclass

`endif
'''

PCIE_TLP_EP_COVERAGE_SV = r'''// EP Coverage Collector (DISABLED)
`ifndef PCIE_TLP_EP_COVERAGE_SVH
`define PCIE_TLP_EP_COVERAGE_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*; import pcie_tlp_ep_pkg::*;

class pcie_tlp_ep_coverage extends uvm_subscriber #(pcie_tlp_ep_tx);
    `uvm_component_utils(pcie_tlp_ep_coverage)
    pcie_tlp_ep_agent_config cfg;

    function new(string name = "pcie_tlp_ep_coverage", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        if (!uvm_config_db#(pcie_tlp_ep_agent_config)::get(this, "", "cfg", cfg)) begin
            `uvm_info(get_type_name(), "No configuration set, using defaults", UVM_LOW)
        end
    endfunction

    function void write(pcie_tlp_ep_tx t);
        `uvm_info(get_type_name(), $sformatf("Coverage disabled for EP TLP ID %0d", t.transaction_id), UVM_HIGH)
    endfunction

    function void report_phase(uvm_phase phase);
        `uvm_info(get_type_name(), "Coverage disabled", UVM_NONE)
    endfunction

endclass

`endif
'''

# ========================= RC HVL FILES =========================
PCIE_TLP_RC_AGENT_CONFIG_SV = r'''// RC Agent Configuration
`ifndef PCIE_TLP_RC_AGENT_CONFIG_SVH
`define PCIE_TLP_RC_AGENT_CONFIG_SVH

import uvm_pkg::*; `include "uvm_macros.svh"
import pcie_tlp_globals_pkg::*;

class pcie_tlp_rc_agent_config extends uvm_object;
    `uvm_object_utils(pcie_tlp_rc_agent_config)
    uvm_active_passive_enum is_active = UVM_ACTIVE;
    bit has_coverage = 1'b0;
    int num_transactions = 10;
    int max_payload_size = PCIE_TLP_MAX_PAYLOAD;
    bit flow_control_enabled = 1'b1;
    int wait_states = 0;
    int outstanding_write_tx = 4;
    int outstanding_read_tx  = 4;
    int address_range_min[int];
    int address_range_max[int];

    function new(string name = "pcie_tlp_rc_agent_config");
        super.new(name);
    endfunction

    function void set_min_address_range(int target_id, int min_addr);
        address_range_min[target_id] = min_addr;
    endfunction

    function void set_max_address_range(int target_id, int max_addr);
        address_range_max[target_id] = max_addr;
    endfunction

    function int get_min_address_range(int target_id);
        if (address_range_min.exists(target_id))
            return address_range_min[target_id];
        else
            return 0;
    endfunction

    function int get_max_address_range(int target_id);
        if (address_range_max.exists(target_id))
            return address_range_max[target_id];
        else
            return 0;
    endfunction

    function void do_print(uvm_printer printer);
        super.do_print(printer);
        printer.print_string("is_active", is_active.name());
        printer.print_field("has_coverage", has_coverage, $bits(has_coverage), UVM_BIN);
        printer.print_field("num_transactions", num_transactions, $bits(num_transactions), UVM_DEC);
        printer.print_field("max_payload_size", max_payload_size, $bits(max_payload_size), UVM_DEC);
        printer.print_field("flow_control_enabled", flow_control_enabled, $bits(flow_control_enabled), UVM_BIN);
        printer.print_field("wait_states", wait_states, $bits(wait_states), UVM_DEC);
        printer.print_field("outstanding_write_tx", outstanding_write_tx, $bits(outstanding_write_tx), UVM_DEC);
        printer.print_field("outstanding_read_tx", outstanding_read_tx, $bits(outstanding_read_tx), UVM_DEC);
        foreach (address_range_min[i]) begin
            printer.print_field($sformatf("address_range_min[%0d]", i),
                                address_range_min[i],
                                $bits(address_range_min[i]), UVM_HEX);
        end
        foreach (address_range_max[i]) begin
            printer.print_field($sformatf("address_range_max[%0d]", i),
                                address_range_max[i],
                                $bits(address_range_max[i]), UVM_HEX);
        end
    endfunction

endclass

`endif
'''

PCIE_TLP_RC_TX_SV = r'''// RC Transaction
`ifndef PCIE_TLP_RC_TX_SVH
`define PCIE_TLP_RC_TX_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*;

class pcie_tlp_rc_tx extends uvm_sequence_item;
    `uvm_object_utils(pcie_tlp_rc_tx)

    rand tlp_fmt_e   fmt;
    rand tlp_type_e  typ;
    rand logic [9:0] length;
    rand logic [31:0] address;
    rand logic [31:0] tag;
    rand logic [2:0]  tc;
    rand logic [1:0]  vc_id;
    rand logic [3:0]  seq_num;
    rand logic [1023:0] payload;
    rand int             payload_size;
    rand int             transaction_id;
    rand int             wait_states;

    tlp_t tlp;

    int addr_pool[$];
    int avoid_base[$];
    int avoid_span[$];
    int readback_base[$];

    constraint payload_size_c {
        payload_size % 4 == 0;
        payload_size / 4 == length;
        length inside {[0:PCIE_TLP_MAX_PAYLOAD]};
    }

    constraint fmt_type_c {
        (fmt == TLP_FMT_MEM_READ)  -> typ inside {TLP_TYPE_MEM_RD};
        (fmt == TLP_FMT_MEM_WRITE) -> typ inside {TLP_TYPE_MEM_WR};
        (fmt == TLP_FMT_CFG_READ)  -> typ inside {TLP_TYPE_CFG_RD};
        (fmt == TLP_FMT_CFG_WRITE) -> typ inside {TLP_TYPE_CFG_WR};
        (fmt == TLP_FMT_IO_READ)   -> typ inside {TLP_TYPE_IO_RD};
        (fmt == TLP_FMT_IO_WRITE)  -> typ inside {TLP_TYPE_IO_WR};
        (fmt == TLP_FMT_MSG)       -> typ inside {TLP_TYPE_MSG};
        (fmt == TLP_FMT_MSG_DATA)  -> typ inside {TLP_TYPE_MSG_DATA};
    }

    constraint addr_aligned_c {
        (fmt inside {TLP_FMT_MEM_READ, TLP_FMT_MEM_WRITE}) -> (address[1:0] == 2'b00);
    }

    constraint tag_c { tag inside {[0:31]}; }
    constraint trans_id_c { transaction_id > 0; }
    constraint wait_states_c { wait_states inside {[0:5]}; }

    function new(string name = "pcie_tlp_rc_tx");
        super.new(name);
        fmt = TLP_FMT_MEM_READ;
        typ = TLP_TYPE_MEM_RD;
        length = 1;
        address = 32'h0000_0000;
        tag = 0;
        tc = 0;
        vc_id = 0;
        seq_num = 0;
        payload = '0;
        payload_size = 4;
        transaction_id = 1;
        wait_states = 0;
    endfunction

    function void post_randomize();
        tlp.header.dw0[30:28] = fmt;
        tlp.header.dw0[24:19] = typ;
        tlp.header.dw0[9:0]   = length;
        tlp.header.dw1 = address;
        tlp.header.dw2 = {tc, 5'b0, tag[7:0]};
        tlp.header.dw3 = {vc_id, seq_num, 26'b0};
        if (payload_size > 0) tlp.payload = payload;
        else tlp.payload = '0;
        tlp.payload_size = payload_size;
        tlp.transaction_id = transaction_id;
        tlp.timestamp = $time;
    endfunction

    function void do_copy(uvm_object rhs);
        pcie_tlp_rc_tx copy_obj;
        if (!$cast(copy_obj, rhs)) `uvm_fatal("do_copy", "cast failed")
        super.do_copy(rhs);
        fmt = copy_obj.fmt; typ = copy_obj.typ; length = copy_obj.length;
        address = copy_obj.address; tag = copy_obj.tag; tc = copy_obj.tc;
        vc_id = copy_obj.vc_id; seq_num = copy_obj.seq_num;
        payload = copy_obj.payload; payload_size = copy_obj.payload_size;
        transaction_id = copy_obj.transaction_id; wait_states = copy_obj.wait_states;
        tlp = copy_obj.tlp;
    endfunction

    function bit do_compare(uvm_object rhs, uvm_comparer comparer);
        pcie_tlp_rc_tx cmp_obj;
        if (!$cast(cmp_obj, rhs)) return 0;
        return super.do_compare(rhs, comparer) &&
               (fmt == cmp_obj.fmt) && (typ == cmp_obj.typ) &&
               (length == cmp_obj.length) && (address == cmp_obj.address) &&
               (tag == cmp_obj.tag) && (tc == cmp_obj.tc) &&
               (vc_id == cmp_obj.vc_id) && (seq_num == cmp_obj.seq_num) &&
               (payload == cmp_obj.payload) && (payload_size == cmp_obj.payload_size) &&
               (transaction_id == cmp_obj.transaction_id) &&
               (wait_states == cmp_obj.wait_states);
    endfunction

    function void do_print(uvm_printer printer);
        super.do_print(printer);
        printer.print_string("fmt", fmt.name());
        printer.print_string("typ", typ.name());
        printer.print_field("length", length, $bits(length), UVM_DEC);
        printer.print_field("address", address, $bits(address), UVM_HEX);
        printer.print_field("tag", tag, $bits(tag), UVM_HEX);
        printer.print_field("tc", tc, $bits(tc), UVM_DEC);
        printer.print_field("vc_id", vc_id, $bits(vc_id), UVM_DEC);
        printer.print_field("seq_num", seq_num, $bits(seq_num), UVM_DEC);
        printer.print_field("payload_size", payload_size, $bits(payload_size), UVM_DEC);
        printer.print_field("transaction_id", transaction_id, $bits(transaction_id), UVM_DEC);
        printer.print_field("wait_states", wait_states, $bits(wait_states), UVM_DEC);
        if (payload_size > 0) begin
            int words = (payload_size + 3) / 4;
            for (int i = 0; i < words && i < 8; i++) begin
                printer.print_field($sformatf("payload[%0d]", i), payload[i*32 +: 32], 32, UVM_HEX);
            end
            if (words > 8) printer.print_string("payload", "... (more)");
        end
    endfunction

endclass

`endif
'''

PCIE_TLP_RC_SEQ_ITEM_CONVERTER_SV = r'''// RC Sequence Item Converter
`ifndef PCIE_TLP_RC_SEQ_ITEM_CONVERTER_SVH
`define PCIE_TLP_RC_SEQ_ITEM_CONVERTER_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*; import pcie_tlp_rc_pkg::*;

class pcie_tlp_rc_seq_item_converter extends uvm_object;
    `uvm_object_utils(pcie_tlp_rc_seq_item_converter)

    function new(string name = "pcie_tlp_rc_seq_item_converter");
        super.new(name);
    endfunction

    static function void from_tx_class(input pcie_tlp_rc_tx tx, output tlp_t tlp);
        tlp.header.dw0[30:28] = tx.fmt;
        tlp.header.dw0[24:19] = tx.typ;
        tlp.header.dw0[9:0]   = tx.length;
        tlp.header.dw1        = tx.address;
        tlp.header.dw2        = {tx.tc, 5'b0, tx.tag[7:0]};
        tlp.header.dw3        = {tx.vc_id, tx.seq_num, 26'b0};
        tlp.payload     = tx.payload;
        tlp.payload_size = tx.payload_size;
        tlp.transaction_id = tx.transaction_id;
        tlp.timestamp     = tx.tlp.timestamp;
    endfunction

    static function void to_tx_class(input tlp_t tlp, output pcie_tlp_rc_tx tx);
        tx.fmt   = tlp_fmt_e'(tlp.header.dw0[30:28]);
        tx.typ   = tlp_type_e'(tlp.header.dw0[24:19]);
        tx.length = tlp.header.dw0[9:0];
        tx.address = tlp.header.dw1;
        tx.tag   = tlp.header.dw2[7:0];
        tx.tc    = tlp.header.dw2[14:12];
        tx.vc_id = tlp.header.dw3[27:26];
        tx.seq_num = tlp.header.dw3[23:20];
        tx.payload     = tlp.payload;
        tx.payload_size = tlp.payload_size;
        tx.transaction_id = tlp.transaction_id;
        tx.tlp = tlp;
    endfunction

endclass

`endif
'''

PCIE_TLP_RC_COVERNTER_CONFIG_SV = r'''// RC Configuration Converter
`ifndef PCIE_TLP_RC_COVERNTER_CONFIG_SVH
`define PCIE_TLP_RC_COVERNTER_CONFIG_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*; import pcie_tlp_rc_pkg::*;

typedef struct {
    int num_transactions;
    int start_address;
    int end_address;
    bit is_active;
    int max_payload_size;
    int wait_states;
    bit flow_control_enabled;
    int outstanding_limit;
} pcie_tlp_rc_cfg_s;

class pcie_tlp_rc_cfg_converter extends uvm_object;
    `uvm_object_utils(pcie_tlp_rc_cfg_converter)

    function new(string name = "pcie_tlp_rc_cfg_converter");
        super.new(name);
    endfunction

    static function void from_class(input pcie_tlp_rc_agent_config cfg_in,
                                    output pcie_tlp_rc_cfg_s cfg_out);
        cfg_out.num_transactions  = cfg_in.num_transactions;
        cfg_out.start_address     = cfg_in.address_range_min[0];
        cfg_out.end_address       = cfg_in.address_range_max[0];
        cfg_out.is_active         = (cfg_in.is_active == UVM_ACTIVE);
        cfg_out.max_payload_size  = PCIE_TLP_MAX_PAYLOAD;
        cfg_out.wait_states       = cfg_in.wait_states;
        cfg_out.flow_control_enabled = cfg_in.flow_control_enabled;
        cfg_out.outstanding_limit = cfg_in.outstanding_write_tx;
    endfunction

    static function void to_class(input pcie_tlp_rc_cfg_s cfg_in,
                                  output pcie_tlp_rc_agent_config cfg_out);
        cfg_out.num_transactions = cfg_in.num_transactions;
        cfg_out.wait_states      = cfg_in.wait_states;
        cfg_out.flow_control_enabled = cfg_in.flow_control_enabled;
    endfunction

    function void do_print(uvm_printer printer);
        pcie_tlp_rc_cfg_s cfg;
        printer.print_field("num_transactions", cfg.num_transactions, $bits(cfg.num_transactions), UVM_DEC);
        printer.print_field("start_address", cfg.start_address, $bits(cfg.start_address), UVM_HEX);
        printer.print_field("end_address", cfg.end_address, $bits(cfg.end_address), UVM_HEX);
        printer.print_field("is_active", cfg.is_active, $bits(cfg.is_active), UVM_BIN);
        printer.print_field("max_payload_size", cfg.max_payload_size, $bits(cfg.max_payload_size), UVM_DEC);
        printer.print_field("wait_states", cfg.wait_states, $bits(cfg.wait_states), UVM_DEC);
        printer.print_field("flow_control_enabled", cfg.flow_control_enabled, $bits(cfg.flow_control_enabled), UVM_BIN);
        printer.print_field("outstanding_limit", cfg.outstanding_limit, $bits(cfg.outstanding_limit), UVM_DEC);
    endfunction

endclass

`endif
'''

PCIE_TLP_RC_WRITE_SEQUENCER_SV = r'''// RC Write Sequencer
`ifndef PCIE_TLP_RC_WRITE_SEQUENCER_SVH
`define PCIE_TLP_RC_WRITE_SEQUENCER_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*; import pcie_tlp_rc_pkg::*;

class pcie_tlp_rc_write_sequencer extends uvm_sequencer #(pcie_tlp_rc_tx);
    `uvm_component_utils(pcie_tlp_rc_write_sequencer)
    pcie_tlp_rc_agent_config cfg;

    function new(string name = "pcie_tlp_rc_write_sequencer", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        `uvm_info(get_type_name(), "build_phase started", UVM_HIGH)
        if (!uvm_config_db#(pcie_tlp_rc_agent_config)::get(this, "", "cfg", cfg)) begin
            `uvm_info(get_type_name(), "No configuration set, using defaults", UVM_LOW)
        end
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        `uvm_info(get_type_name(), "connect_phase started", UVM_HIGH)
    endfunction

    function void end_of_elaboration_phase(uvm_phase phase);
        super.end_of_elaboration_phase(phase);
        `uvm_info(get_type_name(), "end_of_elaboration_phase - Write Sequencer ready", UVM_HIGH)
    endfunction

    function void start_of_simulation_phase(uvm_phase phase);
        super.start_of_simulation_phase(phase);
        `uvm_info(get_type_name(), "start_of_simulation_phase started", UVM_HIGH)
    endfunction

    task run_phase(uvm_phase phase);
        super.run_phase(phase);
        `uvm_info(get_type_name(), "run_phase started", UVM_HIGH)
    endtask

endclass

`endif
'''

PCIE_TLP_RC_READ_SEQUENCER_SV = r'''// RC Read Sequencer
`ifndef PCIE_TLP_RC_READ_SEQUENCER_SVH
`define PCIE_TLP_RC_READ_SEQUENCER_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*; import pcie_tlp_rc_pkg::*;

class pcie_tlp_rc_read_sequencer extends uvm_sequencer #(pcie_tlp_rc_tx);
    `uvm_component_utils(pcie_tlp_rc_read_sequencer)
    pcie_tlp_rc_agent_config cfg;

    function new(string name = "pcie_tlp_rc_read_sequencer", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        `uvm_info(get_type_name(), "build_phase started", UVM_HIGH)
        if (!uvm_config_db#(pcie_tlp_rc_agent_config)::get(this, "", "cfg", cfg)) begin
            `uvm_info(get_type_name(), "No configuration set, using defaults", UVM_LOW)
        end
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        `uvm_info(get_type_name(), "connect_phase started", UVM_HIGH)
    endfunction

    function void end_of_elaboration_phase(uvm_phase phase);
        super.end_of_elaboration_phase(phase);
        `uvm_info(get_type_name(), "end_of_elaboration_phase - Read Sequencer ready", UVM_HIGH)
    endfunction

    function void start_of_simulation_phase(uvm_phase phase);
        super.start_of_simulation_phase(phase);
        `uvm_info(get_type_name(), "start_of_simulation_phase started", UVM_HIGH)
    endfunction

    task run_phase(uvm_phase phase);
        super.run_phase(phase);
        `uvm_info(get_type_name(), "run_phase started", UVM_HIGH)
    endtask

endclass

`endif
'''

PCIE_TLP_RC_DRIVER_PROXY_SV = r'''// RC Driver Proxy
`ifndef PCIE_TLP_RC_DRIVER_PROXY_SVH
`define PCIE_TLP_RC_DRIVER_PROXY_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*; import pcie_tlp_rc_pkg::*;

class pcie_tlp_rc_driver_proxy extends uvm_driver #(pcie_tlp_rc_tx);
    `uvm_component_utils(pcie_tlp_rc_driver_proxy)
    virtual pcie_tlp_rc_driver_bfm bfm;
    uvm_analysis_port #(pcie_tlp_rc_tx) resp_port;

    function new(string name = "pcie_tlp_rc_driver_proxy", uvm_component parent = null);
        super.new(name, parent);
        resp_port = new("resp_port", this);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        `uvm_info(get_type_name(), "build_phase started", UVM_HIGH)
        if (!uvm_config_db#(virtual pcie_tlp_rc_driver_bfm)::get(this, "", "pcie_tlp_rc_driver_bfm", bfm)) begin
            `uvm_fatal(get_type_name(), "Failed to get BFM handle")
        end
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        `uvm_info(get_type_name(), "connect_phase started", UVM_HIGH)
    endfunction

    function void end_of_elaboration_phase(uvm_phase phase);
        super.end_of_elaboration_phase(phase);
        `uvm_info(get_type_name(), "end_of_elaboration_phase - Driver proxy ready", UVM_HIGH)
    endfunction

    function void start_of_simulation_phase(uvm_phase phase);
        super.start_of_simulation_phase(phase);
        `uvm_info(get_type_name(), "start_of_simulation_phase started", UVM_HIGH)
        bfm.wait_for_reset();
    endfunction

    task run_phase(uvm_phase phase);
        pcie_tlp_rc_tx req;
        tlp_t tlp;
        super.run_phase(phase);
        `uvm_info(get_type_name(), "run_phase started", UVM_HIGH)
        forever begin
            seq_item_port.get_next_item(req);
            pcie_tlp_rc_seq_item_converter::from_tx_class(req, tlp);
            if (tlp.transaction_id == 0) tlp.transaction_id = $urandom_range(1, 2**31-1);
            tlp.timestamp = $time;
            `uvm_info(get_type_name(), $sformatf("Sending TLP ID %0d", tlp.transaction_id), UVM_MEDIUM)
            bfm.send_tlp(tlp);
            seq_item_port.item_done();
        end
    endtask

endclass

`endif
'''

PCIE_TLP_RC_MONITOR_PROXY_SV = r'''// RC Monitor Proxy
`ifndef PCIE_TLP_RC_MONITOR_PROXY_SVH
`define PCIE_TLP_RC_MONITOR_PROXY_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*; import pcie_tlp_rc_pkg::*;

class pcie_tlp_rc_monitor_proxy extends uvm_monitor;
    `uvm_component_utils(pcie_tlp_rc_monitor_proxy)
    virtual pcie_tlp_rc_monitor_bfm bfm;
    pcie_tlp_rc_agent_config cfg;
    uvm_analysis_port #(pcie_tlp_rc_tx) tx_ap;
    uvm_analysis_port #(pcie_tlp_rc_tx) rx_ap;

    function new(string name = "pcie_tlp_rc_monitor_proxy", uvm_component parent = null);
        super.new(name, parent);
        tx_ap = new("tx_ap", this);
        rx_ap = new("rx_ap", this);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        `uvm_info(get_type_name(), "build_phase started", UVM_HIGH)
        if (!uvm_config_db#(virtual pcie_tlp_rc_monitor_bfm)::get(this, "", "pcie_tlp_rc_monitor_bfm", bfm)) begin
            `uvm_fatal(get_type_name(), "Failed to get BFM handle")
        end
        if (cfg == null) begin
            if (!uvm_config_db#(pcie_tlp_rc_agent_config)::get(this, "", "cfg", cfg)) begin
                `uvm_info(get_type_name(), "No config set, using defaults", UVM_LOW)
            end
        end
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        `uvm_info(get_type_name(), "connect_phase started", UVM_HIGH)
        bfm.rc_mon_proxy_h = this;
    endfunction

    function void end_of_elaboration_phase(uvm_phase phase);
        super.end_of_elaboration_phase(phase);
        `uvm_info(get_type_name(), "end_of_elaboration_phase - Monitor proxy ready", UVM_HIGH)
    endfunction

    function void start_of_simulation_phase(uvm_phase phase);
        super.start_of_simulation_phase(phase);
        `uvm_info(get_type_name(), "start_of_simulation_phase started", UVM_HIGH)
        bfm.wait_for_reset();
    endfunction

    task run_phase(uvm_phase phase);
        super.run_phase(phase);
        `uvm_info(get_type_name(), "run_phase started", UVM_HIGH)
        fork
            sample_tx_tlps();
            sample_rx_tlps();
        join
    endtask

    task sample_tx_tlps();
        tlp_t tlp;
        forever begin
            bfm.sample_tx_tlp(tlp);
            pcie_tlp_rc_tx tx_item = pcie_tlp_rc_tx::type_id::create("tx_item");
            pcie_tlp_rc_seq_item_converter::to_tx_class(tlp, tx_item);
            tx_ap.write(tx_item);
        end
    endtask

    task sample_rx_tlps();
        tlp_t tlp;
        forever begin
            bfm.sample_rx_tlp(tlp);
            pcie_tlp_rc_tx rx_item = pcie_tlp_rc_tx::type_id::create("rx_item");
            pcie_tlp_rc_seq_item_converter::to_tx_class(tlp, rx_item);
            rx_ap.write(rx_item);
        end
    endtask

endclass

`endif
'''

PCIE_TLP_RC_AGENT_SV = r'''// RC Agent
`ifndef PCIE_TLP_RC_AGENT_SVH
`define PCIE_TLP_RC_AGENT_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*; import pcie_tlp_rc_pkg::*;

class pcie_tlp_rc_agent extends uvm_agent;
    `uvm_component_utils(pcie_tlp_rc_agent)

    pcie_tlp_rc_agent_config cfg;
    pcie_tlp_rc_driver_proxy    driver;
    pcie_tlp_rc_monitor_proxy   monitor;
    pcie_tlp_rc_read_sequencer  read_sequencer;
    pcie_tlp_rc_write_sequencer write_sequencer;
    pcie_tlp_rc_coverage        coverage;

    function new(string name = "pcie_tlp_rc_agent", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        `uvm_info(get_type_name(), "build_phase started", UVM_HIGH)
        if (!uvm_config_db#(pcie_tlp_rc_agent_config)::get(this, "", "cfg", cfg)) begin
            `uvm_fatal(get_type_name(), "No configuration object found")
        end
        if (cfg.is_active == UVM_ACTIVE) begin
            driver = pcie_tlp_rc_driver_proxy::type_id::create("driver", this);
            read_sequencer  = pcie_tlp_rc_read_sequencer::type_id::create("read_sequencer", this);
            write_sequencer = pcie_tlp_rc_write_sequencer::type_id::create("write_sequencer", this);
        end
        monitor = pcie_tlp_rc_monitor_proxy::type_id::create("monitor", this);
        if (cfg.has_coverage) begin
            coverage = pcie_tlp_rc_coverage::type_id::create("coverage", this);
        end
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        `uvm_info(get_type_name(), "connect_phase started", UVM_HIGH)
        if (cfg.is_active == UVM_ACTIVE) begin
            driver.cfg = cfg;
            read_sequencer.cfg = cfg;
            write_sequencer.cfg = cfg;
            driver.seq_item_port.connect(read_sequencer.seq_item_export);
        end
        monitor.cfg = cfg;
        if (cfg.has_coverage) begin
            coverage.cfg = cfg;
            monitor.tx_ap.connect(coverage.analysis_imp);
            monitor.rx_ap.connect(coverage.analysis_imp);
        end
    endfunction

    function void end_of_elaboration_phase(uvm_phase phase);
        super.end_of_elaboration_phase(phase);
        `uvm_info(get_type_name(), "end_of_elaboration_phase - RC Agent ready", UVM_HIGH)
    endfunction

    function void start_of_simulation_phase(uvm_phase phase);
        super.start_of_simulation_phase(phase);
        `uvm_info(get_type_name(), "start_of_simulation_phase started", UVM_HIGH)
    endfunction

    task run_phase(uvm_phase phase);
        super.run_phase(phase);
        `uvm_info(get_type_name(), "run_phase started", UVM_HIGH)
    endtask

endclass

`endif
'''

PCIE_TLP_RC_PKG_SV = r'''// RC Agent Package
`ifndef PCIE_TLP_RC_PKG_SVH
`define PCIE_TLP_RC_PKG_SVH

package pcie_tlp_rc_pkg;
    `include "uvm_macros.svh"
    import uvm_pkg::*;
    import pcie_tlp_globals_pkg::*;

    `include "pcie_tlp_rc_agent_config.sv"
    `include "pcie_tlp_rc_tx.sv"
    `include "pcie_tlp_rc_seq_item_converter.sv"
    `include "pcie_tlp_rc_covernter_config.sv"
    `include "pcie_tlp_rc_write_sequencer.sv"
    `include "pcie_tlp_rc_read_sequencer.sv"
    `include "pcie_tlp_rc_driver_proxy.sv"
    `include "pcie_tlp_rc_monitor_proxy.sv"
    `include "pcie_tlp_rc_coverage.sv"
    `include "pcie_tlp_rc_agent.sv"
endpackage

`endif
'''

# ========================= EP HVL FILES =========================
PCIE_TLP_EP_AGENT_CONFIG_SV = r'''// EP Agent Configuration
`ifndef PCIE_TLP_EP_AGENT_CONFIG_SVH
`define PCIE_TLP_EP_AGENT_CONFIG_SVH

import uvm_pkg::*; `include "uvm_macros.svh"
import pcie_tlp_globals_pkg::*;

class pcie_tlp_ep_agent_config extends uvm_object;
    `uvm_object_utils(pcie_tlp_ep_agent_config)
    uvm_active_passive_enum is_active = UVM_ACTIVE;
    bit has_coverage = 1'b0;
    int min_address = 32'h0000_0000;
    int max_address = 32'h0000_0FFF;
    int memory_size = 4096;
    int wait_states = 0;
    int outstanding_limit = 8;
    int response_mode = 0;
    bit flow_control_enabled = 1'b1;
    int default_read_data = 32'hDEAD_BEEF;

    function new(string name = "pcie_tlp_ep_agent_config");
        super.new(name);
    endfunction

    function int get_min_address(); return min_address; endfunction
    function int get_max_address(); return max_address; endfunction
    function int get_memory_size(); return memory_size; endfunction
    function int get_wait_states(); return wait_states; endfunction
    function int get_outstanding_limit(); return outstanding_limit; endfunction
    function bit is_in_order(); return (response_mode == 0); endfunction
    function bit is_out_of_order(); return (response_mode == 1); endfunction

    function void do_print(uvm_printer printer);
        super.do_print(printer);
        printer.print_string("is_active", is_active.name());
        printer.print_field("has_coverage", has_coverage, $bits(has_coverage), UVM_BIN);
        printer.print_field("min_address", min_address, $bits(min_address), UVM_HEX);
        printer.print_field("max_address", max_address, $bits(max_address), UVM_HEX);
        printer.print_field("memory_size", memory_size, $bits(memory_size), UVM_DEC);
        printer.print_field("wait_states", wait_states, $bits(wait_states), UVM_DEC);
        printer.print_field("outstanding_limit", outstanding_limit, $bits(outstanding_limit), UVM_DEC);
        printer.print_field("response_mode", response_mode, $bits(response_mode), UVM_DEC);
        printer.print_field("flow_control_enabled", flow_control_enabled, 1, UVM_BIN);
        printer.print_field("default_read_data", default_read_data, $bits(default_read_data), UVM_HEX);
    endfunction

endclass

`endif
'''

PCIE_TLP_EP_TX_SV = r'''// EP Transaction
`ifndef PCIE_TLP_EP_TX_SVH
`define PCIE_TLP_EP_TX_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*;

class pcie_tlp_ep_tx extends uvm_sequence_item;
    `uvm_object_utils(pcie_tlp_ep_tx)

    rand tlp_fmt_e   req_fmt;
    rand tlp_type_e  req_type;
    rand logic [9:0] req_length;
    rand logic [31:0] req_address;
    rand logic [31:0] req_tag;
    rand logic [2:0]  req_tc;
    rand logic [1:0]  req_vc_id;
    rand logic [3:0]  req_seq_num;
    rand logic [1023:0] req_payload;
    rand int             payload_size;
    rand int             transaction_id;
    rand int             wait_states;
    rand logic [31:0]   comp_data;
    rand logic [2:0]    comp_status;
    rand bit            comp_has_data;
    rand int            address_space;

    tlp_t request_tlp;
    tlp_t completion_tlp;

    constraint payload_size_c {
        payload_size % 4 == 0;
        payload_size / 4 == req_length;
        req_length inside {[0:PCIE_TLP_MAX_PAYLOAD]};
    }

    constraint req_fmt_type_c {
        (req_fmt == TLP_FMT_MEM_READ)  -> req_type inside {TLP_TYPE_MEM_RD};
        (req_fmt == TLP_FMT_MEM_WRITE) -> req_type inside {TLP_TYPE_MEM_WR};
        (req_fmt == TLP_FMT_CFG_READ)  -> req_type inside {TLP_TYPE_CFG_RD};
        (req_fmt == TLP_FMT_CFG_WRITE) -> req_type inside {TLP_TYPE_CFG_WR};
        (req_fmt == TLP_FMT_IO_READ)   -> req_type inside {TLP_TYPE_IO_RD};
        (req_fmt == TLP_FMT_IO_WRITE)  -> req_type inside {TLP_TYPE_IO_WR};
    }

    constraint req_addr_aligned_c {
        (req_fmt inside {TLP_FMT_MEM_READ, TLP_FMT_MEM_WRITE}) -> (req_address[1:0] == 2'b00);
    }

    constraint req_tag_c { req_tag inside {[0:31]}; }
    constraint trans_id_c { transaction_id > 0; }
    constraint wait_states_c { wait_states inside {[0:5]}; }
    constraint comp_data_c {
        (req_type == TLP_TYPE_MEM_RD || req_type == TLP_TYPE_CFG_RD) -> comp_has_data == 1;
        (req_type inside {TLP_TYPE_MEM_WR, TLP_TYPE_CFG_WR}) -> comp_has_data == 0;
    }

    function new(string name = "pcie_tlp_ep_tx");
        super.new(name);
        req_fmt = TLP_FMT_MEM_READ;
        req_type = TLP_TYPE_MEM_RD;
        req_length = 1;
        req_address = 32'h0000_0000;
        req_tag = 0;
        req_tc = 0;
        req_vc_id = 0;
        req_seq_num = 0;
        req_payload = '0;
        payload_size = 4;
        transaction_id = 1;
        wait_states = 0;
        comp_data = 32'hDEAD_BEEF;
        comp_status = 3'b000;
        comp_has_data = 1;
        address_space = 0;
    endfunction

    function void post_randomize();
        request_tlp.header.dw0[30:28] = req_fmt;
        request_tlp.header.dw0[24:19] = req_type;
        request_tlp.header.dw0[9:0]   = req_length;
        request_tlp.header.dw1 = req_address;
        request_tlp.header.dw2 = {req_tc, 5'b0, req_tag[7:0]};
        request_tlp.header.dw3 = {req_vc_id, req_seq_num, 26'b0};
        request_tlp.payload = req_payload;
        request_tlp.payload_size = payload_size;
        request_tlp.transaction_id = transaction_id;
        request_tlp.timestamp = $time;

        completion_tlp = request_tlp;
        completion_tlp.header.dw0[30:28] = TLP_FMT_MEM_READ;
        completion_tlp.header.dw0[24:19] = TLP_TYPE_CMPL;
        completion_tlp.header.dw0[9:0]   = (comp_has_data) ? 1 : 0;
        completion_tlp.payload = {32'h0, comp_data};
        completion_tlp.payload_size = (comp_has_data) ? 4 : 0;
        completion_tlp.transaction_id = transaction_id;
        completion_tlp.timestamp = $time;
    endfunction

    function void do_copy(uvm_object rhs);
        pcie_tlp_ep_tx copy_obj;
        if (!$cast(copy_obj, rhs)) `uvm_fatal("do_copy", "cast failed")
        super.do_copy(rhs);
        req_fmt = copy_obj.req_fmt; req_type = copy_obj.req_type;
        req_length = copy_obj.req_length; req_address = copy_obj.req_address;
        req_tag = copy_obj.req_tag; req_tc = copy_obj.req_tc;
        req_vc_id = copy_obj.req_vc_id; req_seq_num = copy_obj.req_seq_num;
        req_payload = copy_obj.req_payload; payload_size = copy_obj.payload_size;
        transaction_id = copy_obj.transaction_id; wait_states = copy_obj.wait_states;
        comp_data = copy_obj.comp_data; comp_status = copy_obj.comp_status;
        comp_has_data = copy_obj.comp_has_data; address_space = copy_obj.address_space;
        request_tlp = copy_obj.request_tlp; completion_tlp = copy_obj.completion_tlp;
    endfunction

    function bit do_compare(uvm_object rhs, uvm_comparer comparer);
        pcie_tlp_ep_tx cmp_obj;
        if (!$cast(cmp_obj, rhs)) return 0;
        return super.do_compare(rhs, comparer) &&
               (req_fmt == cmp_obj.req_fmt) && (req_type == cmp_obj.req_type) &&
               (req_length == cmp_obj.req_length) && (req_address == cmp_obj.req_address) &&
               (req_tag == cmp_obj.req_tag) && (req_tc == cmp_obj.req_tc) &&
               (req_vc_id == cmp_obj.req_vc_id) && (req_seq_num == cmp_obj.req_seq_num) &&
               (req_payload == cmp_obj.req_payload) && (payload_size == cmp_obj.payload_size) &&
               (transaction_id == cmp_obj.transaction_id) && (wait_states == cmp_obj.wait_states) &&
               (comp_data == cmp_obj.comp_data) && (comp_status == cmp_obj.comp_status) &&
               (comp_has_data == cmp_obj.comp_has_data) && (address_space == cmp_obj.address_space);
    endfunction

    function void do_print(uvm_printer printer);
        super.do_print(printer);
        printer.print_string("req_fmt", req_fmt.name());
        printer.print_string("req_type", req_type.name());
        printer.print_field("req_length", req_length, $bits(req_length), UVM_DEC);
        printer.print_field("req_address", req_address, $bits(req_address), UVM_HEX);
        printer.print_field("req_tag", req_tag, $bits(req_tag), UVM_HEX);
        printer.print_field("req_tc", req_tc, $bits(req_tc), UVM_DEC);
        printer.print_field("req_vc_id", req_vc_id, $bits(req_vc_id), UVM_DEC);
        printer.print_field("req_seq_num", req_seq_num, $bits(req_seq_num), UVM_DEC);
        printer.print_field("comp_data", comp_data, $bits(comp_data), UVM_HEX);
        printer.print_field("comp_status", comp_status, $bits(comp_status), UVM_DEC);
        printer.print_field("comp_has_data", comp_has_data, 1, UVM_BIN);
        printer.print_field("transaction_id", transaction_id, $bits(transaction_id), UVM_DEC);
        printer.print_field("wait_states", wait_states, $bits(wait_states), UVM_DEC);
        printer.print_field("address_space", address_space, $bits(address_space), UVM_DEC);
        printer.print_field("payload_size", payload_size, $bits(payload_size), UVM_DEC);
        if (payload_size > 0) begin
            int words = (payload_size + 3) / 4;
            for (int i = 0; i < words && i < 8; i++) begin
                printer.print_field($sformatf("req_payload[%0d]", i), req_payload[i*32 +: 32], 32, UVM_HEX);
            end
            if (words > 8) printer.print_string("req_payload", "... (more)");
        end
    endfunction

endclass

`endif
'''

PCIE_TLP_EP_SEQ_ITEM_CONVERTER_SV = r'''// EP Sequence Item Converter
`ifndef PCIE_TLP_EP_SEQ_ITEM_CONVERTER_SVH
`define PCIE_TLP_EP_SEQ_ITEM_CONVERTER_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*; import pcie_tlp_ep_pkg::*;

class pcie_tlp_ep_seq_item_converter extends uvm_object;
    `uvm_object_utils(pcie_tlp_ep_seq_item_converter)

    function new(string name = "pcie_tlp_ep_seq_item_converter");
        super.new(name);
    endfunction

    static function void from_tx_to_request(input pcie_tlp_ep_tx tx, output tlp_t tlp);
        tlp.header.dw0[30:28] = tx.req_fmt;
        tlp.header.dw0[24:19] = tx.req_type;
        tlp.header.dw0[9:0]   = tx.req_length;
        tlp.header.dw1        = tx.req_address;
        tlp.header.dw2        = {tx.req_tc, 5'b0, tx.req_tag[7:0]};
        tlp.header.dw3        = {tx.req_vc_id, tx.req_seq_num, 26'b0};
        tlp.payload           = tx.req_payload;
        tlp.payload_size      = tx.payload_size;
        tlp.transaction_id    = tx.transaction_id;
        tlp.timestamp         = $time;
    endfunction

    static function void from_tx_to_completion(input pcie_tlp_ep_tx tx, output tlp_t comp_tlp);
        comp_tlp.header.dw0[30:28] = TLP_FMT_MEM_READ;
        comp_tlp.header.dw0[24:19] = TLP_TYPE_CMPL;
        comp_tlp.header.dw0[9:0]   = (tx.comp_has_data) ? 1 : 0;
        comp_tlp.header.dw1        = tx.req_address;
        comp_tlp.header.dw2        = {tx.req_tc, 5'b0, tx.req_tag[7:0]};
        comp_tlp.header.dw3        = {tx.req_vc_id, tx.req_seq_num, 26'b0};
        comp_tlp.payload           = {32'h0, tx.comp_data};
        comp_tlp.payload_size      = (tx.comp_has_data) ? 4 : 0;
        comp_tlp.transaction_id    = tx.transaction_id;
        comp_tlp.timestamp         = $time;
    endfunction

    static function void to_tx_from_request(input tlp_t tlp, output pcie_tlp_ep_tx tx);
        tx.req_fmt   = tlp_fmt_e'(tlp.header.dw0[30:28]);
        tx.req_type  = tlp_type_e'(tlp.header.dw0[24:19]);
        tx.req_length = tlp.header.dw0[9:0];
        tx.req_address = tlp.header.dw1;
        tx.req_tag   = tlp.header.dw2[7:0];
        tx.req_tc    = tlp.header.dw2[14:12];
        tx.req_vc_id = tlp.header.dw3[27:26];
        tx.req_seq_num = tlp.header.dw3[23:20];
        tx.req_payload = tlp.payload;
        tx.payload_size = tlp.payload_size;
        tx.transaction_id = tlp.transaction_id;
        tx.request_tlp = tlp;
    endfunction

    static function void to_tx_from_completion(input tlp_t tlp, output pcie_tlp_ep_tx tx);
        tx.req_fmt   = tlp_fmt_e'(tlp.header.dw0[30:28]);
        tx.req_type  = tlp_type_e'(tlp.header.dw0[24:19]);
        tx.req_length = tlp.header.dw0[9:0];
        tx.req_address = tlp.header.dw1;
        tx.req_tag   = tlp.header.dw2[7:0];
        tx.req_tc    = tlp.header.dw2[14:12];
        tx.req_vc_id = tlp.header.dw3[27:26];
        tx.req_seq_num = tlp.header.dw3[23:20];
        if (tlp.payload_size >= 4) begin
            tx.comp_data = tlp.payload[31:0];
            tx.comp_has_data = 1;
        end else begin
            tx.comp_data = 32'h0;
            tx.comp_has_data = 0;
        end
        tx.payload_size = tlp.payload_size;
        tx.transaction_id = tlp.transaction_id;
        tx.completion_tlp = tlp;
    endfunction

    static function void combine_request_and_data(input pcie_tlp_ep_tx req, input logic [31:0] read_data, output pcie_tlp_ep_tx combined);
        combined = new();
        combined.req_fmt      = req.req_fmt;
        combined.req_type     = req.req_type;
        combined.req_length   = req.req_length;
        combined.req_address  = req.req_address;
        combined.req_tag      = req.req_tag;
        combined.req_tc       = req.req_tc;
        combined.req_vc_id    = req.req_vc_id;
        combined.req_seq_num  = req.req_seq_num;
        combined.req_payload  = req.req_payload;
        combined.payload_size = req.payload_size;
        combined.transaction_id = req.transaction_id;
        combined.comp_data    = read_data;
        combined.comp_has_data = 1'b1;
        combined.request_tlp = req.request_tlp;
    endfunction

    function void do_print(uvm_printer printer);
        tlp_t tlp;
        printer.print_field("tlp.header.dw0", tlp.header.dw0, $bits(tlp.header.dw0), UVM_HEX);
        printer.print_field("tlp.header.dw1", tlp.header.dw1, $bits(tlp.header.dw1), UVM_HEX);
        printer.print_field("tlp.header.dw2", tlp.header.dw2, $bits(tlp.header.dw2), UVM_HEX);
        printer.print_field("tlp.header.dw3", tlp.header.dw3, $bits(tlp.header.dw3), UVM_HEX);
    endfunction

endclass

`endif
'''

PCIE_TLP_EP_CONVERNTER_CONFIG_SV = r'''// EP Configuration Converter
`ifndef PCIE_TLP_EP_COVERNTER_CONFIG_SVH
`define PCIE_TLP_EP_COVERNTER_CONFIG_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*; import pcie_tlp_ep_pkg::*;

typedef struct {
    int min_address;
    int max_address;
    int memory_size;
    int wait_states;
    int outstanding_limit;
    int response_mode;
    bit flow_control_enabled;
    bit is_active;
} pcie_tlp_ep_cfg_s;

class pcie_tlp_ep_cfg_converter extends uvm_object;
    `uvm_object_utils(pcie_tlp_ep_cfg_converter)

    function new(string name = "pcie_tlp_ep_cfg_converter");
        super.new(name);
    endfunction

    static function void from_class(input pcie_tlp_ep_agent_config cfg_in,
                                    output pcie_tlp_ep_cfg_s cfg_out);
        cfg_out.min_address       = cfg_in.min_address;
        cfg_out.max_address       = cfg_in.max_address;
        cfg_out.memory_size       = cfg_in.memory_size;
        cfg_out.wait_states       = cfg_in.wait_states;
        cfg_out.outstanding_limit = cfg_in.outstanding_limit;
        cfg_out.response_mode     = cfg_in.response_mode;
        cfg_out.flow_control_enabled = cfg_in.flow_control_enabled;
        cfg_out.is_active         = (cfg_in.is_active == UVM_ACTIVE);
    endfunction

    static function void to_class(input pcie_tlp_ep_cfg_s cfg_in,
                                  output pcie_tlp_ep_agent_config cfg_out);
        cfg_out.min_address       = cfg_in.min_address;
        cfg_out.max_address       = cfg_in.max_address;
        cfg_out.memory_size       = cfg_in.memory_size;
        cfg_out.wait_states       = cfg_in.wait_states;
        cfg_out.outstanding_limit = cfg_in.outstanding_limit;
        cfg_out.response_mode     = cfg_in.response_mode;
        cfg_out.flow_control_enabled = cfg_in.flow_control_enabled;
        cfg_out.is_active         = cfg_in.is_active ? UVM_ACTIVE : UVM_PASSIVE;
    endfunction

    function void do_print(uvm_printer printer);
        pcie_tlp_ep_cfg_s cfg;
        printer.print_field("min_address", cfg.min_address, $bits(cfg.min_address), UVM_HEX);
        printer.print_field("max_address", cfg.max_address, $bits(cfg.max_address), UVM_HEX);
        printer.print_field("memory_size", cfg.memory_size, $bits(cfg.memory_size), UVM_DEC);
        printer.print_field("wait_states", cfg.wait_states, $bits(cfg.wait_states), UVM_DEC);
        printer.print_field("outstanding_limit", cfg.outstanding_limit, $bits(cfg.outstanding_limit), UVM_DEC);
        printer.print_field("response_mode", cfg.response_mode, $bits(cfg.response_mode), UVM_DEC);
        printer.print_field("flow_control_enabled", cfg.flow_control_enabled, 1, UVM_BIN);
        printer.print_field("is_active", cfg.is_active, 1, UVM_BIN);
    endfunction

endclass

`endif
'''

PCIE_TLP_EP_WRITE_SEQUENCER_SV = r'''// EP Write Sequencer
`ifndef PCIE_TLP_EP_WRITE_SEQUENCER_SVH
`define PCIE_TLP_EP_WRITE_SEQUENCER_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*; import pcie_tlp_ep_pkg::*;

class pcie_tlp_ep_write_sequencer extends uvm_sequencer #(pcie_tlp_ep_tx);
    `uvm_component_utils(pcie_tlp_ep_write_sequencer)
    pcie_tlp_ep_agent_config cfg;

    function new(string name = "pcie_tlp_ep_write_sequencer", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        `uvm_info(get_type_name(), "build_phase started", UVM_HIGH)
        if (!uvm_config_db#(pcie_tlp_ep_agent_config)::get(this, "", "cfg", cfg)) begin
            `uvm_info(get_type_name(), "No configuration set, using defaults", UVM_LOW)
        end
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        `uvm_info(get_type_name(), "connect_phase started", UVM_HIGH)
    endfunction

    function void end_of_elaboration_phase(uvm_phase phase);
        super.end_of_elaboration_phase(phase);
        `uvm_info(get_type_name(), "end_of_elaboration_phase - Write Sequencer ready", UVM_HIGH)
    endfunction

    function void start_of_simulation_phase(uvm_phase phase);
        super.start_of_simulation_phase(phase);
        `uvm_info(get_type_name(), "start_of_simulation_phase started", UVM_HIGH)
    endfunction

    task run_phase(uvm_phase phase);
        super.run_phase(phase);
        `uvm_info(get_type_name(), "run_phase started", UVM_HIGH)
    endtask

endclass

`endif
'''

PCIE_TLP_EP_READ_SEQUENCER_SV = r'''// EP Read Sequencer
`ifndef PCIE_TLP_EP_READ_SEQUENCER_SVH
`define PCIE_TLP_EP_READ_SEQUENCER_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*; import pcie_tlp_ep_pkg::*;

class pcie_tlp_ep_read_sequencer extends uvm_sequencer #(pcie_tlp_ep_tx);
    `uvm_component_utils(pcie_tlp_ep_read_sequencer)
    pcie_tlp_ep_agent_config cfg;

    function new(string name = "pcie_tlp_ep_read_sequencer", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        `uvm_info(get_type_name(), "build_phase started", UVM_HIGH)
        if (!uvm_config_db#(pcie_tlp_ep_agent_config)::get(this, "", "cfg", cfg)) begin
            `uvm_info(get_type_name(), "No configuration set, using defaults", UVM_LOW)
        end
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        `uvm_info(get_type_name(), "connect_phase started", UVM_HIGH)
    endfunction

    function void end_of_elaboration_phase(uvm_phase phase);
        super.end_of_elaboration_phase(phase);
        `uvm_info(get_type_name(), "end_of_elaboration_phase - Read Sequencer ready", UVM_HIGH)
    endfunction

    function void start_of_simulation_phase(uvm_phase phase);
        super.start_of_simulation_phase(phase);
        `uvm_info(get_type_name(), "start_of_simulation_phase started", UVM_HIGH)
    endfunction

    task run_phase(uvm_phase phase);
        super.run_phase(phase);
        `uvm_info(get_type_name(), "run_phase started", UVM_HIGH)
    endtask

endclass

`endif
'''

PCIE_TLP_EP_DRIVER_PROXY_SV = r'''// EP Driver Proxy
`ifndef PCIE_TLP_EP_DRIVER_PROXY_SVH
`define PCIE_TLP_EP_DRIVER_PROXY_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*; import pcie_tlp_ep_pkg::*;

class pcie_tlp_ep_driver_proxy extends uvm_driver #(pcie_tlp_ep_tx);
    `uvm_component_utils(pcie_tlp_ep_driver_proxy)
    pcie_tlp_ep_agent_config cfg;
    pcie_tlp_ep_memory memory;
    virtual pcie_tlp_ep_driver_bfm bfm;
    uvm_analysis_port #(pcie_tlp_ep_tx) rsp_port;
    semaphore write_sem;
    semaphore read_sem;

    function new(string name = "pcie_tlp_ep_driver_proxy", uvm_component parent = null);
        super.new(name, parent);
        rsp_port = new("rsp_port", this);
        write_sem = new(1);
        read_sem = new(1);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        `uvm_info(get_type_name(), "build_phase started", UVM_HIGH)
        if (!uvm_config_db#(virtual pcie_tlp_ep_driver_bfm)::get(this, "", "pcie_tlp_ep_driver_bfm", bfm)) begin
            `uvm_fatal(get_type_name(), "Failed to get BFM handle")
        end
        if (cfg == null) begin
            if (!uvm_config_db#(pcie_tlp_ep_agent_config)::get(this, "", "cfg", cfg)) begin
                `uvm_error(get_type_name(), "No config set, using defaults")
            end
        end
        if (memory == null) begin
            memory = pcie_tlp_ep_memory::type_id::create("memory", this);
            memory.min_address = cfg.min_address;
            memory.max_address = cfg.max_address;
            memory.memory_size = cfg.memory_size;
        end
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        `uvm_info(get_type_name(), "connect_phase started", UVM_HIGH)
        bfm.ep_drv_proxy_h = this;
    endfunction

    function void end_of_elaboration_phase(uvm_phase phase);
        super.end_of_elaboration_phase(phase);
        `uvm_info(get_type_name(), "end_of_elaboration_phase - EP Driver proxy ready", UVM_HIGH)
    endfunction

    function void start_of_simulation_phase(uvm_phase phase);
        super.start_of_simulation_phase(phase);
        `uvm_info(get_type_name(), "start_of_simulation_phase started", UVM_HIGH)
        bfm.wait_for_reset();
    endfunction

    task run_phase(uvm_phase phase);
        pcie_tlp_ep_tx req;
        super.run_phase(phase);
        `uvm_info(get_type_name(), "run_phase started", UVM_HIGH)
        forever begin
            seq_item_port.get_next_item(req);
            process_request(req);
            seq_item_port.item_done();
        end
    endtask

    task process_request(pcie_tlp_ep_tx req);
        tlp_t tlp;
        tlp.header.dw0[30:28] = req.req_fmt;
        tlp.header.dw0[24:19] = req.req_type;
        tlp.header.dw0[9:0]   = req.req_length;
        tlp.header.dw1        = req.req_address;
        tlp.header.dw2        = {req.req_tc, 5'b0, req.req_tag[7:0]};
        tlp.header.dw3        = {req.req_vc_id, req.req_seq_num, 26'b0};
        tlp.payload           = req.req_payload;
        tlp.payload_size      = req.payload_size;
        tlp.transaction_id    = req.transaction_id;
        tlp.timestamp         = $time;

        `uvm_info(get_type_name(), $sformatf("Processing request TLP ID %0d, fmt=%s, type=%s, addr=0x%08x",
                   tlp.transaction_id, req.req_fmt.name(), req.req_type.name(), req.req_address), UVM_MEDIUM)

        case (req.req_fmt)
            TLP_FMT_MEM_READ:  handle_mem_read(req, tlp);
            TLP_FMT_MEM_WRITE: handle_mem_write(req, tlp);
            TLP_FMT_CFG_READ:  handle_cfg_read(req, tlp);
            TLP_FMT_CFG_WRITE: handle_cfg_write(req, tlp);
            TLP_FMT_IO_READ:   handle_io_read(req, tlp);
            TLP_FMT_IO_WRITE:  handle_io_write(req, tlp);
            default: `uvm_error(get_type_name(), $sformatf("Unsupported TLP format: %s", req.req_fmt.name()))
        endcase
    endtask

    task handle_mem_read(pcie_tlp_ep_tx req, tlp_t tlp);
        logic [31:0] read_data;
        tlp_t comp_tlp;
        int addr = req.req_address;
        read_sem.get(1);
        if (memory.is_addr_valid(addr)) begin
            read_data = memory.mem_read_word(addr);
        end else begin
            read_data = cfg.default_read_data;
            `uvm_warning(get_type_name(), $sformatf("Memory read out of range: 0x%08x", addr))
        end
        comp_tlp = tlp;
        comp_tlp.header.dw0[30:28] = TLP_FMT_MEM_READ;
        comp_tlp.header.dw0[24:19] = TLP_TYPE_CMPL;
        comp_tlp.header.dw0[9:0]   = 1;
        comp_tlp.payload = {32'h0, read_data};
        comp_tlp.payload_size = 4;
        comp_tlp.transaction_id = req.transaction_id;
        comp_tlp.timestamp = $time;
        repeat (req.wait_states) @(bfm.drv_cb);
        bfm.send_completion(comp_tlp);
        read_sem.put(1);
        pcie_tlp_ep_tx rsp_item = pcie_tlp_ep_tx::type_id::create("rsp_item");
        rsp_item.comp_data = read_data;
        rsp_item.transaction_id = req.transaction_id;
        rsp_port.write(rsp_item);
    endtask

    task handle_mem_write(pcie_tlp_ep_tx req, tlp_t tlp);
        tlp_t comp_tlp;
        int addr = req.req_address;
        logic [31:0] write_data = req.req_payload[31:0];
        write_sem.get(1);
        if (memory.is_addr_valid(addr)) begin
            memory.mem_write_word(addr, write_data);
        end else begin
            `uvm_warning(get_type_name(), $sformatf("Memory write out of range: 0x%08x", addr))
        end
        comp_tlp = tlp;
        comp_tlp.header.dw0[30:28] = TLP_FMT_MEM_READ;
        comp_tlp.header.dw0[24:19] = TLP_TYPE_CMPL;
        comp_tlp.header.dw0[9:0]   = 0;
        comp_tlp.payload_size = 0;
        comp_tlp.transaction_id = req.transaction_id;
        comp_tlp.timestamp = $time;
        repeat (req.wait_states) @(bfm.drv_cb);
        bfm.send_completion(comp_tlp);
        write_sem.put(1);
    endtask

    task handle_cfg_read(pcie_tlp_ep_tx req, tlp_t tlp);
        tlp_t comp_tlp;
        logic [31:0] cfg_data;
        int offset = req.req_address & 32'hFF;
        cfg_data = memory.cfg_read(offset);
        comp_tlp = tlp;
        comp_tlp.header.dw0[30:28] = TLP_FMT_CFG_READ;
        comp_tlp.header.dw0[24:19] = TLP_TYPE_CMPL;
        comp_tlp.header.dw0[9:0]   = 1;
        comp_tlp.payload = {32'h0, cfg_data};
        comp_tlp.payload_size = 4;
        comp_tlp.transaction_id = req.transaction_id;
        comp_tlp.timestamp = $time;
        repeat (req.wait_states) @(bfm.drv_cb);
        bfm.send_completion(comp_tlp);
    endtask

    task handle_cfg_write(pcie_tlp_ep_tx req, tlp_t tlp);
        tlp_t comp_tlp;
        int offset = req.req_address & 32'hFF;
        logic [31:0] write_data = req.req_payload[31:0];
        memory.cfg_write(offset, write_data);
        comp_tlp = tlp;
        comp_tlp.header.dw0[30:28] = TLP_FMT_CFG_READ;
        comp_tlp.header.dw0[24:19] = TLP_TYPE_CMPL;
        comp_tlp.header.dw0[9:0]   = 0;
        comp_tlp.payload_size = 0;
        comp_tlp.transaction_id = req.transaction_id;
        comp_tlp.timestamp = $time;
        repeat (req.wait_states) @(bfm.drv_cb);
        bfm.send_completion(comp_tlp);
    endtask

    task handle_io_read(pcie_tlp_ep_tx req, tlp_t tlp);
        tlp_t comp_tlp;
        logic [31:0] io_data = 32'hFFFFFFFF;
        comp_tlp = tlp;
        comp_tlp.header.dw0[30:28] = TLP_FMT_IO_READ;
        comp_tlp.header.dw0[24:19] = TLP_TYPE_CMPL;
        comp_tlp.header.dw0[9:0]   = 1;
        comp_tlp.payload = {32'h0, io_data};
        comp_tlp.payload_size = 4;
        comp_tlp.transaction_id = req.transaction_id;
        comp_tlp.timestamp = $time;
        repeat (req.wait_states) @(bfm.drv_cb);
        bfm.send_completion(comp_tlp);
    endtask

    task handle_io_write(pcie_tlp_ep_tx req, tlp_t tlp);
        `uvm_info(get_type_name(), $sformatf("IO write addr=0x%08x data=0x%08x", req.req_address, req.req_payload[31:0]), UVM_MEDIUM)
    endtask

endclass

`endif
'''

PCIE_TLP_EP_MONITOR_PROXY_SV = r'''// EP Monitor Proxy
`ifndef PCIE_TLP_EP_MONITOR_PROXY_SVH
`define PCIE_TLP_EP_MONITOR_PROXY_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*; import pcie_tlp_ep_pkg::*;

class pcie_tlp_ep_monitor_proxy extends uvm_monitor;
    `uvm_component_utils(pcie_tlp_ep_monitor_proxy)
    virtual pcie_tlp_ep_monitor_bfm bfm;
    pcie_tlp_ep_agent_config cfg;
    uvm_analysis_port #(pcie_tlp_ep_tx) req_ap;
    uvm_analysis_port #(pcie_tlp_ep_tx) comp_ap;

    function new(string name = "pcie_tlp_ep_monitor_proxy", uvm_component parent = null);
        super.new(name, parent);
        req_ap = new("req_ap", this);
        comp_ap = new("comp_ap", this);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        `uvm_info(get_type_name(), "build_phase started", UVM_HIGH)
        if (!uvm_config_db#(virtual pcie_tlp_ep_monitor_bfm)::get(this, "", "pcie_tlp_ep_monitor_bfm", bfm)) begin
            `uvm_fatal(get_type_name(), "Failed to get BFM handle")
        end
        if (cfg == null) begin
            if (!uvm_config_db#(pcie_tlp_ep_agent_config)::get(this, "", "cfg", cfg)) begin
                `uvm_info(get_type_name(), "No config set, using defaults", UVM_LOW)
            end
        end
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        `uvm_info(get_type_name(), "connect_phase started", UVM_HIGH)
        bfm.ep_mon_proxy_h = this;
    endfunction

    function void end_of_elaboration_phase(uvm_phase phase);
        super.end_of_elaboration_phase(phase);
        `uvm_info(get_type_name(), "end_of_elaboration_phase - EP Monitor proxy ready", UVM_HIGH)
    endfunction

    function void start_of_simulation_phase(uvm_phase phase);
        super.start_of_simulation_phase(phase);
        `uvm_info(get_type_name(), "start_of_simulation_phase started", UVM_HIGH)
        bfm.wait_for_reset();
    endfunction

    task run_phase(uvm_phase phase);
        super.run_phase(phase);
        `uvm_info(get_type_name(), "run_phase started", UVM_HIGH)
        fork
            sample_requests();
            sample_completions();
        join
    endtask

    task sample_requests();
        tlp_t tlp;
        forever begin
            bfm.sample_request(tlp);
            pcie_tlp_ep_tx tx = pcie_tlp_ep_tx::type_id::create("req_tx");
            pcie_tlp_ep_seq_item_converter::to_tx_from_request(tlp, tx);
            req_ap.write(tx);
        end
    endtask

    task sample_completions();
        tlp_t tlp;
        forever begin
            bfm.sample_completion(tlp);
            pcie_tlp_ep_tx tx = pcie_tlp_ep_tx::type_id::create("comp_tx");
            pcie_tlp_ep_seq_item_converter::to_tx_from_completion(tlp, tx);
            comp_ap.write(tx);
        end
    endtask

endclass

`endif
'''

PCIE_TLP_EP_MEMORY_SV = r'''// EP Memory Model
`ifndef PCIE_TLP_EP_MEMORY_SVH
`define PCIE_TLP_EP_MEMORY_SVH

import uvm_pkg::*; `include "uvm_macros.svh"
import pcie_tlp_globals_pkg::*;

class pcie_tlp_ep_memory extends uvm_object;
    `uvm_object_utils(pcie_tlp_ep_memory)

    protected bit [7:0] memory [longint];
    protected bit [31:0] config_space [0:63];
    protected bit [7:0] io_space [longint];
    bit [7:0] fifo_memory [$:PCIE_TLP_MAX_PAYLOAD-1];

    int min_address = 32'h0000_0000;
    int max_address = 32'h0000_0FFF;
    int memory_size = 4096;
    bit [31:0] default_read_data = 32'hDEAD_BEEF;

    function new(string name = "pcie_tlp_ep_memory");
        super.new(name);
        init_config_space();
    endfunction

    function void init_config_space();
        config_space[0] = {16'h7011, 16'h10EE};
        config_space[1] = 32'h0000_0007;
        config_space[2] = 32'h06040000;
        config_space[3] = 32'h00000000;
        config_space[4] = 32'h0000_0000;
        config_space[5] = 32'h0000_0000;
    endfunction

    function void mem_write(input int address, input bit [7:0] data);
        if (address inside {[min_address:max_address]}) begin
            memory[address] = data;
        end else begin
            `uvm_warning(get_type_name(), $sformatf("Memory write out of range: 0x%08x", address))
        end
    endfunction

    function bit [7:0] mem_read(input int address);
        if (address inside {[min_address:max_address]}) begin
            if (memory.exists(address)) return memory[address];
            else return default_read_data[7:0];
        end else begin
            `uvm_warning(get_type_name(), $sformatf("Memory read out of range: 0x%08x", address))
            return default_read_data[7:0];
        end
    endfunction

    function void mem_write_word(input int address, input bit [31:0] data);
        for (int i = 0; i < 4; i++) begin
            mem_write(address + i, data[8*i +: 8]);
        end
    endfunction

    function bit [31:0] mem_read_word(input int address);
        bit [31:0] data;
        for (int i = 0; i < 4; i++) begin
            data[8*i +: 8] = mem_read(address + i);
        end
        return data;
    endfunction

    function void cfg_write(input int offset, input bit [31:0] data);
        if (offset < 64) begin
            config_space[offset] = data;
        end else begin
            `uvm_warning(get_type_name(), $sformatf("Config write out of range: offset 0x%04x", offset))
        end
    endfunction

    function bit [31:0] cfg_read(input int offset);
        if (offset < 64) begin
            return config_space[offset];
        end else begin
            `uvm_warning(get_type_name(), $sformatf("Config read out of range: offset 0x%04x", offset))
            return 32'hFFFFFFFF;
        end
    endfunction

    function void io_write(input int address, input bit [7:0] data);
        io_space[address] = data;
    endfunction

    function bit [7:0] io_read(input int address);
        if (io_space.exists(address)) return io_space[address];
        else return default_read_data[7:0];
    endfunction

    function void fifo_write(input bit [7:0] data);
        if (fifo_memory.size() < PCIE_TLP_MAX_PAYLOAD) begin
            fifo_memory.push_front(data);
        end else begin
            `uvm_error(get_type_name(), "FIFO overflow")
        end
    endfunction

    function bit [7:0] fifo_read();
        bit [7:0] data;
        if (fifo_memory.size() > 0) begin
            data = fifo_memory.pop_back();
            return data;
        end else begin
            `uvm_error(get_type_name(), "FIFO underflow")
            return 8'h00;
        end
    endfunction

    function bit is_addr_valid(input int address);
        return (address inside {[min_address:max_address]});
    endfunction

    function bit is_addr_exists(input int address);
        return memory.exists(address);
    endfunction

    function void clear_memory();
        memory = '{};
        fifo_memory = '{};
    endfunction

    function void do_print(uvm_printer printer);
        super.do_print(printer);
        printer.print_field("min_address", min_address, $bits(min_address), UVM_HEX);
        printer.print_field("max_address", max_address, $bits(max_address), UVM_HEX);
        printer.print_field("memory_size", memory_size, $bits(memory_size), UVM_DEC);
        printer.print_field("default_read_data", default_read_data, $bits(default_read_data), UVM_HEX);
        printer.print_field("memory_entries", memory.size(), $bits(memory.size()), UVM_DEC);
        printer.print_field("fifo_size", fifo_memory.size(), $bits(fifo_memory.size()), UVM_DEC);
        for (int i = 0; i < 16 && i < 64; i++) begin
            printer.print_field($sformatf("config[%0d]", i), config_space[i], 32, UVM_HEX);
        end
    endfunction

endclass

`endif
'''

PCIE_TLP_EP_AGENT_SV = r'''// EP Agent
`ifndef PCIE_TLP_EP_AGENT_SVH
`define PCIE_TLP_EP_AGENT_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*; import pcie_tlp_ep_pkg::*;

class pcie_tlp_ep_agent extends uvm_agent;
    `uvm_component_utils(pcie_tlp_ep_agent)

    pcie_tlp_ep_agent_config cfg;
    pcie_tlp_ep_driver_proxy    driver;
    pcie_tlp_ep_monitor_proxy   monitor;
    pcie_tlp_ep_read_sequencer  read_sequencer;
    pcie_tlp_ep_write_sequencer write_sequencer;
    pcie_tlp_ep_coverage        coverage;

    function new(string name = "pcie_tlp_ep_agent", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        `uvm_info(get_type_name(), "build_phase started", UVM_HIGH)
        if (!uvm_config_db#(pcie_tlp_ep_agent_config)::get(this, "", "cfg", cfg)) begin
            `uvm_fatal(get_type_name(), "No configuration object found")
        end
        if (cfg.is_active == UVM_ACTIVE) begin
            driver = pcie_tlp_ep_driver_proxy::type_id::create("driver", this);
            read_sequencer  = pcie_tlp_ep_read_sequencer::type_id::create("read_sequencer", this);
            write_sequencer = pcie_tlp_ep_write_sequencer::type_id::create("write_sequencer", this);
        end
        monitor = pcie_tlp_ep_monitor_proxy::type_id::create("monitor", this);
        if (cfg.has_coverage) begin
            coverage = pcie_tlp_ep_coverage::type_id::create("coverage", this);
        end
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        `uvm_info(get_type_name(), "connect_phase started", UVM_HIGH)
        if (cfg.is_active == UVM_ACTIVE) begin
            driver.cfg = cfg;
            read_sequencer.cfg = cfg;
            write_sequencer.cfg = cfg;
            driver.seq_item_port.connect(read_sequencer.seq_item_export);
        end
        monitor.cfg = cfg;
        if (cfg.has_coverage) begin
            coverage.cfg = cfg;
            monitor.req_ap.connect(coverage.analysis_export);
            monitor.comp_ap.connect(coverage.analysis_export);
        end
    endfunction

    function void end_of_elaboration_phase(uvm_phase phase);
        super.end_of_elaboration_phase(phase);
        `uvm_info(get_type_name(), "end_of_elaboration_phase - EP Agent ready", UVM_HIGH)
    endfunction

    function void start_of_simulation_phase(uvm_phase phase);
        super.start_of_simulation_phase(phase);
        `uvm_info(get_type_name(), "start_of_simulation_phase started", UVM_HIGH)
    endfunction

    task run_phase(uvm_phase phase);
        super.run_phase(phase);
        `uvm_info(get_type_name(), "run_phase started", UVM_HIGH)
    endtask

endclass

`endif
'''

PCIE_TLP_EP_PKG_SV = r'''// EP Agent Package
`ifndef PCIE_TLP_EP_PKG_SVH
`define PCIE_TLP_EP_PKG_SVH

package pcie_tlp_ep_pkg;
    `include "uvm_macros.svh"
    import uvm_pkg::*;
    import pcie_tlp_globals_pkg::*;

    `include "pcie_tlp_ep_memory.sv"
    `include "pcie_tlp_ep_tx.sv"
    `include "pcie_tlp_ep_agent_config.sv"
    `include "pcie_tlp_ep_seq_item_converter.sv"
    `include "pcie_tlp_ep_convernter_config.sv"
    `include "pcie_tlp_ep_coverage.sv"
    `include "pcie_tlp_ep_write_sequencer.sv"
    `include "pcie_tlp_ep_read_sequencer.sv"
    `include "pcie_tlp_ep_driver_proxy.sv"
    `include "pcie_tlp_ep_monitor_proxy.sv"
    `include "pcie_tlp_ep_agent.sv"
endpackage

`endif
'''

# ========================= ENVIRONMENT & TESTS =========================
PCIE_TLP_ENV_CONFIG_SV = r'''// PCIe Environment Configuration
`ifndef PCIE_TLP_ENV_CONFIG_SVH
`define PCIE_TLP_ENV_CONFIG_SVH

import uvm_pkg::*; `include "uvm_macros.svh"
import pcie_tlp_globals_pkg::*;
import pcie_tlp_rc_pkg::*;
import pcie_tlp_ep_pkg::*;

class pcie_tlp_env_config extends uvm_object;
    `uvm_object_utils(pcie_tlp_env_config)

    bit has_scoreboard = 1'b1;
    bit has_virtual_seqr = 1'b1;
    bit rc_agent_enabled = 1'b1;
    bit ep_agent_enabled = 1'b1;
    int num_transactions = 10;
    int start_address = 32'h0000_0000;
    int end_address   = 32'h0000_0FFF;
    write_read_data_mode_e write_read_mode_h = WRITE_READ_DATA;
    pcie_tlp_rc_agent_config rc_cfg;
    pcie_tlp_ep_agent_config ep_cfg;

    function new(string name = "pcie_tlp_env_config");
        super.new(name);
    endfunction

    function void do_print(uvm_printer printer);
        super.do_print(printer);
        printer.print_field("has_scoreboard", has_scoreboard, 1, UVM_BIN);
        printer.print_field("has_virtual_seqr", has_virtual_seqr, 1, UVM_BIN);
        printer.print_field("rc_agent_enabled", rc_agent_enabled, 1, UVM_BIN);
        printer.print_field("ep_agent_enabled", ep_agent_enabled, 1, UVM_BIN);
        printer.print_field("num_transactions", num_transactions, $bits(num_transactions), UVM_DEC);
        printer.print_field("start_address", start_address, $bits(start_address), UVM_HEX);
        printer.print_field("end_address", end_address, $bits(end_address), UVM_HEX);
        printer.print_string("write_read_mode_h", write_read_mode_h.name());
        if (rc_cfg != null) printer.print_object("rc_cfg", rc_cfg);
        if (ep_cfg != null) printer.print_object("ep_cfg", ep_cfg);
    endfunction

endclass

`endif
'''

PCIE_TLP_SCOREBOARD_SV = r'''// PCIe Scoreboard
`ifndef PCIE_TLP_SCOREBOARD_SVH
`define PCIE_TLP_SCOREBOARD_SVH

import uvm_pkg::*; `include "uvm_macros.svh"
import pcie_tlp_globals_pkg::*;

class pcie_tlp_scoreboard extends uvm_scoreboard;
    `uvm_component_utils(pcie_tlp_scoreboard)

    uvm_analysis_imp #(tlp_t, pcie_tlp_scoreboard) exp_imp;
    uvm_analysis_imp #(tlp_t, pcie_tlp_scoreboard) act_imp;
    uvm_tlm_analysis_fifo #(tlp_t) exp_fifo;
    uvm_tlm_analysis_fifo #(tlp_t) act_fifo;

    int total_compare;
    int pass_count;
    int fail_count;

    function new(string name = "pcie_tlp_scoreboard", uvm_component parent = null);
        super.new(name, parent);
        exp_imp = new("exp_imp", this);
        act_imp = new("act_imp", this);
        exp_fifo = new("exp_fifo", this);
        act_fifo = new("act_fifo", this);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        exp_fifo.set_size(1024);
        act_fifo.set_size(1024);
    endfunction

    function void write_exp(tlp_t t);
        exp_fifo.put(t);
    endfunction

    function void write_act(tlp_t t);
        act_fifo.put(t);
    endfunction

    task run_phase(uvm_phase phase);
        super.run_phase(phase);
        forever begin
            tlp_t exp_t, act_t;
            exp_fifo.get(exp_t);
            act_fifo.get(act_t);
            total_compare++;
            if (compare_tlp(exp_t, act_t)) begin
                pass_count++;
                `uvm_info(get_type_name(), $sformatf("Comparison PASSED for TLP ID %0d", exp_t.transaction_id), UVM_HIGH)
            end else begin
                fail_count++;
                `uvm_error(get_type_name(), $sformatf("Comparison FAILED for TLP ID %0d", exp_t.transaction_id))
                print_mismatch(exp_t, act_t);
            end
        end
    endtask

    function bit compare_tlp(tlp_t a, tlp_t b);
        if (a.header.dw0 !== b.header.dw0) return 0;
        if (a.header.dw1 !== b.header.dw1) return 0;
        if (a.header.dw2 !== b.header.dw2) return 0;
        if (a.header.dw3 !== b.header.dw3) return 0;
        if (a.payload_size !== b.payload_size) return 0;
        if (a.payload_size > 0) begin
            for (int i = 0; i < 4 && i < a.payload_size/4; i++) begin
                if (a.payload[i*32 +: 32] !== b.payload[i*32 +: 32]) return 0;
            end
        end
        return 1;
    endfunction

    function void print_mismatch(tlp_t a, tlp_t b);
        `uvm_info(get_type_name(), "Mismatch Details:", UVM_LOW)
        `uvm_info(get_type_name(), $sformatf("  Expected DW0: 0x%08x  Actual DW0: 0x%08x", a.header.dw0, b.header.dw0), UVM_LOW)
        `uvm_info(get_type_name(), $sformatf("  Expected DW1: 0x%08x  Actual DW1: 0x%08x", a.header.dw1, b.header.dw1), UVM_LOW)
        `uvm_info(get_type_name(), $sformatf("  Expected DW2: 0x%08x  Actual DW2: 0x%08x", a.header.dw2, b.header.dw2), UVM_LOW)
        `uvm_info(get_type_name(), $sformatf("  Expected DW3: 0x%08x  Actual DW3: 0x%08x", a.header.dw3, b.header.dw3), UVM_LOW)
        `uvm_info(get_type_name(), $sformatf("  Expected Payload Size: %0d  Actual: %0d", a.payload_size, b.payload_size), UVM_LOW)
    endfunction

    function void check_phase(uvm_phase phase);
        super.check_phase(phase);
        if (fail_count > 0) begin
            `uvm_error(get_type_name(), $sformatf("Scoreboard check: %0d failures detected", fail_count))
        end else if (total_compare == 0) begin
            `uvm_warning(get_type_name(), "No transactions compared")
        end else begin
            `uvm_info(get_type_name(), "Scoreboard check PASSED", UVM_LOW)
        end
    endfunction

    function void report_phase(uvm_phase phase);
        super.report_phase(phase);
        `uvm_info(get_type_name(), "=========================================", UVM_LOW)
        `uvm_info(get_type_name(), "Scoreboard Statistics:", UVM_LOW)
        `uvm_info(get_type_name(), $sformatf("  Total Compared : %0d", total_compare), UVM_LOW)
        `uvm_info(get_type_name(), $sformatf("  Pass Count     : %0d", pass_count), UVM_LOW)
        `uvm_info(get_type_name(), $sformatf("  Fail Count     : %0d", fail_count), UVM_LOW)
        if (total_compare > 0) begin
            real pass_rate = (pass_count * 100.0) / total_compare;
            `uvm_info(get_type_name(), $sformatf("  Pass Rate      : %0.2f %%", pass_rate), UVM_LOW)
        end
        `uvm_info(get_type_name(), "=========================================", UVM_LOW)
    endfunction

endclass

`endif
'''

PCIE_TLP_ENV_SV = r'''// PCIe Environment
`ifndef PCIE_TLP_ENV_SVH
`define PCIE_TLP_ENV_SVH

import uvm_pkg::*; `include "uvm_macros.svh"
import pcie_tlp_globals_pkg::*;
import pcie_tlp_rc_pkg::*;
import pcie_tlp_ep_pkg::*;

class pcie_tlp_env extends uvm_env;
    `uvm_component_utils(pcie_tlp_env)

    pcie_tlp_env_config cfg;
    pcie_tlp_rc_agent rc_agent;
    pcie_tlp_ep_agent ep_agent;
    pcie_tlp_virtual_sequencer vseqr;
    pcie_tlp_scoreboard sb;

    function new(string name = "pcie_tlp_env", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        `uvm_info(get_type_name(), "build_phase started", UVM_HIGH)
        if (!uvm_config_db#(pcie_tlp_env_config)::get(this, "", "cfg", cfg)) begin
            `uvm_fatal(get_type_name(), "Failed to get environment configuration from config DB")
        end
        `uvm_info(get_type_name(), $sformatf("Building environment: RC=%0d, EP=%0d, Scoreboard=%0d",
                   cfg.rc_agent_enabled, cfg.ep_agent_enabled, cfg.has_scoreboard), UVM_LOW)

        if (cfg.rc_agent_enabled) begin
            rc_agent = pcie_tlp_rc_agent::type_id::create("rc_agent", this);
        end
        if (cfg.ep_agent_enabled) begin
            ep_agent = pcie_tlp_ep_agent::type_id::create("ep_agent", this);
        end
        vseqr = pcie_tlp_virtual_sequencer::type_id::create("vseqr", this);
        if (cfg.has_scoreboard) begin
            sb = pcie_tlp_scoreboard::type_id::create("sb", this);
        end
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        `uvm_info(get_type_name(), "connect_phase started", UVM_HIGH)

        if (cfg.rc_agent_enabled && rc_agent != null) begin
            vseqr.rc_read_seqr  = rc_agent.read_sequencer;
            vseqr.rc_write_seqr = rc_agent.write_sequencer;
            `uvm_info(get_type_name(), "Connected RC sequencers to virtual sequencer", UVM_HIGH)
        end
        if (cfg.ep_agent_enabled && ep_agent != null) begin
            vseqr.ep_read_seqr  = ep_agent.read_sequencer;
            vseqr.ep_write_seqr = ep_agent.write_sequencer;
            `uvm_info(get_type_name(), "Connected EP sequencers to virtual sequencer", UVM_HIGH)
        end

        if (cfg.has_scoreboard && sb != null) begin
            if (cfg.rc_agent_enabled && rc_agent != null) begin
                rc_agent.monitor.tx_ap.connect(sb.exp_imp);
                `uvm_info(get_type_name(), "Connected RC monitor tx_ap to scoreboard exp_imp", UVM_HIGH)
            end
            if (cfg.ep_agent_enabled && ep_agent != null) begin
                ep_agent.monitor.req_ap.connect(sb.act_imp);
                `uvm_info(get_type_name(), "Connected EP monitor req_ap to scoreboard act_imp", UVM_HIGH)
            end
        end
    endfunction

    function void end_of_elaboration_phase(uvm_phase phase);
        super.end_of_elaboration_phase(phase);
        `uvm_info(get_type_name(), "end_of_elaboration_phase - Environment ready", UVM_HIGH)
        uvm_top.print_topology();
    endfunction

    function void start_of_simulation_phase(uvm_phase phase);
        super.start_of_simulation_phase(phase);
        `uvm_info(get_type_name(), "start_of_simulation_phase started", UVM_HIGH)
    endfunction

    task run_phase(uvm_phase phase);
        super.run_phase(phase);
        `uvm_info(get_type_name(), "run_phase started", UVM_HIGH)
    endtask

endclass

`endif
'''

PCIE_TLP_VIRTUAL_SEQUENCER_SV = r'''// PCIe Virtual Sequencer
`ifndef PCIE_TLP_VIRTUAL_SEQUENCER_SVH
`define PCIE_TLP_VIRTUAL_SEQUENCER_SVH

import uvm_pkg::*; `include "uvm_macros.svh"
import pcie_tlp_globals_pkg::*;
import pcie_tlp_rc_pkg::*;
import pcie_tlp_ep_pkg::*;

class pcie_tlp_virtual_sequencer extends uvm_sequencer #(uvm_sequence_item);
    `uvm_component_utils(pcie_tlp_virtual_sequencer)

    pcie_tlp_rc_read_sequencer  rc_read_seqr;
    pcie_tlp_rc_write_sequencer rc_write_seqr;
    pcie_tlp_ep_read_sequencer  ep_read_seqr;
    pcie_tlp_ep_write_sequencer ep_write_seqr;

    function new(string name = "pcie_tlp_virtual_sequencer", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        `uvm_info(get_type_name(), "build_phase - Virtual Sequencer", UVM_HIGH)
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        `uvm_info(get_type_name(), "connect_phase - Virtual Sequencer", UVM_HIGH)
    endfunction

    function void end_of_elaboration_phase(uvm_phase phase);
        super.end_of_elaboration_phase(phase);
        `uvm_info(get_type_name(), "end_of_elaboration_phase - Virtual Sequencer ready", UVM_HIGH)
    endfunction

    function void start_of_simulation_phase(uvm_phase phase);
        super.start_of_simulation_phase(phase);
        `uvm_info(get_type_name(), "start_of_simulation_phase - Virtual Sequencer", UVM_HIGH)
    endfunction

    task run_phase(uvm_phase phase);
        super.run_phase(phase);
        `uvm_info(get_type_name(), "run_phase - Virtual Sequencer started", UVM_HIGH)
    endtask

endclass

`endif
'''

PCIE_TLP_ENV_PKG_SV = r'''// PCIe Environment Package
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
'''

PCIE_TLP_HVL_TOP_SV = r'''// HVL Top module
`ifndef PCIE_TLP_HVL_TOP_SVH
`define PCIE_TLP_HVL_TOP_SVH

module pcie_tlp_hvl_top;

    import uvm_pkg::*;
    `include "uvm_macros.svh"
    import pcie_tlp_globals_pkg::*;

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
'''

# ========================= TEST FILES =========================
PCIE_TLP_BASE_TEST_SV = r'''// PCIe Base Test
`ifndef PCIE_TLP_BASE_TEST_SVH
`define PCIE_TLP_BASE_TEST_SVH

import uvm_pkg::*; `include "uvm_macros.svh"
import pcie_tlp_globals_pkg::*;
import pcie_tlp_rc_pkg::*;
import pcie_tlp_ep_pkg::*;
import pcie_tlp_env_pkg::*;

class pcie_tlp_base_test extends uvm_test;
    `uvm_component_utils(pcie_tlp_base_test)

    pcie_tlp_env_config cfg;
    pcie_tlp_env env;

    function new(string name = "pcie_tlp_base_test", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        `uvm_info(get_type_name(), "build_phase started", UVM_LOW)
        setup_env_config();
        env = pcie_tlp_env::type_id::create("env", this);
        set_timeout(100ms);
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        `uvm_info(get_type_name(), "connect_phase started", UVM_LOW)
    endfunction

    function void end_of_elaboration_phase(uvm_phase phase);
        super.end_of_elaboration_phase(phase);
        `uvm_info(get_type_name(), "end_of_elaboration_phase - Test configured", UVM_LOW)
    endfunction

    function void start_of_simulation_phase(uvm_phase phase);
        super.start_of_simulation_phase(phase);
        `uvm_info(get_type_name(), "start_of_simulation_phase started", UVM_LOW)
    endfunction

    task run_phase(uvm_phase phase);
        super.run_phase(phase);
        `uvm_info(get_type_name(), "run_phase started", UVM_LOW)
        phase.raise_objection(this);
        pcie_tlp_virtual_base_seq seq = pcie_tlp_virtual_base_seq::type_id::create("seq");
        seq.start(env.vseqr);
        #(100us);
        phase.drop_objection(this);
        `uvm_info(get_type_name(), "run_phase completed", UVM_LOW)
    endtask

    function void check_phase(uvm_phase phase);
        super.check_phase(phase);
    endfunction

    function void report_phase(uvm_phase phase);
        super.report_phase(phase);
        `uvm_info(get_type_name(), "report_phase - Test completed", UVM_LOW)
        if (env.sb != null) env.sb.report_phase(phase);
    endfunction

    function void final_phase(uvm_phase phase);
        super.final_phase(phase);
        `uvm_info(get_type_name(), "final_phase completed", UVM_LOW)
    endfunction

    function void setup_env_config();
        cfg = pcie_tlp_env_config::type_id::create("cfg");
        cfg.rc_agent_enabled = 1'b1;
        cfg.ep_agent_enabled = 1'b1;
        cfg.has_scoreboard = 1'b1;
        cfg.num_transactions = 10;
        cfg.start_address = 32'h0000_0000;
        cfg.end_address   = 32'h0000_0FFF;
        setup_rc_agent_config();
        setup_ep_agent_config();
        uvm_config_db #(pcie_tlp_env_config)::set(this, "*", "cfg", cfg);
        `uvm_info(get_type_name(), $sformatf("Environment configuration:\n%s", cfg.sprint()), UVM_HIGH)
    endfunction

    function void setup_rc_agent_config();
        pcie_tlp_rc_agent_config rc_cfg;
        rc_cfg = pcie_tlp_rc_agent_config::type_id::create("rc_cfg");
        rc_cfg.is_active = UVM_ACTIVE;
        rc_cfg.has_coverage = 1'b0;
        rc_cfg.num_transactions = cfg.num_transactions;
        rc_cfg.wait_states = 0;
        rc_cfg.outstanding_write_tx = 4;
        rc_cfg.outstanding_read_tx  = 4;
        rc_cfg.set_min_address_range(0, cfg.start_address);
        rc_cfg.set_max_address_range(0, cfg.end_address);
        uvm_config_db #(pcie_tlp_rc_agent_config)::set(this, "*env*", "cfg", rc_cfg);
        `uvm_info(get_type_name(), $sformatf("RC Agent Config:\n%s", rc_cfg.sprint()), UVM_HIGH)
    endfunction

    function void setup_ep_agent_config();
        pcie_tlp_ep_agent_config ep_cfg;
        ep_cfg = pcie_tlp_ep_agent_config::type_id::create("ep_cfg");
        ep_cfg.is_active = UVM_ACTIVE;
        ep_cfg.has_coverage = 1'b0;
        ep_cfg.min_address = cfg.start_address;
        ep_cfg.max_address = cfg.end_address;
        ep_cfg.memory_size = cfg.end_address - cfg.start_address + 1;
        ep_cfg.wait_states = 0;
        ep_cfg.outstanding_limit = 8;
        ep_cfg.response_mode = 0;
        ep_cfg.flow_control_enabled = 1'b1;
        ep_cfg.default_read_data = 32'hDEAD_BEEF;
        uvm_config_db #(pcie_tlp_ep_agent_config)::set(this, "*env*", "cfg", ep_cfg);
        `uvm_info(get_type_name(), $sformatf("EP Agent Config:\n%s", ep_cfg.sprint()), UVM_HIGH)
    endfunction

endclass

`endif
'''

PCIE_TLP_MEM_READ_TEST_SV = r'''// Memory Read Test
`ifndef PCIE_TLP_MEM_READ_TEST_SVH
`define PCIE_TLP_MEM_READ_TEST_SVH
import uvm_pkg::*; `include "uvm_macros.svh"
class pcie_tlp_mem_read_test extends pcie_tlp_base_test;
    `uvm_component_utils(pcie_tlp_mem_read_test)
    function new(string name, uvm_component parent=null); super.new(name, parent); endfunction
    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        cfg.num_transactions = 20;
        cfg.start_address = 32'h0000_0000;
        cfg.end_address   = 32'h0000_0FFF;
        `uvm_info("TEST", "Memory Read Test configured", UVM_LOW)
    endfunction
endclass
`endif
'''

PCIE_TLP_MEM_WRITE_TEST_SV = r'''// Memory Write Test
`ifndef PCIE_TLP_MEM_WRITE_TEST_SVH
`define PCIE_TLP_MEM_WRITE_TEST_SVH
import uvm_pkg::*; `include "uvm_macros.svh"
class pcie_tlp_mem_write_test extends pcie_tlp_base_test;
    `uvm_component_utils(pcie_tlp_mem_write_test)
    function new(string name, uvm_component parent=null); super.new(name, parent); endfunction
    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        cfg.num_transactions = 15;
        cfg.start_address = 32'h1000_0000;
        cfg.end_address   = 32'h1000_0FFF;
        `uvm_info("TEST", "Memory Write Test configured", UVM_LOW)
    endfunction
endclass
`endif
'''

# ========================= SEQUENCE FILES =========================
PCIE_TLP_RC_BASE_SEQ_SV = r'''// RC Base Sequence
`ifndef PCIE_TLP_RC_BASE_SEQ_SVH
`define PCIE_TLP_RC_BASE_SEQ_SVH

import uvm_pkg::*; `include "uvm_macros.svh"
import pcie_tlp_globals_pkg::*;
import pcie_tlp_rc_pkg::*;

class pcie_tlp_rc_base_seq extends uvm_sequence #(pcie_tlp_rc_tx);
    `uvm_object_utils(pcie_tlp_rc_base_seq)

    int num_read_transactions  = 5;
    int num_write_transactions = 5;
    int num_config_transactions = 0;
    int num_io_transactions = 0;
    int address_min = 32'h0000_0000;
    int address_max = 32'h0000_0FFF;
    int max_payload_size = PCIE_TLP_MAX_PAYLOAD;
    int wait_states = 0;
    bit flow_control_enabled = 1;

    static int inflight_base[int];
    static int inflight_span[int];
    static int committed_base[$];
    static int trans_count;
    static int total_count;

    function new(string name = "pcie_tlp_rc_base_seq");
        super.new(name);
    endfunction

    task body();
        super.body();
        total_count = num_read_transactions + num_write_transactions +
                      num_config_transactions + num_io_transactions;
        `uvm_info(get_type_name(), $sformatf("Starting RC sequence: %0d reads, %0d writes, %0d config, %0d IO",
                   num_read_transactions, num_write_transactions,
                   num_config_transactions, num_io_transactions), UVM_LOW)
        fork
            generate_writes();
            generate_reads();
            generate_configs();
            generate_ios();
        join
        wait(trans_count == total_count);
        `uvm_info(get_type_name(), $sformatf("All %0d transactions completed", total_count), UVM_LOW)
    endtask

    task generate_writes();
        repeat (num_write_transactions) begin
            pcie_tlp_rc_tx tx = pcie_tlp_rc_tx::type_id::create("tx");
            start_item(tx);
            if (!tx.randomize() with {
                fmt == TLP_FMT_MEM_WRITE;
                typ == TLP_TYPE_MEM_WR;
                address inside {[address_min:address_max]};
                length inside {[1:max_payload_size]};
                payload_size == length * 4;
                transaction_id >= 1;
                wait_states == local::wait_states;
            }) begin
                `uvm_fatal(get_type_name(), "Randomization failed for write transaction")
            end
            inflight_base[tx.transaction_id] = tx.address;
            inflight_span[tx.transaction_id] = tx.payload_size;
            `uvm_info(get_type_name(), $sformatf("Issued WRITE TLP ID %0d, addr=0x%08x, len=%0d",
                       tx.transaction_id, tx.address, tx.payload_size), UVM_MEDIUM)
            finish_item(tx);
            fork
                begin
                    automatic int id = tx.transaction_id;
                    pcie_tlp_rc_tx rsp;
                    get_response(rsp, id);
                    committed_base.push_back(inflight_base[id]);
                    inflight_base.delete(id);
                    inflight_span.delete(id);
                    trans_count++;
                    `uvm_info(get_type_name(), $sformatf("WRITE completion received, ID %0d", id), UVM_HIGH)
                end
            join_none
        end
    endtask

    task generate_reads();
        repeat (num_read_transactions) begin
            pcie_tlp_rc_tx tx = pcie_tlp_rc_tx::type_id::create("tx");
            start_item(tx);
            tx.avoid_base = {};
            tx.avoid_span = {};
            foreach (inflight_base[id]) begin
                tx.avoid_base.push_back(inflight_base[id]);
                tx.avoid_span.push_back(inflight_span[id] + 16);
            end
            tx.readback_base = committed_base;
            if (!tx.randomize() with {
                fmt == TLP_FMT_MEM_READ;
                typ == TLP_TYPE_MEM_RD;
                address inside {[address_min:address_max]};
                length inside {[1:max_payload_size]};
                payload_size == length * 4;
                transaction_id >= 1;
                wait_states == local::wait_states;
            }) begin
                `uvm_fatal(get_type_name(), "Randomization failed for read transaction")
            end
            `uvm_info(get_type_name(), $sformatf("Issued READ TLP ID %0d, addr=0x%08x, len=%0d",
                       tx.transaction_id, tx.address, tx.payload_size), UVM_MEDIUM)
            finish_item(tx);
            fork
                begin
                    automatic int id = tx.transaction_id;
                    pcie_tlp_rc_tx rsp;
                    get_response(rsp, id);
                    trans_count++;
                    `uvm_info(get_type_name(), $sformatf("READ completion received, ID %0d", id), UVM_HIGH)
                end
            join_none
        end
    endtask

    task generate_configs();
        repeat (num_config_transactions) begin
            pcie_tlp_rc_tx tx = pcie_tlp_rc_tx::type_id::create("tx");
            start_item(tx);
            if (!tx.randomize() with {
                fmt inside {TLP_FMT_CFG_READ, TLP_FMT_CFG_WRITE};
                typ inside {TLP_TYPE_CFG_RD, TLP_TYPE_CFG_WR};
                address[9:0] inside {0, 4, 8, 12, 16, 20, 24, 28};
                length == 1;
                payload_size == 4;
                transaction_id >= 1;
                wait_states == local::wait_states;
            }) begin
                `uvm_fatal(get_type_name(), "Randomization failed for config transaction")
            end
            `uvm_info(get_type_name(), $sformatf("Issued CFG TLP ID %0d, offset=0x%04x",
                       tx.transaction_id, tx.address[9:0]), UVM_MEDIUM)
            finish_item(tx);
            fork
                begin
                    automatic int id = tx.transaction_id;
                    pcie_tlp_rc_tx rsp;
                    get_response(rsp, id);
                    trans_count++;
                end
            join_none
        end
    endtask

    task generate_ios();
        repeat (num_io_transactions) begin
            pcie_tlp_rc_tx tx = pcie_tlp_rc_tx::type_id::create("tx");
            start_item(tx);
            if (!tx.randomize() with {
                fmt inside {TLP_FMT_IO_READ, TLP_FMT_IO_WRITE};
                typ inside {TLP_TYPE_IO_RD, TLP_TYPE_IO_WR};
                address[15:0] inside {[0:255]};
                length == 1;
                payload_size == 4;
                transaction_id >= 1;
                wait_states == local::wait_states;
            }) begin
                `uvm_fatal(get_type_name(), "Randomization failed for IO transaction")
            end
            `uvm_info(get_type_name(), $sformatf("Issued IO TLP ID %0d, addr=0x%04x",
                       tx.transaction_id, tx.address[15:0]), UVM_MEDIUM)
            finish_item(tx);
            fork
                begin
                    automatic int id = tx.transaction_id;
                    pcie_tlp_rc_tx rsp;
                    get_response(rsp, id);
                    trans_count++;
                end
            join_none
        end
    endtask

endclass

`endif
'''

PCIE_TLP_RC_SEQ_PKG_SV = r'''// RC Sequence Package
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
'''

PCIE_TLP_EP_BASE_SEQ_SV = r'''// EP Base Sequence
`ifndef PCIE_TLP_EP_BASE_SEQ_SVH
`define PCIE_TLP_EP_BASE_SEQ_SVH

import uvm_pkg::*; `include "uvm_macros.svh"
import pcie_tlp_globals_pkg::*;
import pcie_tlp_ep_pkg::*;

class pcie_tlp_ep_base_seq extends uvm_sequence #(pcie_tlp_ep_tx);
    `uvm_object_utils(pcie_tlp_ep_base_seq)

    int num_write_completions = 5;
    int num_read_completions  = 5;
    int min_address = 32'h0000_0000;
    int max_address = 32'h0000_0FFF;
    int default_data = 32'hDEAD_BEEF;
    int wait_states = 0;

    static int trans_count;
    static int total_count;

    function new(string name = "pcie_tlp_ep_base_seq");
        super.new(name);
    endfunction

    task body();
        super.body();
        total_count = num_write_completions + num_read_completions;
        `uvm_info(get_type_name(), $sformatf("Starting EP sequence: %0d write completions, %0d read completions",
                   num_write_completions, num_read_completions), UVM_LOW)
        fork
            generate_write_completions();
            generate_read_completions();
        join
        wait(trans_count == total_count);
        `uvm_info(get_type_name(), $sformatf("All %0d completions completed", total_count), UVM_LOW)
    endtask

    task generate_write_completions();
        repeat (num_write_completions) begin
            pcie_tlp_ep_tx tx = pcie_tlp_ep_tx::type_id::create("tx");
            start_item(tx);
            if (!tx.randomize() with {
                req_fmt == TLP_FMT_MEM_WRITE;
                req_type == TLP_TYPE_MEM_WR;
                comp_has_data == 0;
                comp_data == 0;
                transaction_id >= 1;
                wait_states == local::wait_states;
                req_address inside {[local::min_address:local::max_address]};
            }) begin
                `uvm_fatal(get_type_name(), "Randomization failed for write completion")
            end
            `uvm_info(get_type_name(), $sformatf("Sending WRITE completion TLP ID %0d, addr=0x%08x",
                       tx.transaction_id, tx.req_address), UVM_MEDIUM)
            finish_item(tx);
            fork
                begin
                    automatic int id = tx.transaction_id;
                    pcie_tlp_ep_tx rsp;
                    get_response(rsp, id);
                    trans_count++;
                    `uvm_info(get_type_name(), $sformatf("Write completion response received, ID %0d", id), UVM_HIGH)
                end
            join_none
        end
    endtask

    task generate_read_completions();
        repeat (num_read_completions) begin
            pcie_tlp_ep_tx tx = pcie_tlp_ep_tx::type_id::create("tx");
            start_item(tx);
            if (!tx.randomize() with {
                req_fmt == TLP_FMT_MEM_READ;
                req_type == TLP_TYPE_MEM_RD;
                comp_has_data == 1;
                comp_data inside {[0:32'hFFFFFFFF]};
                transaction_id >= 1;
                wait_states == local::wait_states;
                req_address inside {[local::min_address:local::max_address]};
            }) begin
                `uvm_fatal(get_type_name(), "Randomization failed for read completion")
            end
            `uvm_info(get_type_name(), $sformatf("Sending READ completion TLP ID %0d, addr=0x%08x, data=0x%08x",
                       tx.transaction_id, tx.req_address, tx.comp_data), UVM_MEDIUM)
            finish_item(tx);
            fork
                begin
                    automatic int id = tx.transaction_id;
                    pcie_tlp_ep_tx rsp;
                    get_response(rsp, id);
                    trans_count++;
                    `uvm_info(get_type_name(), $sformatf("Read completion response received, ID %0d", id), UVM_HIGH)
                end
            join_none
        end
    endtask

endclass

`endif
'''

PCIE_TLP_EP_SEQ_PKG_SV = r'''// EP Sequence Package
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
'''

PCIE_TLP_VIRTUAL_BASE_SEQ_SV = r'''// PCIe Virtual Base Sequence
`ifndef PCIE_TLP_VIRTUAL_BASE_SEQ_SVH
`define PCIE_TLP_VIRTUAL_BASE_SEQ_SVH

import uvm_pkg::*; `include "uvm_macros.svh"
import pcie_tlp_globals_pkg::*;
import pcie_tlp_env_pkg::*;
import pcie_tlp_rc_seq_pkg::*;
import pcie_tlp_ep_seq_pkg::*;

class pcie_tlp_virtual_base_seq extends uvm_sequence;
    `uvm_object_utils(pcie_tlp_virtual_base_seq)
    `uvm_declare_p_sequencer(pcie_tlp_virtual_sequencer)

    pcie_tlp_env_config cfg;
    pcie_tlp_rc_base_seq rc_seq;
    pcie_tlp_ep_base_seq ep_seq;

    function new(string name = "pcie_tlp_virtual_base_seq");
        super.new(name);
    endfunction

    task body();
        if (!uvm_config_db#(pcie_tlp_env_config)::get(null, get_full_name(), "cfg", cfg)) begin
            `uvm_fatal(get_type_name(), "Failed to get environment configuration from config DB")
        end
        if (!$cast(p_sequencer, m_sequencer)) begin
            `uvm_error(get_type_name(), "Virtual sequencer pointer cast failed")
        end
        `uvm_info(get_type_name(), $sformatf("Starting virtual base sequence with %0d transactions", cfg.num_transactions), UVM_LOW)

        rc_seq = pcie_tlp_rc_base_seq::type_id::create("rc_seq");
        ep_seq = pcie_tlp_ep_base_seq::type_id::create("ep_seq");

        rc_seq.num_read_transactions  = cfg.num_transactions / 2;
        rc_seq.num_write_transactions = cfg.num_transactions / 2;
        rc_seq.address_min = cfg.start_address;
        rc_seq.address_max = cfg.end_address;

        ep_seq.num_write_completions = rc_seq.num_write_transactions;
        ep_seq.num_read_completions  = rc_seq.num_read_transactions;
        ep_seq.min_address = cfg.start_address;
        ep_seq.max_address = cfg.end_address;

        fork
            begin
                `uvm_info(get_type_name(), "Starting RC sequence", UVM_HIGH)
                rc_seq.start(p_sequencer.rc_read_seqr);
            end
            begin
                `uvm_info(get_type_name(), "Starting EP sequence", UVM_HIGH)
                ep_seq.start(p_sequencer.ep_read_seqr);
            end
        join

        `uvm_info(get_type_name(), "Virtual base sequence completed", UVM_LOW)
    endtask

endclass

`endif
'''

PCIE_TLP_VSEQ_BASE_PKG_SV = r'''// Virtual Sequence Base Package
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
'''

# ========================= MAKEFILE FILES =========================
MAKEFILE_TXT = r'''# PCIe TLP VIP Makefile
# QuestaSim/ModelSim

SIM          = vsim
WORK         = work
UVM_VER      = 1.1d
TEST         = pcie_tlp_base_test
COVER_OPT    = +cover +fcover
SIM_OPT      = -sv -uvm$(UVM_VER) $(COVER_OPT)
TOP          = pcie_tlp_hvl_top

all: compile sim

compile:
	vlib $(WORK)
	vlog -work $(WORK) $(SIM_OPT) -f ../pcie_tlp_compile.f

sim:
	vsim -c -do "run -all; exit" -work $(WORK) $(TOP) +UVM_TESTNAME=$(TEST)

gui:
	vsim -do "run -all" -work $(WORK) $(TOP) +UVM_TESTNAME=$(TEST)

clean:
	rm -rf $(WORK) *.log *.wlf *.vcd transcript

.PHONY: all compile sim gui clean
'''

QUESTASIM_MAKEFILE = r'''# -s means silent mode
# The command executed along with the output will be displayed on the terminal
# To get only the ouput use 'silent' mode
#
# make target -s


# -n or --just-print 
# The first test I perform on a new makefile target is to invoke make with the --just-print (-n) option. 
# This causes make to read the makefile and print every command it would normally execute to 
# update the target but without executing them.
#
# make target -n


# When you run make with the -i or --ignore-errors flag, 
# errors are ignored in all recipes of all rules. 
# A rule in the makefile for the special target .IGNORE has the same effect, 
# if there are no prerequisites. This is less flexible but sometimes useful.
# When errors are to be ignored, because of -i flag, make treats an error return just like success,
# except that it prints out a message that tells you the status code the shell exited with, 
# and says that the error has been ignored.
#
# make target -i 

# // TODO(mshariff): 
# Add .git rules to ignore log files, basically the sim folder except makefile and scripts


.IGNORE:
	compile
	simulate

# WE can also use the target where we WANT the silent mode 
.SILENT:
	compile
	simulate
	usage

# First target will be executed incase the user doesn't mention
# the target to execute
# In this case, usage will be executed
# Usage
usage:
	echo "";
	echo "-----------------------------------------------------------------";
	echo "------------------------- Usage ---------------------------------";
	echo "";
	echo "make target <options> <variable>=<value>";
	echo "";
	echo "To compile use:";
	echo "make compile";
	echo "";
	echo "To provide compilation argument:";
	echo "make compile args=+<macro_name>=<macro_value>";
	echo "";
	echo "make compile args=+DATA_WIDTH=64";
	echo "";
	echo "To simulate individual test:"
	echo "make simulate test=<test_name> uvm_verbosity=<VERBOSITY_LEVEL>";
	echo "";
	echo "Example:";
	echo "make simulate test=base_test uvm_verbosity=UVM_HIGH";
	echo "";
	echo "To provide seed number (default is random):"
	echo "make simulate test=<test_name> uvm_verbosity=<VERBOSITY_LEVEL> seed=<value>";
	echo "";
	echo "To run regression:"
	echo "make regression testlist_name=<regression_testlist_name.list>";
	echo "";
	echo "Example:";
	echo "make regression testlist_name=pcie_tlp_transfers_regression.list";
	echo "";
	echo "-----------------------------------------------------------------";
	echo "-----------------------------------------------------------------";
	echo "";

all:
	make clean; make compile; make simulate;

# For Assertions use +acc options
#  +cover=becstf
compile:
	make clean_compile;
	make clean_simulate;
	vlib work; 
	vlog -sv \
	+acc \
	+cover \
	+fcover \
	+define$(args) \
	-l pcie_tlp_compile.log \
	-f ../pcie_tlp_compile.f 

	# -s means silent mode
	#  The command executed along with the output will be displayed on the terminal
	#  To get only the ouput use 'silent' mode
	# make compile_war_err -s
	# or use .SILENT
	make compile_war_err

# Setting a default test as base_test
ifndef test
override test = pcie_tlp_base_test
endif

# Setting the default uvm_verbosity to UVM_MEDIUM
ifndef uvm_verbosity
override uvm_verbosity = UVM_NONE
endif

ifndef args
override args = +DATA_WIDTH=32
endif


## For randomized seed
# TODO(mshariff): 
#Add this line after -sva 
#-sv_seed random 

# Setting the default seed value to random
ifndef seed
override seed = random
endif


# Setting the default test folder to test name 
ifndef test_folder
override test_folder = $(test)
endif

simulate:
	mkdir $(test_folder)

	# Use -novopt for no optimization - Makes the simulation slower
	# vsim -pli finesim.so -coverage top
	vsim -vopt \
	work.hvl_top \
	work.hdl_top \
	-voptargs=+acc=npr \
	-sv_seed $(seed) \
	-assertdebug \
	+UVM_TESTNAME=$(test) \
	+UVM_VERBOSITY=$(uvm_verbosity) \
	-l $(test_folder)/$(test).log \
	-sva \
	-coverage \
	-c -do "log -r /*; add wave -r /*; coverage save -onexit -assert -directive -cvg -codeAll $(test_folder)/$(test)_coverage.ucdb; run -all; exit" \
	-wlf $(test_folder)/waveform.wlf


	# For checking and reporting simulation errors
	make simulate_war_err

	## TODO(mshariff): 
	## # For coverage report in text format 
	## #vcover report -text $(test)/$(test)_cov
	# -c -do "log -r /*; add wave -r /*; coverage save -onexit -assert -directive -cvg -codeAll $(test)/coverage.ucdb; coverage report -file $(teset)/coverage.txt -byfile -detail -noannotate -option -directive -cvg -details -verbose; run -all; exit" \
	# vcover report -file  -byfile -detail -noannotate -option -cvg

	# For coverage report in HTML format 
	vcover report -html $(test_folder)/$(test)_coverage.ucdb -htmldir $(test_folder)/html_cov_report -details

	# To open the html coverage report
	# firefox test_folder/html_cov_report/index.html &

	# To open the waveform use the below command 
	# vsim -view waveform.wlf &
	#
	# To open the wavefrom with saved signals
	# vsim -view waveform.wlf -do pcie_tlp_waves.do &

clean_simulate:
	rm -rf *_test*

clean_compile:
	rm -rf work/ *_compile.log transcript waveform.wlf  vsim_stacktrace.vstf vsim.wlf
	rm -rf merged_coverage.ucdb merged_cov_html_report

clean:
	make clean_compile
	make clean_simulate

##
## For Regression and coverage merge
##
regression:
	# Run compilation
	make clean_simulate
	make compile
	# Run simualtion - regression 
	python regression_handling.py $(testlist_name)
	#	# Get the tests from regression list
	#	grep "_test" ../../src/hvl_top/testlists/pcie_tlp_simple_fd_regression.list | grep -v "\#" > reg_list
	#	make simulate test=value #Get the name from regression list
	#	Merge coverage
	make merge_cov_report
		
# For merge to happen, the coverage names for each test must be different
#
merge_cov_report:
	rm -rf merged_coverage.ucdb merged_cov_html_report
	# Merging all the coverage
	vcover merge merged_coverage.ucdb -64 */*.ucdb  
	#vcover merge mem_cover mem_cov1 mem_cov2 mem_cov3 mem_cov4 mem_cov5 mem_cov6 mem_cov7 mem_cov8
	vcover report -html merged_coverage.ucdb -htmldir ./merged_cov_html_report -details

	echo "";
	echo "-----------------------------------------------------------------";
	echo "Coverage report: firefox merged_cov_html_report/index.html &"
	echo "-----------------------------------------------------------------";
	echo "";

compile_war_err:
	echo "";
	echo "-----------------------------------------------------------------";
	echo "------------------- Compilation Report --------------------------";
	echo "";
	grep "^** " pcie_tlp_compile.log;
	echo "";
	grep "^Error" pcie_tlp_compile.log;
	echo "";
	echo "Log file path: pcie_tlp_compile.log"
	echo "";
	echo "-----------------------------------------------------------------";
	echo "-----------------------------------------------------------------";
	echo "";

simulate_war_err:
	echo "";
	echo "-----------------------------------------------------------------";
	echo "-------------------- Simulation Report --------------------------";
	echo "";
	echo "Simulator Errors";
	grep "Error" $(test_folder)/$(test).log;
	echo "";
	echo "UVM Fatal";
	grep "UVM_FATAL" $(test_folder)/$(test).log;
	echo "";
	echo "UVM Errors";
	grep "UVM_ERROR" $(test_folder)/$(test).log;
	echo "";
	echo "UVM Warnings";
	grep "UVM_WARNING" $(test_folder)/$(test).log;
	echo "";
	echo "Testname: $(test)"
	echo "";
	echo "Log file path: $(test_folder)/$(test).log"
	echo "";
	echo "Waveform: vsim -view $(test_folder)/waveform.wlf &"
	echo "";
	echo "Coverage report: firefox $(test_folder)/html_cov_report/index.html &"
	echo "";
	echo "-----------------------------------------------------------------";
	echo "-----------------------------------------------------------------";
	echo "";
'''

PCIE_TLP_COMPILE_F = r'''# PCIe TLP Compile File
# List all source files for compilation

# Global Package
../../src/globals/pcie_tlp_globals_pkg.sv

# Interface
../../src/hdl_top/pcie_tlp_interface/pcie_tlp_if.sv

# BFMs
../../src/hdl_top/rc_agent_bfm/pcie_tlp_rc_agent_bfm.sv
../../src/hdl_top/rc_agent_bfm/pcie_tlp_rc_driver_bfm.sv
../../src/hdl_top/rc_agent_bfm/pcie_tlp_rc_monitor_bfm.sv
../../src/hdl_top/ep_agent_bfm/pcie_tlp_ep_agent_bfm.sv
../../src/hdl_top/ep_agent_bfm/pcie_tlp_ep_driver_bfm.sv
../../src/hdl_top/ep_agent_bfm/pcie_tlp_ep_monitor_bfm.sv

# Assertions (Disabled)
../../src/hdl_top/pcie_tlp_rc_assertions.sv
../../src/hdl_top/pcie_tlp_ep_assertions.sv
../../src/hdl_top/pcie_tlp_tb_rc_assertions.sv
../../src/hdl_top/pcie_tlp_tb_ep_assertions.sv

# HVL Environment
../../src/hvl_top/rc/pcie_tlp_rc_pkg.sv
../../src/hvl_top/ep/pcie_tlp_ep_pkg.sv
../../src/hvl_top/env/pcie_tlp_env_pkg.sv

# Tests
../../src/hvl_top/test/pcie_tlp_base_test.sv
../../src/hvl_top/test/pcie_tlp_mem_read_test.sv
../../src/hvl_top/test/pcie_tlp_mem_write_test.sv

# Sequences
../../src/hvl_top/test/sequences/rc_sequences/pcie_tlp_rc_seq_pkg.sv
../../src/hvl_top/test/sequences/ep_sequences/pcie_tlp_ep_seq_pkg.sv
../../src/hvl_top/test/virtual_sequences/pcie_tlp_vseq_base_pkg.sv

# Top Modules
../../src/hvl_top/pcie_tlp_hvl_top.sv
../../src/hdl_top/pcie_tlp_hdl_top.sv
'''

PCIE_TLP_REGRESSION_LIST = r'''# PCIe TLP Regression Test List
pcie_tlp_base_test
pcie_tlp_mem_read_test
pcie_tlp_mem_write_test
'''

# ============================================================================
# FILE MAPPINGS
# ============================================================================
FILE_MAPPINGS = {
    # HDL Files
    'src/globals/pcie_tlp_globals_pkg.sv': PCIE_TLP_GLOBALS_PKG_SV,
    'src/hdl_top/pcie_tlp_interface/pcie_tlp_if.sv': PCIE_TLP_IF_SV,
    'src/hdl_top/rc_agent_bfm/pcie_tlp_rc_agent_bfm.sv': PCIE_TLP_RC_AGENT_BFM_SV,
    'src/hdl_top/rc_agent_bfm/pcie_tlp_rc_driver_bfm.sv': PCIE_TLP_RC_DRIVER_BFM_SV,
    'src/hdl_top/rc_agent_bfm/pcie_tlp_rc_monitor_bfm.sv': PCIE_TLP_RC_MONITOR_BFM_SV,
    'src/hdl_top/ep_agent_bfm/pcie_tlp_ep_agent_bfm.sv': PCIE_TLP_EP_AGENT_BFM_SV,
    'src/hdl_top/ep_agent_bfm/pcie_tlp_ep_driver_bfm.sv': PCIE_TLP_EP_DRIVER_BFM_SV,
    'src/hdl_top/ep_agent_bfm/pcie_tlp_ep_monitor_bfm.sv': PCIE_TLP_EP_MONITOR_BFM_SV,
    'src/hdl_top/pcie_tlp_hdl_top.sv': PCIE_TLP_HDL_TOP_SV,
    'src/hdl_top/pcie_tlp_rc_assertions.sv': PCIE_TLP_RC_ASSERTIONS_SV,
    'src/hdl_top/pcie_tlp_ep_assertions.sv': PCIE_TLP_EP_ASSERTIONS_SV,
    'src/hdl_top/pcie_tlp_tb_rc_assertions.sv': PCIE_TLP_TB_RC_ASSERTIONS_SV,
    'src/hdl_top/pcie_tlp_tb_ep_assertions.sv': PCIE_TLP_TB_EP_ASSERTIONS_SV,
    'src/hdl_top/pcie_tlp_rc_coverage.sv': PCIE_TLP_RC_COVERAGE_SV,
    'src/hdl_top/pcie_tlp_ep_coverage.sv': PCIE_TLP_EP_COVERAGE_SV,

    # RC HVL Files
    'src/hvl_top/rc/pcie_tlp_rc_agent_config.sv': PCIE_TLP_RC_AGENT_CONFIG_SV,
    'src/hvl_top/rc/pcie_tlp_rc_tx.sv': PCIE_TLP_RC_TX_SV,
    'src/hvl_top/rc/pcie_tlp_rc_seq_item_converter.sv': PCIE_TLP_RC_SEQ_ITEM_CONVERTER_SV,
    'src/hvl_top/rc/pcie_tlp_rc_covernter_config.sv': PCIE_TLP_RC_COVERNTER_CONFIG_SV,
    'src/hvl_top/rc/pcie_tlp_rc_write_sequencer.sv': PCIE_TLP_RC_WRITE_SEQUENCER_SV,
    'src/hvl_top/rc/pcie_tlp_rc_read_sequencer.sv': PCIE_TLP_RC_READ_SEQUENCER_SV,
    'src/hvl_top/rc/pcie_tlp_rc_driver_proxy.sv': PCIE_TLP_RC_DRIVER_PROXY_SV,
    'src/hvl_top/rc/pcie_tlp_rc_monitor_proxy.sv': PCIE_TLP_RC_MONITOR_PROXY_SV,
    'src/hvl_top/rc/pcie_tlp_rc_agent.sv': PCIE_TLP_RC_AGENT_SV,
    'src/hvl_top/rc/pcie_tlp_rc_pkg.sv': PCIE_TLP_RC_PKG_SV,

    # EP HVL Files
    'src/hvl_top/ep/pcie_tlp_ep_agent_config.sv': PCIE_TLP_EP_AGENT_CONFIG_SV,
    'src/hvl_top/ep/pcie_tlp_ep_tx.sv': PCIE_TLP_EP_TX_SV,
    'src/hvl_top/ep/pcie_tlp_ep_seq_item_converter.sv': PCIE_TLP_EP_SEQ_ITEM_CONVERTER_SV,
    'src/hvl_top/ep/pcie_tlp_ep_convernter_config.sv': PCIE_TLP_EP_CONVERNTER_CONFIG_SV,
    'src/hvl_top/ep/pcie_tlp_ep_write_sequencer.sv': PCIE_TLP_EP_WRITE_SEQUENCER_SV,
    'src/hvl_top/ep/pcie_tlp_ep_read_sequencer.sv': PCIE_TLP_EP_READ_SEQUENCER_SV,
    'src/hvl_top/ep/pcie_tlp_ep_driver_proxy.sv': PCIE_TLP_EP_DRIVER_PROXY_SV,
    'src/hvl_top/ep/pcie_tlp_ep_monitor_proxy.sv': PCIE_TLP_EP_MONITOR_PROXY_SV,
    'src/hvl_top/ep/pcie_tlp_ep_memory.sv': PCIE_TLP_EP_MEMORY_SV,
    'src/hvl_top/ep/pcie_tlp_ep_agent.sv': PCIE_TLP_EP_AGENT_SV,
    'src/hvl_top/ep/pcie_tlp_ep_pkg.sv': PCIE_TLP_EP_PKG_SV,

    # Environment Files
    'src/hvl_top/env/pcie_tlp_env_config.sv': PCIE_TLP_ENV_CONFIG_SV,
    'src/hvl_top/env/pcie_tlp_scoreboard.sv': PCIE_TLP_SCOREBOARD_SV,
    'src/hvl_top/env/pcie_tlp_env.sv': PCIE_TLP_ENV_SV,
    'src/hvl_top/env/virtual_sequencer/pcie_tlp_virtual_sequencer.sv': PCIE_TLP_VIRTUAL_SEQUENCER_SV,
    'src/hvl_top/env/pcie_tlp_env_pkg.sv': PCIE_TLP_ENV_PKG_SV,
    'src/hvl_top/pcie_tlp_hvl_top.sv': PCIE_TLP_HVL_TOP_SV,

    # Test Files
    'src/hvl_top/test/pcie_tlp_base_test.sv': PCIE_TLP_BASE_TEST_SV,
    'src/hvl_top/test/pcie_tlp_mem_read_test.sv': PCIE_TLP_MEM_READ_TEST_SV,
    'src/hvl_top/test/pcie_tlp_mem_write_test.sv': PCIE_TLP_MEM_WRITE_TEST_SV,

    # Sequence Files
    'src/hvl_top/test/sequences/rc_sequences/pcie_tlp_rc_base_seq.sv': PCIE_TLP_RC_BASE_SEQ_SV,
    'src/hvl_top/test/sequences/rc_sequences/pcie_tlp_rc_seq_pkg.sv': PCIE_TLP_RC_SEQ_PKG_SV,
    'src/hvl_top/test/sequences/ep_sequences/pcie_tlp_ep_base_seq.sv': PCIE_TLP_EP_BASE_SEQ_SV,
    'src/hvl_top/test/sequences/ep_sequences/pcie_tlp_ep_seq_pkg.sv': PCIE_TLP_EP_SEQ_PKG_SV,
    'src/hvl_top/test/virtual_sequences/pcie_tlp_virtual_base_seq.sv': PCIE_TLP_VIRTUAL_BASE_SEQ_SV,
    'src/hvl_top/test/virtual_sequences/pcie_tlp_vseq_base_pkg.sv': PCIE_TLP_VSEQ_BASE_PKG_SV,

    # Makefile Files
    'sim/makefile': MAKEFILE_TXT,
    'sim/pcie_tlp_compile.f': PCIE_TLP_COMPILE_F,
    'sim/questasim/makefile': QUESTASIM_MAKEFILE,
    'sim/cadence_sim/makefile': MAKEFILE_TXT,
    'sim/synopsys_sim/makefile': MAKEFILE_TXT,
    'src/hvl_top/testlists/pcie_tlp_regression.list': PCIE_TLP_REGRESSION_LIST,
}

# ============================================================================
# MAIN SCRIPT
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Generate PCIe TLP VIP with full UVM code.')
    parser.add_argument('--root', default='pcie_tlp_vip', help='Root directory name')
    parser.add_argument('--force', action='store_true', help='Overwrite existing files')
    parser.add_argument('--hdl', action='store_true', help='Generate HDL files only')
    parser.add_argument('--hvl', action='store_true', help='Generate HVL files only')
    parser.add_argument('--tests', action='store_true', help='Generate test files only')
    parser.add_argument('--sequences', action='store_true', help='Generate sequence files only')
    parser.add_argument('--makefiles', action='store_true', help='Generate Makefile files only')
    args = parser.parse_args()

    root = args.root
    force = args.force

    # Determine which files to generate
    generate_all = not (args.hdl or args.hvl or args.tests or args.sequences or args.makefiles)

    print("="*70)
    print("PCIe TLP VIP Generator - Full UVM Code")
    print("All files have the 'pcie_tlp_' prefix")
    print("="*70)
    print(f"Root: {root}")
    print(f"Overwrite existing: {force}")
    print("-"*70)

    # Create root directory
    if not os.path.exists(root):
        os.makedirs(root, exist_ok=True)
        print(f"?? Created root directory: {root}")

    # Define file groups for filtering
    hdl_prefixes = ['src/globals/', 'src/hdl_top/']
    hvl_prefixes = ['src/hvl_top/rc/', 'src/hvl_top/ep/', 'src/hvl_top/env/', 'src/hvl_top/']
    test_prefixes = ['src/hvl_top/test/', 'src/hvl_top/testlists/']
    seq_prefixes = ['src/hvl_top/test/sequences/']
    make_prefixes = ['sim/', 'sim/questasim/', 'sim/cadence_sim/', 'sim/synopsys_sim/']

    created = 0
    skipped = 0
    errors = 0

    for rel_path, content in FILE_MAPPINGS.items():
        # Determine if this file should be generated based on filters
        should_generate = generate_all
        if args.hdl and any(rel_path.startswith(p) for p in hdl_prefixes):
            should_generate = True
        if args.hvl and any(rel_path.startswith(p) for p in hvl_prefixes):
            should_generate = True
        if args.tests and any(rel_path.startswith(p) for p in test_prefixes):
            should_generate = True
        if args.sequences and any(rel_path.startswith(p) for p in seq_prefixes):
            should_generate = True
        if args.makefiles and any(rel_path.startswith(p) for p in make_prefixes):
            should_generate = True

        if not should_generate:
            continue

        full_path = os.path.join(root, rel_path)
        dirname = os.path.dirname(full_path)

        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)
            print(f"?? Created directory: {dirname}")

        if os.path.exists(full_path) and not force:
            print(f"??  Skipping existing: {rel_path}")
            skipped += 1
            continue

        try:
            with open(full_path, 'w') as f:
                f.write(content)
            print(f"? Created: {rel_path} ({len(content)} bytes)")
            created += 1
        except Exception as e:
            print(f"? Error writing {rel_path}: {e}")
            errors += 1

    # Create additional documentation files
    doc_files = [
        ('README.md', '# PCIe TLP VIP\n\nComplete UVM-based verification IP for PCIe TLP.\n\n## UVM Phases Implemented\n\nAll components implement the full UVM phase flow:\n\n- **build_phase**: Component creation and configuration\n- **connect_phase**: TLM connections between components\n- **end_of_elaboration_phase**: Post-construction checks\n- **start_of_simulation_phase**: Pre-simulation initialization\n- **run_phase**: Main simulation task\n- **extract_phase**: Data extraction from components\n- **check_phase**: Assertion checking\n- **report_phase**: Final report generation\n- **final_phase**: Cleanup\n\n## Directory Structure\n\n- `src/` - Source files\n  - `globals/` - Global package\n  - `hdl_top/` - HDL top and BFMs\n  - `hvl_top/` - HVL environment\n    - `rc/` - Root Complex agent\n    - `ep/` - Endpoint agent\n    - `env/` - Environment and virtual sequencer\n    - `test/` - Test classes\n    - `test/sequences/` - Sequence classes\n- `sim/` - Simulation scripts and makefiles\n\n## Usage\n\n```bash\ncd sim\nmake compile\nmake sim TEST=pcie_tlp_base_test\n```\n'),
        ('coding_guidelines.md', '# Coding Guidelines\n\n## UVM Coding Standards\n\n1. All classes derived from `uvm_object` or `uvm_component`\n2. Use `uvm_component_utils` and `uvm_object_utils` macros\n3. Implement all UVM phases in every component:\n   - `build_phase`\n   - `connect_phase`\n   - `end_of_elaboration_phase`\n   - `start_of_simulation_phase`\n   - `run_phase`\n   - `extract_phase`\n   - `check_phase`\n   - `report_phase`\n   - `final_phase`\n4. Use `uvm_config_db` for configuration passing\n5. All sequence items extend `uvm_sequence_item`\n6. Use `uvm_analysis_port` for monitor connections\n7. Follow SystemVerilog coding conventions\n'),
        ('contribution_guidelines.md', '# Contribution Guidelines\n\n## How to Contribute\n\n1. Fork the repository\n2. Create a feature branch\n3. Make your changes\n4. Run regression tests\n5. Submit a pull request\n\n## Code Review Process\n\nAll submissions must pass:\n- UVM compliance checks\n- Coverage goals\n- Regression tests\n'),
        ('LICENSE.md', '# License\n\nMIT License\n\nCopyright (c) 2024\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the "Software"), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all\ncopies or substantial portions of the Software.\n'),
        ('pcie_tlp_script', '#!/bin/bash\necho "PCIe TLP VIP Script"\necho "Usage: ./pcie_tlp_script [compile|sim|clean]"\n\ncase $1 in\n  compile)\n    cd sim && make compile\n    ;;\n  sim)\n    cd sim && make sim TEST=$2\n    ;;\n  clean)\n    cd sim && make clean\n    ;;\n  *)\n    echo "Unknown command"\n    ;;\nesac\n'),
    ]

    for filename, doc_content in doc_files:
        full_path = os.path.join(root, filename)
        if os.path.exists(full_path) and not force:
            print(f"??  Skipping existing: {filename}")
            skipped += 1
            continue
        try:
            with open(full_path, 'w') as f:
                f.write(doc_content)
            print(f"? Created: {filename} ({len(doc_content)} bytes)")
            created += 1
        except Exception as e:
            print(f"? Error writing {filename}: {e}")
            errors += 1

    print("-"*70)
    print(f"SUMMARY: Created {created} files, skipped {skipped}, errors {errors}")
    print(f"Location: {os.path.abspath(root)}")
    print("="*70)

    if errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
