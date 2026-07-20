# PCIe TLP VIP

Complete UVM-based verification IP for PCIe TLP.

## UVM Phases Implemented

All components implement the full UVM phase flow:

- **build_phase**: Component creation and configuration
- **connect_phase**: TLM connections between components
- **end_of_elaboration_phase**: Post-construction checks
- **start_of_simulation_phase**: Pre-simulation initialization
- **run_phase**: Main simulation task
- **extract_phase**: Data extraction from components
- **check_phase**: Assertion checking
- **report_phase**: Final report generation
- **final_phase**: Cleanup

## Directory Structure

- `src/` - Source files
  - `globals/` - Global package
  - `hdl_top/` - HDL top and BFMs
  - `hvl_top/` - HVL environment
    - `rc/` - Root Complex agent
    - `ep/` - Endpoint agent
    - `env/` - Environment and virtual sequencer
    - `test/` - Test classes
    - `test/sequences/` - Sequence classes
- `sim/` - Simulation scripts and makefiles

## Usage

```bash
cd sim
make compile
make sim TEST=pcie_tlp_base_test
```
