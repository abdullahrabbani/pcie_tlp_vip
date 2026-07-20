// PCIe Scoreboard
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
