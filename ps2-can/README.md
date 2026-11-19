# RNS-E PS/2 to CAN adapter — revision A

Open **ps2-can.kicad_pro** in KiCad 10. This project contains an editable schematic,
a 65 × 45 mm two-layer PCB and local libraries. All parts mount on the top side.
The design is a prototype: it has not been fabricated or electrically tested.
Adapter firmware and the RNS-E Linux CAN/input driver are not included.

## Connections

| Connector | Pin | Signal |
|---|---|---|
| J1 vehicle, numbered square pad first | 1 | Switched +12 V |
| J1 | 2 | Ground |
| J1 | 3 | Infotainment CANH |
| J1 | 4 | Infotainment CANL |
| J2 keyboard / J3 mouse | 1 | PS/2 data |
| J2 / J3 | 2, 6 | Unconnected |
| J2 / J3 | 3 | Ground |
| J2 / J3 | 4 | Individually fused +5 V |
| J2 / J3 | 5 | PS/2 clock |
| J4 UPDI | 1 | +5 V target voltage reference |
| J4 | 2 | UPDI / PA0 |
| J4 | 3 | Ground |

J4 is a **5 V UPDI** connection. Power the target from J1; configure the programmer
to sense target voltage without supplying it. Preserve PA0's UPDI fuse setting.
The peripheral sockets are for genuine PS/2 devices; passive USB adapters require
peripherals that explicitly support PS/2. Connect peripherals with power off.
The board shares ground with the vehicle; it is not isolated.

## Ordering

Use [the current stock update](ordering/stock-update.md) for revised headerless
DigiKey and Mouser orders. The base [distributor order files](ordering/README.md)
record the design-MPN baseline for one-board DigiKey or
Mouser upload. They group the BOM into 24 lines / 48 components, excluding bare
test pads. The checked BOM corrects the F1 fuse and Y1 crystal package selections
and uses an orderable Vishay SS16 for D1; the existing PCB fits these parts.

## Assembly

Use `bom.csv` for exact MPNs and search links; `previews/assembly.pdf` identifies
parts. Purchase MD-60S sockets made **after 2022-03-03**. Earlier versions have
different hole spacing. The custom footprint follows the current top-view drawing:
pins 4/2/1/3 at x = -3.4/-1.3/+1.3/+3.4 mm, y = 8.5 mm from the front;
pins 6/5 at x = -3.4/+3.4 mm, y = 11 mm; locating slot 2.2 × 0.7 mm at y = 4.7 mm.
Confirm the supplied socket against a 1:1 print before soldering.

Fit resistors/capacitors and SOIC devices first, then power protection, LEDs,
crystal, regulator and connectors. Use flux and an ordinary fine soldering tip.
The SOD-323 ESD diodes are the smallest parts; they have exposed terminals and
are bidirectional, so either orientation works. D1/D2 and LEDs are polarized:
follow the cathode marks and assembly drawing. SOIC pin 1 uses the dot/notch.
TP1–TP4 are bare plated holes, not purchased components. H1–H4 accept M2 hardware.
Allow clearance under the board for the mini-DIN locating tabs and solder joints.

## Power and CAN design

J1 input passes through a 0.5 A fuse and SS16 reverse-polarity diode. SMBJ18A
clamps the protected VBAT rail. TSR 1-2450 converts it to 5 V with a 1 A rating.
Input operation is nominally 9–16 V; brownout/reset during cranking is acceptable.
C5 is rated 50 V; the regulator input limit is 36 V and TJA1055 BAT limit is 40 V.
The TVS nominal maximum clamp is 29.2 V at its specified pulse current, below both
limits. This comparison does not establish load-dump immunity: fuse opening time,
TVS energy, source impedance and wiring overshoot need physical testing. Do not
use a continuously applied supply above the TVS stand-off rating.

Each PS/2 port has a 0.20 A hold PTC (temperature dependent). Budget 100 mA each
for keyboard and mouse and approximately 100 mA for board/CAN operation. The
regulator has margin for startup and CAN activity, but these ports are not intended
for illuminated high-current peripherals. Routing uses 0.25 mm tracks with 0.1874 mm fanout sections,
0.20 mm clearances and 0.6/0.3 mm vias. The project minimum trace width is 0.15 mm;
see the PCB width audit for actual widths. Both copper layers have grounded pours; no assumption of automotive EMC
qualification is made.

The bus interface is **TJA1055T**, fault-tolerant ISO 11898-3. A TJA1051, MCP2551,
SN65HVD230 or conventional high-speed CAN module is not a substitute. The MCP2515
is the CAN protocol controller; its 16 MHz crystal supplies the accurate CAN clock.
The AVR uses its internal clock. No CAN FD is used.

R13/R14 provide distributed termination to TJA1055 RTH/RTL, initially 5.6 kΩ each.
They are not a 120 Ω termination across CANH/CANL. NXP recommends a whole-network
effective termination of approximately 100 Ω per line; actual node resistors and
network topology determine the result. The fitted values minimally load an
existing vehicle network. For a small bench network, inspect the other node's
termination and select an appropriate pair (within the manufacturer's limits),
then verify bus levels and error counters. Do not expect a two-node bench with
two 5.6 kΩ terminations to represent a correctly terminated vehicle network.

CAN EN/STB have pull-downs, so the board powers up in standby. TXD has a pull-up;
MCP2515 CS and RESET are pulled high. INH is intentionally unconnected. WAKE is
held to protected VBAT through 10 kΩ. This revision uses switched power; it does
not implement an always-on wake/power manager.

## Firmware interfaces and bring-up

See `firmware-interface.md` for the pin allocation and proposed wire protocol.
The Linux configuration in this repository has evdev but no networking; CAN and
input integration are additional work, not provided by this circuit.

1. Inspect soldering and resistance between VBAT/5 V and ground with power off.
2. With peripherals and vehicle CAN disconnected, apply a current-limited 12 V
   bench supply (start at 100 mA). Check VBAT polarity, 5 V regulation and POWER LED.
3. Attach a 5 V UPDI programmer to J4. Read device identity before programming.
   Start with transceiver EN/STB low; check both with a meter or logic analyzer.
4. Test each PS/2 device separately. Verify idle-high clock/data, reset/BAT exchange,
   open-drain host signaling and independent port fuses. Increase supply current
   limit only as required for the measured peripheral load.
5. Test MCP2515 SPI identity/configuration and internal loopback before enabling
   the transceiver. Check oscillator startup and the selected CAN timing.
6. Connect a correctly terminated **fault-tolerant** CAN bench node and a common
   ground. Start with receive-only operation. Verify ACKs, error counters, bus
   voltage levels and 100 kbit/s timing before transmitting test input packets.
7. Validate CAN identifiers against the actual vehicle network before installation.
   Use bounded packet rates and disable transmission on bus-off or firmware faults.
8. Before any RNS-E hardware test payload is delivered, verify the actual physical
   display-open motor command and separate disc-eject command on normal/error
   screens and during reads/initialization. Keep polling responsive and audit any
   loader/updater handoff. A reset, return shortcut or displayed eject button is
   not proof of physical ejection. This PCB does not replace that control path.

## Files and reproduction

- `ps2-can.kicad_sch`, `.kicad_pcb`, `.kicad_pro`: editable source.
- `ps2-can.kicad_sym`, `ps2-can.pretty/`, library tables: local symbols/footprints.
- `bom.csv`, `connectivity.json`: purchase list and reference connectivity/placement.
- `previews/`: schematic, assembly and board previews.
- `manufacturing/`: Gerbers and Excellon drills for 2 layers, 1.6 mm FR-4, 1 oz copper.
- `reports/`: ERC, DRC, exported schematic netlist and connectivity/width audits.
- `generate.py`: regenerates schematic and **unrouted** PCB; overwrites manual edits.
- `ps2-can.dsn`, `final.ses`: Specctra interchange for the final route.

Generation uses KiCad's bundled Python with `pcbnew`. Route the DSN with
Freerouting 2.5.0, fanout enabled, automatic neckdown disabled and optimization
disabled; the final session routes every connection. Export the schematic XML
netlist to `reports/schematic.xml` before finishing the board. `finish.py` imports the resulting session and fills the ground
zones. Run `label-board.py` once to place the silkscreen legends, then run checks/export again after any change; do not reuse stale Gerbers.
Project symbols deliberately show actual pin numbers and explicit net labels.

## Manufacturer references

- [ATtiny1616 datasheet](https://ww1.microchip.com/downloads/aemDocuments/documents/MCU08/ProductDocuments/DataSheets/ATtiny1614-16-17-DataSheet-DS40002204A.pdf)
- [MCP2515 datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/MCP2515-Stand-Alone-CAN-Controller-with-SPI-20001801J.pdf)
- [TJA1055 datasheet](https://www.nxp.com/docs/en/data-sheet/TJA1055.pdf) and [application guidance](https://www.nxp.com/docs/en/application-note/AH0801.pdf)
- [MD-S socket drawing, page 3](https://www.sameskydevices.com/product/resource/md-s.pdf)
- [TSR 1 regulator datasheet](https://www.tracopower.com/sites/default/files/products/datasheets/tsr1_datasheet.pdf)
- [PESD5V0S1BA datasheet](https://assets.nexperia.com/documents/data-sheet/PESD5V0S1BA.pdf)

KiCad-derived local footprints retain their original library provenance and are
covered by the KiCad libraries' CC BY-SA 4.0 license with their exception for
commercial PCB fabrication. No third-party firmware is included.
