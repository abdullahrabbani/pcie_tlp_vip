// EP Agent BFM
`ifndef PCIE_TLP_EP_AGENT_BFM_SVH
`define PCIE_TLP_EP_AGENT_BFM_SVH

import uvm_pkg::*;
`include "uvm_macros.svh"
import pcie_tlp_globals_pkg::*;
import pcie_tlp_ep_pkg::*;

module pcie_tlp_ep_agent_bfm #(parameter int EP_ID = 0)(
    pcie_tlp_if intf
);

    // NOTE: EP's tx_*/rx_* ports are cross-connected relative to RC's:
    // intf.tx_* is the bus RC transmits on (EP's rx), and intf.rx_* is the
    // bus EP transmits on (RC's rx). This keeps RC and EP from driving the
    // same wires simultaneously.
    pcie_tlp_ep_driver_bfm ep_drv_bfm (
        .clk(intf.clk),
        .rst_n(intf.rst_n),
        .tx_data(intf.rx_data),
        .tx_keep(intf.rx_keep),
        .tx_valid(intf.rx_valid),
        .tx_ready(intf.rx_ready),
        .tx_sop(intf.rx_sop),
        .tx_eop(intf.rx_eop),
        .tx_empty(intf.rx_empty),
        .tx_seq_num(intf.rx_seq_num),
        .tx_vc_id(intf.rx_vc_id),
        .tx_tc(intf.rx_tc),
        .rx_data(intf.tx_data),
        .rx_keep(intf.tx_keep),
        .rx_valid(intf.tx_valid),
        .rx_ready(intf.tx_ready),
        .rx_sop(intf.tx_sop),
        .rx_eop(intf.tx_eop),
        .rx_empty(intf.tx_empty),
        .rx_seq_num(intf.tx_seq_num),
        .rx_vc_id(intf.tx_vc_id),
        .rx_tc(intf.tx_tc)
    );

    pcie_tlp_ep_monitor_bfm ep_mon_bfm (
        .clk(intf.clk),
        .rst_n(intf.rst_n),
        .tx_data(intf.rx_data),
        .tx_keep(intf.rx_keep),
        .tx_valid(intf.rx_valid),
        .tx_ready(intf.rx_ready),
        .tx_sop(intf.rx_sop),
        .tx_eop(intf.rx_eop),
        .tx_empty(intf.rx_empty),
        .tx_seq_num(intf.rx_seq_num),
        .tx_vc_id(intf.rx_vc_id),
        .tx_tc(intf.rx_tc),
        .rx_data(intf.tx_data),
        .rx_keep(intf.tx_keep),
        .rx_valid(intf.tx_valid),
        .rx_ready(intf.tx_ready),
        .rx_sop(intf.tx_sop),
        .rx_eop(intf.tx_eop),
        .rx_empty(intf.tx_empty),
        .rx_seq_num(intf.tx_seq_num),
        .rx_vc_id(intf.tx_vc_id),
        .rx_tc(intf.tx_tc)
    );

    initial begin
        uvm_config_db#(virtual pcie_tlp_ep_driver_bfm)::set(null, "*", "pcie_tlp_ep_driver_bfm", ep_drv_bfm);
        uvm_config_db#(virtual pcie_tlp_ep_monitor_bfm)::set(null, "*", "pcie_tlp_ep_monitor_bfm", ep_mon_bfm);
        `uvm_info("PCIE_TLP_EP_AGENT_BFM", $sformatf("EP Agent BFM instantiated with ID %0d", EP_ID), UVM_LOW)
    end

endmodule : pcie_tlp_ep_agent_bfm

`endif
