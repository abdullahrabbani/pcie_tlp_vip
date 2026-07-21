// ============================================================================
// PCIe TLP VIP - Compile File
// File: pcie_tlp_compile.f
// Description: Compile file for PCIe TLP VIP
// ============================================================================

// ============================================================================
// UVM Options
// ============================================================================
-sv

// ============================================================================
// Include Directories
// ============================================================================

// Global
+incdir+../../src/globals/

// HDL Top
+incdir+../../src/hdl_top/pcie_tlp_interface/
+incdir+../../src/hdl_top/rc_agent_bfm/
+incdir+../../src/hdl_top/ep_agent_bfm/

// HVL - RC Agent
+incdir+../../src/hvl_top/rc/

// HVL - EP Agent
+incdir+../../src/hvl_top/ep/

// HVL - Environment
+incdir+../../src/hvl_top/env/
+incdir+../../src/hvl_top/env/virtual_sequencer/

// HVL - Test
+incdir+../../src/hvl_top/test/
+incdir+../../src/hvl_top/test/sequences/rc_sequences/
+incdir+../../src/hvl_top/test/sequences/ep_sequences/
+incdir+../../src/hvl_top/test/virtual_sequences/

// ============================================================================
// Global Package
// ============================================================================
../../src/globals/pcie_tlp_globals_pkg.sv

// ============================================================================
// HVL Packages
// ============================================================================
../../src/hvl_top/rc/pcie_tlp_rc_pkg.sv
../../src/hvl_top/ep/pcie_tlp_ep_pkg.sv
../../src/hvl_top/env/pcie_tlp_env_pkg.sv

// ============================================================================
// Sequence Packages
// ============================================================================
../../src/hvl_top/test/sequences/rc_sequences/pcie_tlp_rc_seq_pkg.sv
../../src/hvl_top/test/sequences/ep_sequences/pcie_tlp_ep_seq_pkg.sv
../../src/hvl_top/test/virtual_sequences/pcie_tlp_vseq_base_pkg.sv

// ============================================================================
// Tests
// ============================================================================
../../src/hvl_top/test/pcie_tlp_test_pkg.sv

// ============================================================================
// Interface
// ============================================================================
../../src/hdl_top/pcie_tlp_interface/pcie_tlp_if.sv

// ============================================================================
// RC Agent BFMs (HDL)
// ============================================================================
../../src/hdl_top/rc_agent_bfm/pcie_tlp_rc_agent_bfm.sv
../../src/hdl_top/rc_agent_bfm/pcie_tlp_rc_driver_bfm.sv
../../src/hdl_top/rc_agent_bfm/pcie_tlp_rc_monitor_bfm.sv

// ============================================================================
// EP Agent BFMs (HDL)
// ============================================================================
../../src/hdl_top/ep_agent_bfm/pcie_tlp_ep_agent_bfm.sv
../../src/hdl_top/ep_agent_bfm/pcie_tlp_ep_driver_bfm.sv
../../src/hdl_top/ep_agent_bfm/pcie_tlp_ep_monitor_bfm.sv

// ============================================================================
// Assertions
// ============================================================================
../../src/hdl_top/pcie_tlp_rc_assertions.sv
../../src/hdl_top/pcie_tlp_ep_assertions.sv
../../src/hdl_top/pcie_tlp_tb_rc_assertions.sv
../../src/hdl_top/pcie_tlp_tb_ep_assertions.sv

// ============================================================================
// Top-Level Modules
// ============================================================================
../../src/hdl_top/pcie_tlp_hdl_top.sv
../../src/hvl_top/pcie_tlp_hvl_top.sv


