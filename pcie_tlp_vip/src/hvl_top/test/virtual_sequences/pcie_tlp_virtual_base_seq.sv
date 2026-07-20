// PCIe Virtual Base Sequence
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
