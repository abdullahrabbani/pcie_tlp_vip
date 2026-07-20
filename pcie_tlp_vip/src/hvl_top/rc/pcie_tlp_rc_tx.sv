// RC Transaction
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
