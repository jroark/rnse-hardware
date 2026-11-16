# Dual NES controller to RNS-E CAN — revision A

Open `nes-can.kicad_pro` in KiCad 10. Editable schematic, local libraries,
65 × 45 mm two-layer routed PCB, manufacturing plots, BOM and assembly PDF.
This is an unbuilt prototype. ERC/DRC results describe CAD checks, not physical
validation or automotive qualification.

## Wiring

| Connector | Pins, in numbered order |
|---|---|
| J1 | 1 switched +12 V, 2 ground, 3 infotainment CANH, 4 CANL |
| J2 player 1 / J3 player 2 | 1 fused +5 V, 2 ground, 3 latch, 4 clock, 5 data |
| J4 UPDI | 1 target +5 V reference, 2 UPDI, 3 ground |

Use female ends of original NES extension cables, terminated to J2/J3. Verify
each cable by continuity; cable colors are not a pinout. Using NESdev's socket
numbering (looking into the console socket), NES pins 1/2/3/4/7 are respectively
ground/clock/latch/data/+5 V; pins 5/6 are unused. Include a connector-view drawing
from https://www.nesdev.org/wiki/Controller_port_pinout when preparing the harness.
Do not confuse socket and mating-plug views. The headers have square pin-1 pads.

ATtiny PA6/PA7 are player 1 clock/data; PB5/PB4 player 2 clock/data;
PC2/PC3 are player 1/2 latch. PA1/PA2/PA3 are SPI MOSI/MISO/SCK;
PA4 chip select; PA5 CAN interrupt; PB3/PB2 transceiver EN/STB;
PB1 transceiver ERR; PB0 activity LED. PA0 remains UPDI.

## Power and bus

Nominal switched 9–16 V input, fused and reverse-polarity protected, with SMBJ18A
clamp and TSR 1-2450 5 V converter. Each controller has a 0.20 A PTC.
The board shares vehicle ground. Load-dump immunity, EMC and fault survival
require bench validation. Clock/data have series resistors and external ESD
clamps; latch outputs have series resistors and MCU input protection only.

Use **TJA1055 fault-tolerant CAN**, not a high-speed CAN module. MCP2515 has a
16 MHz crystal; CNF1/2/3 are 03/BE/03: 100 kbit/s, 80% sample point.
R13/R14 are 5.6 kΩ distributed termination to RTH/RTL. Do not add 120 Ω across
CANH/CANL. Bench termination must be chosen for the actual network, following
the TJA1055 datasheet. Default-low EN/STB holds standby during initialization.
Firmware enters standby on detected bus-off, then retries initialization.

## Firmware

Install avr-gcc, avr-libc and make. Download Microchip ATtiny_DFP 3.1.260 from
https://packs.download.microchip.com/Microchip.ATtiny_DFP.3.1.260.atpack and extract
it outside the repository. Pack SHA256: `59e3b4317cfc3a07a4ee637e49df44c5bd9025d08cf071b4d0d0c83396af5aae`. Build with:

```
make -C hardware/nes-can/firmware DFP=/path/to/extracted/pack
```

Output: `firmware/build/nes-can.hex`. Program with a 5 V-compatible UPDI programmer;
power the board from J1 and configure the programmer to sense target voltage
without supplying power. Preserve UPDI and the 20 MHz internal oscillator fuse.
The Makefile does not change fuses. The MCU disables its startup clock prescaler.
Use `EXTRA_CFLAGS=-DCAN_MODE=0x40` for internal MCP2515 loopback, or 0x60 for
listen-only. Normal operation is default; verify bus traffic before connecting.

## Protocol v1

Configurable standard ID 0x6e3, DLC 8. This is a bench default, not an Audi-reserved
identifier. Change `NES_CAN_ID` in both firmware and emulator builds if needed.

| Byte | Meaning |
|---|---|
| 0 | Version 1 |
| 1 | Modulo-256 sequence, increment after accepted TX request |
| 2/3 | Player 1/2 full button state |
| 4 | Bit 0: adapter restarted / reinitialized; other bits zero |
| 5–7 | Zero |

Button bits 0–7: A, B, Select, Start, Up, Down, Left, Right; set means pressed.
Poll both pads every approximately 4 ms; send changes at most every 10 ms and
heartbeat at least every 50 ms. One-shot CAN transmission bounds retries;
new snapshots supersede unsent state. Mechanical unplug detection is unavailable:
pulled-up data reads as all buttons released. No presence flag is claimed.
The receiver rejects malformed packets, ignores duplicate sequences without
refreshing freshness, and clears held input after 200 ms. Gaps clear old state
before applying the newly received full snapshot. Both players share freshness.

## Bring-up

1. Check resistance/polarity unpowered. Apply current-limited 12 V without pads
   or CAN attached. Confirm protected VBAT, 5 V, and EN/STB low before firmware.
2. Program UPDI; check latch ≥12 µs and clock half-period ≥6 µs, both controllers'
   button order, idle released state and supply current.
3. Build loopback firmware and verify MCP2515 timing/configuration, then use
   listen-only on the intended bus. Confirm ID availability before normal mode.
4. On a correctly terminated bench bus, verify both full-state bytes, reset flag,
   50 ms heartbeat, 100 frames/s ceiling, no-ACK behavior and bus-off recovery.
5. Test the RNS-E receiver's timeout release, repeated sessions, display/eject
   and long-RETURN recovery before physical installation.

`generate.py` creates placement, libraries, netlist source, and DSN. Route DSN with
Freerouting, export the schematic XML to reports/schematic.xml, run `finish.py`
to import final.ses and fill ground zones, then `finalize.py` for label placement.
Run ERC/DRC after any change and regenerate manufacturing plots from the checked
PCB. `connectivity.json` records numbered pin assignments; `bom.csv` lists MPNs.
