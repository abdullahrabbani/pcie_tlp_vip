# Coding Guidelines

## UVM Coding Standards

1. All classes derived from `uvm_object` or `uvm_component`
2. Use `uvm_component_utils` and `uvm_object_utils` macros
3. Implement all UVM phases in every component:
   - `build_phase`
   - `connect_phase`
   - `end_of_elaboration_phase`
   - `start_of_simulation_phase`
   - `run_phase`
   - `extract_phase`
   - `check_phase`
   - `report_phase`
   - `final_phase`
4. Use `uvm_config_db` for configuration passing
5. All sequence items extend `uvm_sequence_item`
6. Use `uvm_analysis_port` for monitor connections
7. Follow SystemVerilog coding conventions
