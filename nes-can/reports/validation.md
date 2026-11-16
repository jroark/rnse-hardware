# CAD and firmware verification — 2026-11-15

- KiCad 10.0.3 ERC: zero violations.
- KiCad PCB DRC: zero violations and zero unconnected pads.
- Schematic-to-PCB audit: 160 numbered pin/net assignments match.
- Minimum routed copper width: 0.1874 mm (project minimum 0.15 mm).
- Two copper layers, 65 × 45 mm; grounded pours on both layers.
- Schematic, assembly and board-top PDF exports rendered and visually inspected.
- ATtiny1616 normal-mode firmware builds without warnings using AVR GCC 7.3.0,
  avr-libc and Microchip ATtiny_DFP 3.1.260; 892 bytes program, zero static data/BSS.
- Firmware-backed RNS-E integration test passes video, audio, two-player CAN state,
  timeout release, repeat launch and long-RETURN recovery; no flash changes.

No fabrication, electrical measurements, physical controller tests, vehicle
installation, EMC qualification, or physical RNS-E performance testing performed.
