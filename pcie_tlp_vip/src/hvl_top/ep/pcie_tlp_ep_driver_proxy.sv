// EP Driver Proxy
`ifndef PCIE_TLP_EP_DRIVER_PROXY_SVH
`define PCIE_TLP_EP_DRIVER_PROXY_SVH

import uvm_pkg::*; `include "uvm_macros.svh"; import pcie_tlp_globals_pkg::*; import pcie_tlp_ep_pkg::*;

class pcie_tlp_ep_driver_proxy extends uvm_driver #(pcie_tlp_ep_tx);
    `uvm_component_utils(pcie_tlp_ep_driver_proxy)
    pcie_tlp_ep_agent_config cfg;
    pcie_tlp_ep_memory memory;
    virtual pcie_tlp_ep_driver_bfm bfm;
    uvm_analysis_port #(pcie_tlp_ep_tx) rsp_port;
    semaphore write_sem;
    semaphore read_sem;

    function new(string name = "pcie_tlp_ep_driver_proxy", uvm_component parent = null);
        super.new(name, parent);
        rsp_port = new("rsp_port", this);
        write_sem = new(1);
        read_sem = new(1);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        `uvm_info(get_type_name(), "build_phase started", UVM_HIGH)
        if (!uvm_config_db#(virtual pcie_tlp_ep_driver_bfm)::get(this, "", "pcie_tlp_ep_driver_bfm", bfm)) begin
            `uvm_fatal(get_type_name(), "Failed to get BFM handle")
        end
        if (cfg == null) begin
            if (!uvm_config_db#(pcie_tlp_ep_agent_config)::get(this, "", "cfg", cfg)) begin
                `uvm_error(get_type_name(), "No config set, using defaults")
            end
        end
        if (memory == null) begin
            memory = pcie_tlp_ep_memory::type_id::create("memory", this);
            memory.min_address = cfg.min_address;
            memory.max_address = cfg.max_address;
            memory.memory_size = cfg.memory_size;
        end
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        `uvm_info(get_type_name(), "connect_phase started", UVM_HIGH)
        bfm.ep_drv_proxy_h = this;
    endfunction

    function void end_of_elaboration_phase(uvm_phase phase);
        super.end_of_elaboration_phase(phase);
        `uvm_info(get_type_name(), "end_of_elaboration_phase - EP Driver proxy ready", UVM_HIGH)
    endfunction

    function void start_of_simulation_phase(uvm_phase phase);
        super.start_of_simulation_phase(phase);
        `uvm_info(get_type_name(), "start_of_simulation_phase started", UVM_HIGH)
        bfm.wait_for_reset();
    endfunction

    task run_phase(uvm_phase phase);
        pcie_tlp_ep_tx req;
        super.run_phase(phase);
        `uvm_info(get_type_name(), "run_phase started", UVM_HIGH)
        forever begin
            seq_item_port.get_next_item(req);
            process_request(req);
            seq_item_port.item_done();
        end
    endtask

    task process_request(pcie_tlp_ep_tx req);
        tlp_t tlp;
        tlp.header.dw0[30:28] = req.req_fmt;
        tlp.header.dw0[24:19] = req.req_type;
        tlp.header.dw0[9:0]   = req.req_length;
        tlp.header.dw1        = req.req_address;
        tlp.header.dw2        = {req.req_tc, 5'b0, req.req_tag[7:0]};
        tlp.header.dw3        = {req.req_vc_id, req.req_seq_num, 26'b0};
        tlp.payload           = req.req_payload;
        tlp.payload_size      = req.payload_size;
        tlp.transaction_id    = req.transaction_id;
        tlp.timestamp         = $time;

        `uvm_info(get_type_name(), $sformatf("Processing request TLP ID %0d, fmt=%s, type=%s, addr=0x%08x",
                   tlp.transaction_id, req.req_fmt.name(), req.req_type.name(), req.req_address), UVM_MEDIUM)

        case (req.req_fmt)
            TLP_FMT_MEM_READ:  handle_mem_read(req, tlp);
            TLP_FMT_MEM_WRITE: handle_mem_write(req, tlp);
            TLP_FMT_CFG_READ:  handle_cfg_read(req, tlp);
            TLP_FMT_CFG_WRITE: handle_cfg_write(req, tlp);
            TLP_FMT_IO_READ:   handle_io_read(req, tlp);
            TLP_FMT_IO_WRITE:  handle_io_write(req, tlp);
            default: `uvm_error(get_type_name(), $sformatf("Unsupported TLP format: %s", req.req_fmt.name()))
        endcase
    endtask

    task handle_mem_read(pcie_tlp_ep_tx req, tlp_t tlp);
        logic [31:0] read_data;
        tlp_t comp_tlp;
        pcie_tlp_ep_tx rsp_item;
       int addr = req.req_address;
        read_sem.get(1);
        if (memory.is_addr_valid(addr)) begin
            read_data = memory.mem_read_word(addr);
        end else begin
            read_data = cfg.default_read_data;
            `uvm_warning(get_type_name(), $sformatf("Memory read out of range: 0x%08x", addr))
        end
        comp_tlp = tlp;
        comp_tlp.header.dw0[30:28] = TLP_FMT_MEM_READ;
        comp_tlp.header.dw0[24:19] = TLP_TYPE_CMPL;
        comp_tlp.header.dw0[9:0]   = 1;
        comp_tlp.payload = {32'h0, read_data};
        comp_tlp.payload_size = 4;
        comp_tlp.transaction_id = req.transaction_id;
        comp_tlp.timestamp = $time;
        repeat (req.wait_states) @(bfm.drv_cb);
        bfm.send_completion(comp_tlp);
        read_sem.put(1);
        rsp_item = pcie_tlp_ep_tx::type_id::create("rsp_item");
        rsp_item.comp_data = read_data;
        rsp_item.transaction_id = req.transaction_id;
        rsp_port.write(rsp_item);
    endtask

    task handle_mem_write(pcie_tlp_ep_tx req, tlp_t tlp);
        tlp_t comp_tlp;
        int addr = req.req_address;
        logic [31:0] write_data = req.req_payload[31:0];
        write_sem.get(1);
        if (memory.is_addr_valid(addr)) begin
            memory.mem_write_word(addr, write_data);
        end else begin
            `uvm_warning(get_type_name(), $sformatf("Memory write out of range: 0x%08x", addr))
        end
        comp_tlp = tlp;
        comp_tlp.header.dw0[30:28] = TLP_FMT_MEM_READ;
        comp_tlp.header.dw0[24:19] = TLP_TYPE_CMPL;
        comp_tlp.header.dw0[9:0]   = 0;
        comp_tlp.payload_size = 0;
        comp_tlp.transaction_id = req.transaction_id;
        comp_tlp.timestamp = $time;
        repeat (req.wait_states) @(bfm.drv_cb);
        bfm.send_completion(comp_tlp);
        write_sem.put(1);
    endtask

    task handle_cfg_read(pcie_tlp_ep_tx req, tlp_t tlp);
        tlp_t comp_tlp;
        logic [31:0] cfg_data;
        int offset = req.req_address & 32'hFF;
        cfg_data = memory.cfg_read(offset);
        comp_tlp = tlp;
        comp_tlp.header.dw0[30:28] = TLP_FMT_CFG_READ;
        comp_tlp.header.dw0[24:19] = TLP_TYPE_CMPL;
        comp_tlp.header.dw0[9:0]   = 1;
        comp_tlp.payload = {32'h0, cfg_data};
        comp_tlp.payload_size = 4;
        comp_tlp.transaction_id = req.transaction_id;
        comp_tlp.timestamp = $time;
        repeat (req.wait_states) @(bfm.drv_cb);
        bfm.send_completion(comp_tlp);
    endtask

    task handle_cfg_write(pcie_tlp_ep_tx req, tlp_t tlp);
        tlp_t comp_tlp;
        int offset = req.req_address & 32'hFF;
        logic [31:0] write_data = req.req_payload[31:0];
        memory.cfg_write(offset, write_data);
        comp_tlp = tlp;
        comp_tlp.header.dw0[30:28] = TLP_FMT_CFG_READ;
        comp_tlp.header.dw0[24:19] = TLP_TYPE_CMPL;
        comp_tlp.header.dw0[9:0]   = 0;
        comp_tlp.payload_size = 0;
        comp_tlp.transaction_id = req.transaction_id;
        comp_tlp.timestamp = $time;
        repeat (req.wait_states) @(bfm.drv_cb);
        bfm.send_completion(comp_tlp);
    endtask

    task handle_io_read(pcie_tlp_ep_tx req, tlp_t tlp);
        tlp_t comp_tlp;
        logic [31:0] io_data = 32'hFFFFFFFF;
        comp_tlp = tlp;
        comp_tlp.header.dw0[30:28] = TLP_FMT_IO_READ;
        comp_tlp.header.dw0[24:19] = TLP_TYPE_CMPL;
        comp_tlp.header.dw0[9:0]   = 1;
        comp_tlp.payload = {32'h0, io_data};
        comp_tlp.payload_size = 4;
        comp_tlp.transaction_id = req.transaction_id;
        comp_tlp.timestamp = $time;
        repeat (req.wait_states) @(bfm.drv_cb);
        bfm.send_completion(comp_tlp);
    endtask

    task handle_io_write(pcie_tlp_ep_tx req, tlp_t tlp);
        `uvm_info(get_type_name(), $sformatf("IO write addr=0x%08x data=0x%08x", req.req_address, req.req_payload[31:0]), UVM_MEDIUM)
    endtask

endclass

`endif
