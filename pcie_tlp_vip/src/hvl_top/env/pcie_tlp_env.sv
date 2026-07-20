// PCIe Environment
`ifndef PCIE_TLP_ENV_SVH
`define PCIE_TLP_ENV_SVH

import uvm_pkg::*; `include "uvm_macros.svh"
import pcie_tlp_globals_pkg::*;
import pcie_tlp_rc_pkg::*;
import pcie_tlp_ep_pkg::*;

class pcie_tlp_env extends uvm_env;
    `uvm_component_utils(pcie_tlp_env)

    pcie_tlp_env_config cfg;
    pcie_tlp_rc_agent rc_agent;
    pcie_tlp_ep_agent ep_agent;
    pcie_tlp_virtual_sequencer vseqr;
    pcie_tlp_scoreboard sb;

    function new(string name = "pcie_tlp_env", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        `uvm_info(get_type_name(), "build_phase started", UVM_HIGH)
        if (!uvm_config_db#(pcie_tlp_env_config)::get(this, "", "cfg", cfg)) begin
            `uvm_fatal(get_type_name(), "Failed to get environment configuration from config DB")
        end
        `uvm_info(get_type_name(), $sformatf("Building environment: RC=%0d, EP=%0d, Scoreboard=%0d",
                   cfg.rc_agent_enabled, cfg.ep_agent_enabled, cfg.has_scoreboard), UVM_LOW)

        if (cfg.rc_agent_enabled) begin
            rc_agent = pcie_tlp_rc_agent::type_id::create("rc_agent", this);
        end
        if (cfg.ep_agent_enabled) begin
            ep_agent = pcie_tlp_ep_agent::type_id::create("ep_agent", this);
        end
        vseqr = pcie_tlp_virtual_sequencer::type_id::create("vseqr", this);
        if (cfg.has_scoreboard) begin
            sb = pcie_tlp_scoreboard::type_id::create("sb", this);
        end
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        `uvm_info(get_type_name(), "connect_phase started", UVM_HIGH)

        if (cfg.rc_agent_enabled && rc_agent != null) begin
            vseqr.rc_read_seqr  = rc_agent.read_sequencer;
            vseqr.rc_write_seqr = rc_agent.write_sequencer;
            `uvm_info(get_type_name(), "Connected RC sequencers to virtual sequencer", UVM_HIGH)
        end
        if (cfg.ep_agent_enabled && ep_agent != null) begin
            vseqr.ep_read_seqr  = ep_agent.read_sequencer;
            vseqr.ep_write_seqr = ep_agent.write_sequencer;
            `uvm_info(get_type_name(), "Connected EP sequencers to virtual sequencer", UVM_HIGH)
        end

        if (cfg.has_scoreboard && sb != null) begin
            if (cfg.rc_agent_enabled && rc_agent != null) begin
                rc_agent.monitor.tx_ap.connect(sb.exp_imp);
                `uvm_info(get_type_name(), "Connected RC monitor tx_ap to scoreboard exp_imp", UVM_HIGH)
            end
            if (cfg.ep_agent_enabled && ep_agent != null) begin
                ep_agent.monitor.req_ap.connect(sb.act_imp);
                `uvm_info(get_type_name(), "Connected EP monitor req_ap to scoreboard act_imp", UVM_HIGH)
            end
        end
    endfunction

    function void end_of_elaboration_phase(uvm_phase phase);
        super.end_of_elaboration_phase(phase);
        `uvm_info(get_type_name(), "end_of_elaboration_phase - Environment ready", UVM_HIGH)
        uvm_top.print_topology();
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
