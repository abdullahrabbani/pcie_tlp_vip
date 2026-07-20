// RC Base Sequence
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
