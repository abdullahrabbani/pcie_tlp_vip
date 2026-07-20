// EP Memory Model
`ifndef PCIE_TLP_EP_MEMORY_SVH
`define PCIE_TLP_EP_MEMORY_SVH

import uvm_pkg::*; `include "uvm_macros.svh"
import pcie_tlp_globals_pkg::*;

class pcie_tlp_ep_memory extends uvm_object;
    `uvm_object_utils(pcie_tlp_ep_memory)

    protected bit [7:0] memory [longint];
    protected bit [31:0] config_space [0:63];
    protected bit [7:0] io_space [longint];
    bit [7:0] fifo_memory [$:PCIE_TLP_MAX_PAYLOAD-1];

    int min_address = 32'h0000_0000;
    int max_address = 32'h0000_0FFF;
    int memory_size = 4096;
    bit [31:0] default_read_data = 32'hDEAD_BEEF;

    function new(string name = "pcie_tlp_ep_memory");
        super.new(name);
        init_config_space();
    endfunction

    function void init_config_space();
        config_space[0] = {16'h7011, 16'h10EE};
        config_space[1] = 32'h0000_0007;
        config_space[2] = 32'h06040000;
        config_space[3] = 32'h00000000;
        config_space[4] = 32'h0000_0000;
        config_space[5] = 32'h0000_0000;
    endfunction

    function void mem_write(input int address, input bit [7:0] data);
        if (address inside {[min_address:max_address]}) begin
            memory[address] = data;
        end else begin
            `uvm_warning(get_type_name(), $sformatf("Memory write out of range: 0x%08x", address))
        end
    endfunction

    function bit [7:0] mem_read(input int address);
        if (address inside {[min_address:max_address]}) begin
            if (memory.exists(address)) return memory[address];
            else return default_read_data[7:0];
        end else begin
            `uvm_warning(get_type_name(), $sformatf("Memory read out of range: 0x%08x", address))
            return default_read_data[7:0];
        end
    endfunction

    function void mem_write_word(input int address, input bit [31:0] data);
        for (int i = 0; i < 4; i++) begin
            mem_write(address + i, data[8*i +: 8]);
        end
    endfunction

    function bit [31:0] mem_read_word(input int address);
        bit [31:0] data;
        for (int i = 0; i < 4; i++) begin
            data[8*i +: 8] = mem_read(address + i);
        end
        return data;
    endfunction

    function void cfg_write(input int offset, input bit [31:0] data);
        if (offset < 64) begin
            config_space[offset] = data;
        end else begin
            `uvm_warning(get_type_name(), $sformatf("Config write out of range: offset 0x%04x", offset))
        end
    endfunction

    function bit [31:0] cfg_read(input int offset);
        if (offset < 64) begin
            return config_space[offset];
        end else begin
            `uvm_warning(get_type_name(), $sformatf("Config read out of range: offset 0x%04x", offset))
            return 32'hFFFFFFFF;
        end
    endfunction

    function void io_write(input int address, input bit [7:0] data);
        io_space[address] = data;
    endfunction

    function bit [7:0] io_read(input int address);
        if (io_space.exists(address)) return io_space[address];
        else return default_read_data[7:0];
    endfunction

    function void fifo_write(input bit [7:0] data);
        if (fifo_memory.size() < PCIE_TLP_MAX_PAYLOAD) begin
            fifo_memory.push_front(data);
        end else begin
            `uvm_error(get_type_name(), "FIFO overflow")
        end
    endfunction

    function bit [7:0] fifo_read();
        bit [7:0] data;
        if (fifo_memory.size() > 0) begin
            data = fifo_memory.pop_back();
            return data;
        end else begin
            `uvm_error(get_type_name(), "FIFO underflow")
            return 8'h00;
        end
    endfunction

    function bit is_addr_valid(input int address);
        return (address inside {[min_address:max_address]});
    endfunction

    function bit is_addr_exists(input int address);
        return memory.exists(address);
    endfunction

    function void clear_memory();
        memory.delete();   // ? Clears associative array
        
        fifo_memory = '{};
    endfunction

    function void do_print(uvm_printer printer);
        super.do_print(printer);
        printer.print_field("min_address", min_address, $bits(min_address), UVM_HEX);
        printer.print_field("max_address", max_address, $bits(max_address), UVM_HEX);
        printer.print_field("memory_size", memory_size, $bits(memory_size), UVM_DEC);
        printer.print_field("default_read_data", default_read_data, $bits(default_read_data), UVM_HEX);
        printer.print_field("memory_entries", memory.size(), $bits(memory.size()), UVM_DEC);
        printer.print_field("fifo_size", fifo_memory.size(), $bits(fifo_memory.size()), UVM_DEC);
        for (int i = 0; i < 16 && i < 64; i++) begin
            printer.print_field($sformatf("config[%0d]", i), config_space[i], 32, UVM_HEX);
        end
    endfunction

endclass

`endif
