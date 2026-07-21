// PCIe Base Test
`ifndef PCIE_TLP_BASE_TEST_SVH
`define PCIE_TLP_BASE_TEST_SVH

import uvm_pkg::*; `include "uvm_macros.svh"
import pcie_tlp_globals_pkg::*;
import pcie_tlp_rc_pkg::*;
import pcie_tlp_ep_pkg::*;
import pcie_tlp_env_pkg::*;
import pcie_tlp_vseq_base_pkg::*;

class pcie_tlp_base_test extends uvm_test;
    `uvm_component_utils(pcie_tlp_base_test)

    pcie_tlp_env_config cfg;
    pcie_tlp_env env;
    pcie_tlp_virtual_base_seq seq;

    function new(string name = "pcie_tlp_base_test", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        `uvm_info(get_type_name(), "build_phase started", UVM_LOW)
        setup_env_config();
        env = pcie_tlp_env::type_id::create("env", this);
        uvm_top.set_timeout(100ms);
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        `uvm_info(get_type_name(), "connect_phase started", UVM_LOW)
    endfunction

    function void end_of_elaboration_phase(uvm_phase phase);
        super.end_of_elaboration_phase(phase);
        `uvm_info(get_type_name(), "end_of_elaboration_phase - Test configured", UVM_LOW)
    endfunction

    function void start_of_simulation_phase(uvm_phase phase);
        super.start_of_simulation_phase(phase);
        `uvm_info(get_type_name(), "start_of_simulation_phase started", UVM_LOW)
    endfunction

    task run_phase(uvm_phase phase);
        `uvm_info(get_type_name(), "run_phase started", UVM_LOW)
        phase.raise_objection(this);
        super.run_phase(phase);
        seq = pcie_tlp_virtual_base_seq::type_id::create("seq");
        seq.start(env.vseqr);
        #(100us);
        phase.drop_objection(this);
        `uvm_info(get_type_name(), "run_phase completed", UVM_LOW)
    endtask

    function void check_phase(uvm_phase phase);
        super.check_phase(phase);
    endfunction

    function void report_phase(uvm_phase phase);
        super.report_phase(phase);
        `uvm_info(get_type_name(), "report_phase - Test completed", UVM_LOW)
        if (env.sb != null) env.sb.report_phase(phase);
    endfunction

    function void final_phase(uvm_phase phase);
        super.final_phase(phase);
        `uvm_info(get_type_name(), "final_phase completed", UVM_LOW)
    endfunction

    function void setup_env_config();
        cfg = pcie_tlp_env_config::type_id::create("cfg");
        cfg.rc_agent_enabled = 1'b1;
        cfg.ep_agent_enabled = 1'b1;
        cfg.has_scoreboard = 1'b1;
        cfg.num_transactions = 10;
        cfg.start_address = 32'h0000_0000;
        cfg.end_address   = 32'h0000_0FFF;
        setup_rc_agent_config();
        setup_ep_agent_config();
        uvm_config_db #(pcie_tlp_env_config)::set(this, "*", "cfg", cfg);
        `uvm_info(get_type_name(), $sformatf("Environment configuration:\n%s", cfg.sprint()), UVM_HIGH)
    endfunction

    function void setup_rc_agent_config();
        pcie_tlp_rc_agent_config rc_cfg;
        rc_cfg = pcie_tlp_rc_agent_config::type_id::create("rc_cfg");
        rc_cfg.is_active = UVM_ACTIVE;
        rc_cfg.has_coverage = 1'b0;
        rc_cfg.num_transactions = cfg.num_transactions;
        rc_cfg.wait_states = 0;
        rc_cfg.outstanding_write_tx = 4;
        rc_cfg.outstanding_read_tx  = 4;
        rc_cfg.set_min_address_range(0, cfg.start_address);
        rc_cfg.set_max_address_range(0, cfg.end_address);
        uvm_config_db #(pcie_tlp_rc_agent_config)::set(this, "*env*", "cfg", rc_cfg);
        `uvm_info(get_type_name(), $sformatf("RC Agent Config:\n%s", rc_cfg.sprint()), UVM_HIGH)
    endfunction

    function void setup_ep_agent_config();
        pcie_tlp_ep_agent_config ep_cfg;
        ep_cfg = pcie_tlp_ep_agent_config::type_id::create("ep_cfg");
        ep_cfg.is_active = UVM_ACTIVE;
        ep_cfg.has_coverage = 1'b0;
        ep_cfg.min_address = cfg.start_address;
        ep_cfg.max_address = cfg.end_address;
        ep_cfg.memory_size = cfg.end_address - cfg.start_address + 1;
        ep_cfg.wait_states = 0;
        ep_cfg.outstanding_limit = 8;
        ep_cfg.response_mode = 0;
        ep_cfg.flow_control_enabled = 1'b1;
        ep_cfg.default_read_data = 32'hDEAD_BEEF;
        uvm_config_db #(pcie_tlp_ep_agent_config)::set(this, "*env*", "cfg", ep_cfg);
        `uvm_info(get_type_name(), $sformatf("EP Agent Config:\n%s", ep_cfg.sprint()), UVM_HIGH)
    endfunction

endclass

`endif
