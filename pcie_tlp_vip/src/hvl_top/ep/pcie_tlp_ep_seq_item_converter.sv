// EP Sequence Item Converter
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
