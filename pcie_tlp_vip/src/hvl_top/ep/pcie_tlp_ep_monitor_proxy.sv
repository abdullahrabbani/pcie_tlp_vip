// EP Monitor Proxy
`ifndef PCIE_TLP_EP_MONITOR_PROXY_SVH
`define PCIE_TLP_EP_MONITOR_PROXY_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*; import pcie_tlp_ep_pkg::*;

class pcie_tlp_ep_monitor_proxy extends uvm_monitor;
    `uvm_component_utils(pcie_tlp_ep_monitor_proxy)
    virtual pcie_tlp_ep_monitor_bfm bfm;
    pcie_tlp_ep_agent_config cfg;
    uvm_analysis_port #(pcie_tlp_ep_tx) req_ap;
    uvm_analysis_port #(pcie_tlp_ep_tx) comp_ap;

    function new(string name = "pcie_tlp_ep_monitor_proxy", uvm_component parent = null);
        super.new(name, parent);
        req_ap = new("req_ap", this);
        comp_ap = new("comp_ap", this);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        `uvm_info(get_type_name(), "build_phase started", UVM_HIGH)
        if (!uvm_config_db#(virtual pcie_tlp_ep_monitor_bfm)::get(this, "", "pcie_tlp_ep_monitor_bfm", bfm)) begin
            `uvm_fatal(get_type_name(), "Failed to get BFM handle")
        end
        if (cfg == null) begin
            if (!uvm_config_db#(pcie_tlp_ep_agent_config)::get(this, "", "cfg", cfg)) begin
                `uvm_info(get_type_name(), "No config set, using defaults", UVM_LOW)
            end
        end
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        `uvm_info(get_type_name(), "connect_phase started", UVM_HIGH)
        bfm.ep_mon_proxy_h = this;
    endfunction

    function void end_of_elaboration_phase(uvm_phase phase);
        super.end_of_elaboration_phase(phase);
        `uvm_info(get_type_name(), "end_of_elaboration_phase - EP Monitor proxy ready", UVM_HIGH)
    endfunction

    function void start_of_simulation_phase(uvm_phase phase);
        super.start_of_simulation_phase(phase);
        `uvm_info(get_type_name(), "start_of_simulation_phase started", UVM_HIGH)
    endfunction

    task run_phase(uvm_phase phase);
        super.run_phase(phase);
        `uvm_info(get_type_name(), "run_phase started", UVM_HIGH)
        bfm.wait_for_reset();
        fork
            sample_requests();
            sample_completions();
        join
    endtask

    task sample_requests();
        tlp_t tlp;
        pcie_tlp_ep_tx tx;
        forever begin
            bfm.sample_request(tlp);
            tx = pcie_tlp_ep_tx::type_id::create("req_tx");
            pcie_tlp_ep_seq_item_converter::to_tx_from_request(tlp, tx);
            req_ap.write(tx);
        end
    endtask

    task sample_completions();
        tlp_t tlp;
        pcie_tlp_ep_tx tx;
        forever begin
            bfm.sample_completion(tlp);
            tx = pcie_tlp_ep_tx::type_id::create("comp_tx");
            pcie_tlp_ep_seq_item_converter::to_tx_from_completion(tlp, tx);
            comp_ap.write(tx);
        end
    endtask

endclass

`endif
