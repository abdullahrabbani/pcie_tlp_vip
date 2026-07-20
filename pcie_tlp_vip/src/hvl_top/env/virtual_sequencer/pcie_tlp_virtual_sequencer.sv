// PCIe Virtual Sequencer
`ifndef PCIE_TLP_VIRTUAL_SEQUENCER_SVH
`define PCIE_TLP_VIRTUAL_SEQUENCER_SVH

import uvm_pkg::*; `include "uvm_macros.svh"
import pcie_tlp_globals_pkg::*;
import pcie_tlp_rc_pkg::*;
import pcie_tlp_ep_pkg::*;

class pcie_tlp_virtual_sequencer extends uvm_sequencer #(uvm_sequence_item);
    `uvm_component_utils(pcie_tlp_virtual_sequencer)

    pcie_tlp_rc_read_sequencer  rc_read_seqr;
    pcie_tlp_rc_write_sequencer rc_write_seqr;
    pcie_tlp_ep_read_sequencer  ep_read_seqr;
    pcie_tlp_ep_write_sequencer ep_write_seqr;

    function new(string name = "pcie_tlp_virtual_sequencer", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        `uvm_info(get_type_name(), "build_phase - Virtual Sequencer", UVM_HIGH)
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        `uvm_info(get_type_name(), "connect_phase - Virtual Sequencer", UVM_HIGH)
    endfunction

    function void end_of_elaboration_phase(uvm_phase phase);
        super.end_of_elaboration_phase(phase);
        `uvm_info(get_type_name(), "end_of_elaboration_phase - Virtual Sequencer ready", UVM_HIGH)
    endfunction

    function void start_of_simulation_phase(uvm_phase phase);
        super.start_of_simulation_phase(phase);
        `uvm_info(get_type_name(), "start_of_simulation_phase - Virtual Sequencer", UVM_HIGH)
    endfunction

    task run_phase(uvm_phase phase);
        super.run_phase(phase);
        `uvm_info(get_type_name(), "run_phase - Virtual Sequencer started", UVM_HIGH)
    endtask

endclass

`endif
