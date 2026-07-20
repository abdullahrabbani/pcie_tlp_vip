// EP Write Sequencer
`ifndef PCIE_TLP_EP_WRITE_SEQUENCER_SVH
`define PCIE_TLP_EP_WRITE_SEQUENCER_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*; import pcie_tlp_ep_pkg::*;

class pcie_tlp_ep_write_sequencer extends uvm_sequencer #(pcie_tlp_ep_tx);
    `uvm_component_utils(pcie_tlp_ep_write_sequencer)
    pcie_tlp_ep_agent_config cfg;

    function new(string name = "pcie_tlp_ep_write_sequencer", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        `uvm_info(get_type_name(), "build_phase started", UVM_HIGH)
        if (!uvm_config_db#(pcie_tlp_ep_agent_config)::get(this, "", "cfg", cfg)) begin
            `uvm_info(get_type_name(), "No configuration set, using defaults", UVM_LOW)
        end
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        `uvm_info(get_type_name(), "connect_phase started", UVM_HIGH)
    endfunction

    function void end_of_elaboration_phase(uvm_phase phase);
        super.end_of_elaboration_phase(phase);
        `uvm_info(get_type_name(), "end_of_elaboration_phase - Write Sequencer ready", UVM_HIGH)
    endfunction

    function void start_of_simulation_phase(uvm_phase phase);
        super.start_of_simulation_phase(phase);
        `uvm_info(get_type_name(), "start_of_simulation_phase started", UVM_HIGH)
    endfunction

    task run_phase(uvm_phase phase);
        super.run_phase(phase);
        `uvm_info(get_type_name(), "run_phase started", UVM_HIGH)
    endtask

endclass

`endif
