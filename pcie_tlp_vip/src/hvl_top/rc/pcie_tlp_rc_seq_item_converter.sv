// RC Sequence Item Converter
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
