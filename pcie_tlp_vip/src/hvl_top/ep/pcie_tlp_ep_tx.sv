// EP Transaction
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
