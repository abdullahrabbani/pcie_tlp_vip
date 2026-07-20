// PCIe TLP Interface
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
