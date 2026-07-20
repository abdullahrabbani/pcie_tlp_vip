// EP Base Sequence
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
