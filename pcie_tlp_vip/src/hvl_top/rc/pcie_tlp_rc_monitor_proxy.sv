// RC Monitor Proxy
`ifndef PCIE_TLP_RC_MONITOR_PROXY_SVH
`define PCIE_TLP_RC_MONITOR_PROXY_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*; import pcie_tlp_rc_pkg::*;

class pcie_tlp_rc_monitor_proxy extends uvm_monitor;
    `uvm_component_utils(pcie_tlp_rc_monitor_proxy)
    virtual pcie_tlp_rc_monitor_bfm bfm;
    pcie_tlp_rc_agent_config cfg;
    uvm_analysis_port #(pcie_tlp_rc_tx) tx_ap;
    uvm_analysis_port #(pcie_tlp_rc_tx) rx_ap;

    function new(string name = "pcie_tlp_rc_monitor_proxy", uvm_component parent = null);
        super.new(name, parent);
        tx_ap = new("tx_ap", this);
        rx_ap = new("rx_ap", this);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        `uvm_info(get_type_name(), "build_phase started", UVM_HIGH)
        if (!uvm_config_db#(virtual pcie_tlp_rc_monitor_bfm)::get(this, "", "pcie_tlp_rc_monitor_bfm", bfm)) begin
            `uvm_fatal(get_type_name(), "Failed to get BFM handle")
        end
        if (cfg == null) begin
            if (!uvm_config_db#(pcie_tlp_rc_agent_config)::get(this, "", "cfg", cfg)) begin
                `uvm_info(get_type_name(), "No config set, using defaults", UVM_LOW)
            end
        end
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        `uvm_info(get_type_name(), "connect_phase started", UVM_HIGH)
        bfm.rc_mon_proxy_h = this;
    endfunction

    function void end_of_elaboration_phase(uvm_phase phase);
        super.end_of_elaboration_phase(phase);
        `uvm_info(get_type_name(), "end_of_elaboration_phase - Monitor proxy ready", UVM_HIGH)
    endfunction

    function void start_of_simulation_phase(uvm_phase phase);
        super.start_of_simulation_phase(phase);
        `uvm_info(get_type_name(), "start_of_simulation_phase started", UVM_HIGH)
        bfm.wait_for_reset();
    endfunction

    task run_phase(uvm_phase phase);
        super.run_phase(phase);
        `uvm_info(get_type_name(), "run_phase started", UVM_HIGH)
        fork
            sample_tx_tlps();
            sample_rx_tlps();
        join
    endtask

    task sample_tx_tlps();
        tlp_t tlp;
        pcie_tlp_rc_tx tx_item;
        forever begin
            bfm.sample_tx_tlp(tlp);
            tx_item = pcie_tlp_rc_tx::type_id::create("tx_item");
            pcie_tlp_rc_seq_item_converter::to_tx_class(tlp, tx_item);
            tx_ap.write(tx_item);
        end
    endtask

    task sample_rx_tlps();
        tlp_t tlp;
        pcie_tlp_rc_tx rx_item;
        forever begin
            bfm.sample_rx_tlp(tlp);
            rx_item = pcie_tlp_rc_tx::type_id::create("rx_item");
            pcie_tlp_rc_seq_item_converter::to_tx_class(tlp, rx_item);
            rx_ap.write(rx_item);
        end
    endtask

endclass

`endif
