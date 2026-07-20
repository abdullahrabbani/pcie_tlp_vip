// EP Assertions (DISABLED)
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
