// PCIe TLP VIP - Global Package
`ifndef PCIE_TLP_GLOBALS_PKG_SVH
`define PCIE_TLP_GLOBALS_PKG_SVH

package pcie_tlp_globals_pkg;

    // TLP Format
    typedef enum logic [2:0] {
        TLP_FMT_MEM_READ  = 3'b000,
        TLP_FMT_MEM_WRITE = 3'b001,
        TLP_FMT_IO_READ   = 3'b010,
        TLP_FMT_IO_WRITE  = 3'b011,
        TLP_FMT_CFG_READ  = 3'b100,
        TLP_FMT_CFG_WRITE = 3'b101,
        TLP_FMT_MSG       = 3'b110,
        TLP_FMT_MSG_DATA  = 3'b111
    } tlp_fmt_e;

    // TLP Type
    typedef enum logic [5:0] {
        TLP_TYPE_MEM_RD   = 6'b000000,
        TLP_TYPE_MEM_WR   = 6'b000001,
        TLP_TYPE_IO_RD    = 6'b000010,
        TLP_TYPE_IO_WR    = 6'b000011,
        TLP_TYPE_CFG_RD   = 6'b000100,
        TLP_TYPE_CFG_WR   = 6'b000101,
        TLP_TYPE_MSG      = 6'b001000,
        TLP_TYPE_MSG_DATA = 6'b001001,
        TLP_TYPE_CMPL     = 6'b001010
    } tlp_type_e;

    // Write/Read data mode
    typedef enum {
        WRITE_READ_DATA,
        WRITE_ONLY,
        READ_ONLY
    } write_read_data_mode_e;

    // TLP Header
    typedef struct packed {
        logic [31:0] dw0;
        logic [31:0] dw1;
        logic [31:0] dw2;
        logic [31:0] dw3;
    } tlp_header_t;

    // TLP Transaction
    typedef struct {
        tlp_header_t    header;
        logic [1023:0]  payload;
        int             payload_size;
        int             transaction_id;
        time            timestamp;
    } tlp_t;

    // Configuration Space
    typedef struct packed {
        logic [15:0] vendor_id;
        logic [15:0] device_id;
        logic [15:0] command;
        logic [15:0] status;
        logic [31:0] class_code;
        logic [31:0] base_address_0;
        logic [31:0] base_address_1;
    } pcie_tlp_config_space_t;

    // Parameters
    parameter PCIE_TLP_MAX_PAYLOAD = 256;
    parameter PCIE_TLP_TIMEOUT     = 1000;

    // Utility functions
    function automatic tlp_fmt_e get_tlp_fmt(tlp_t t);
        return tlp_fmt_e'(t.header.dw0[30:28]);
    endfunction

    function automatic tlp_type_e get_tlp_type(tlp_t t);
        return tlp_type_e'(t.header.dw0[24:19]);
    endfunction

endpackage

`endif
