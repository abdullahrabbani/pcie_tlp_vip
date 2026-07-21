// RC Driver Proxy
`ifndef PCIE_TLP_RC_DRIVER_PROXY_SVH
`define PCIE_TLP_RC_DRIVER_PROXY_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*; import pcie_tlp_rc_pkg::*;

class pcie_tlp_rc_driver_proxy extends uvm_driver #(pcie_tlp_rc_tx);
    `uvm_component_utils(pcie_tlp_rc_driver_proxy)
    virtual pcie_tlp_rc_driver_bfm bfm;
    pcie_tlp_rc_agent_config cfg;
    uvm_analysis_port #(pcie_tlp_rc_tx) resp_port;

    function new(string name = "pcie_tlp_rc_driver_proxy", uvm_component parent = null);
        super.new(name, parent);
        resp_port = new("resp_port", this);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        `uvm_info(get_type_name(), "build_phase started", UVM_HIGH)
        if (!uvm_config_db#(virtual pcie_tlp_rc_driver_bfm)::get(this, "", "pcie_tlp_rc_driver_bfm", bfm)) begin
            `uvm_fatal(get_type_name(), "Failed to get BFM handle")
        end
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        `uvm_info(get_type_name(), "connect_phase started", UVM_HIGH)
    endfunction

    function void end_of_elaboration_phase(uvm_phase phase);
        super.end_of_elaboration_phase(phase);
        `uvm_info(get_type_name(), "end_of_elaboration_phase - Driver proxy ready", UVM_HIGH)
    endfunction

    function void start_of_simulation_phase(uvm_phase phase);
        super.start_of_simulation_phase(phase);
        `uvm_info(get_type_name(), "start_of_simulation_phase started", UVM_HIGH)
    endfunction

    task run_phase(uvm_phase phase);
        pcie_tlp_rc_tx req;
        tlp_t tlp;
        super.run_phase(phase);
        `uvm_info(get_type_name(), "run_phase started", UVM_HIGH)
        bfm.wait_for_reset();
        forever begin
            seq_item_port.get_next_item(req);
            pcie_tlp_rc_seq_item_converter::from_tx_class(req, tlp);
            if (tlp.transaction_id == 0) tlp.transaction_id = $urandom_range(1, 2**31-1);
            tlp.timestamp = $time;
            `uvm_info(get_type_name(), $sformatf("Sending TLP ID %0d", tlp.transaction_id), UVM_MEDIUM)
            bfm.send_tlp(tlp);
            seq_item_port.item_done();
        end
    endtask

endclass

`endif
