// EP Agent
`ifndef PCIE_TLP_EP_AGENT_SVH
`define PCIE_TLP_EP_AGENT_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*; import pcie_tlp_ep_pkg::*;

class pcie_tlp_ep_agent extends uvm_agent;
    `uvm_component_utils(pcie_tlp_ep_agent)

    pcie_tlp_ep_agent_config cfg;
    pcie_tlp_ep_driver_proxy    driver;
    pcie_tlp_ep_monitor_proxy   monitor;
    pcie_tlp_ep_read_sequencer  read_sequencer;
    pcie_tlp_ep_write_sequencer write_sequencer;
    //pcie_tlp_ep_coverage        coverage;

    function new(string name = "pcie_tlp_ep_agent", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        `uvm_info(get_type_name(), "build_phase started", UVM_HIGH)
        if (!uvm_config_db#(pcie_tlp_ep_agent_config)::get(this, "", "cfg", cfg)) begin
            `uvm_fatal(get_type_name(), "No configuration object found")
        end
        if (cfg.is_active == UVM_ACTIVE) begin
            driver = pcie_tlp_ep_driver_proxy::type_id::create("driver", this);
            read_sequencer  = pcie_tlp_ep_read_sequencer::type_id::create("read_sequencer", this);
            write_sequencer = pcie_tlp_ep_write_sequencer::type_id::create("write_sequencer", this);
        end
        monitor = pcie_tlp_ep_monitor_proxy::type_id::create("monitor", this);
        if (cfg.has_coverage) begin
           // coverage = pcie_tlp_ep_coverage::type_id::create("coverage", this);
        end
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        `uvm_info(get_type_name(), "connect_phase started", UVM_HIGH)
        if (cfg.is_active == UVM_ACTIVE) begin
            driver.cfg = cfg;
            read_sequencer.cfg = cfg;
            write_sequencer.cfg = cfg;
            driver.seq_item_port.connect(read_sequencer.seq_item_export);
        end
        monitor.cfg = cfg;
        if (cfg.has_coverage) begin
           // coverage.cfg = cfg;
           // monitor.req_ap.connect(coverage.analysis_export);
           // monitor.comp_ap.connect(coverage.analysis_export);
        end
    endfunction

    function void end_of_elaboration_phase(uvm_phase phase);
        super.end_of_elaboration_phase(phase);
        `uvm_info(get_type_name(), "end_of_elaboration_phase - EP Agent ready", UVM_HIGH)
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
