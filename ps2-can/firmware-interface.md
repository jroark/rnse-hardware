# Firmware interface specification (implementation deferred)

All signals are 5 V. Use interrupt-driven acquisition and bounded queues; no
blocking loop may prevent receipt of the other PS/2 device or CAN service.

| AVR pin | Port | Function |
|---|---|---|
| 1 / 20 | VDD / GND | 5 V / common ground |
| 2 | PA4 | MCP2515 CS, active low; default high |
| 3 | PA5 | MCP2515 INT, active low |
| 4 / 5 | PA6 / PA7 | Keyboard clock / data |
| 6 / 7 | PB5 / PB4 | Mouse clock / data |
| 8 / 9 | PB3 / PB2 | TJA1055 EN / STB; default low |
| 10 | PB1 | TJA1055 ERR, active low |
| 11 | PB0 | Activity LED, high lights LED |
| 12–15 | PC0–PC3 | Spare, no external connection |
| 16 | PA0 | UPDI; retain programming function |
| 17 / 18 / 19 | PA1 / PA2 / PA3 | SPI MOSI / MISO / SCK, default pin mapping |

PS/2 outputs must only drive low or release (input mode); never drive high.
Use external pull-ups and AVR edge interrupts to acquire frames. Handle parity,
start/stop bits, host commands and device reset. Accept keyboard scan set 2,
including E0/E1 prefixes, break codes and modifiers. Initialize the mouse and
negotiate wheel support if available; handle a standard three-byte mouse too.
On queue overflow or malformed frames, send a state-reset status and reinitialize
the affected device. CS must be high before enabling SPI; use the hardware SPI
master mode and software-controlled CS. Reset the MCP2515 with its SPI command.

For MCP2515 at 16 MHz, a candidate 100 kbit/s timing is CNF1=0x03, CNF2=0xBE,
CNF3=0x03: 20 time quanta (1 + 7 + 8 + 4), 80% sample point, SJW=1 TQ.
The prescaler is 4: 16 MHz / (2 × 4 × 20) = 100 kbit/s. Verify bit timing on the
bench. Start with loopback, then listen-only, then normal mode only after receiver
integration is ready. EN=1/STB=1 selects normal transceiver operation. Hold both
low on startup, failed initialization, watchdog reset and unrecoverable CAN faults.

## Proposed classical CAN protocol v1

IDs below are **bench defaults**, not reserved Audi identifiers. Make them
configurable and check real vehicle traffic before transmitting. Standard 11-bit
frames, DLC 8, unused bytes zero. Each stream has its own modulo-256 sequence.

| ID | Payload bytes 0…7 |
|---|---|
| 0x6E0 keyboard | version=1, sequence, count=1…5, up to five raw PS/2 set-2 bytes |
| 0x6E1 mouse | version=1, sequence, button bitmap, dx low, dx high, dy low, dy high, wheel |
| 0x6E2 status | version=1, sequence, flags, reset reason, overflow count low, high, 0, 0 |

Mouse dx/dy are signed 16-bit little-endian values in Linux pointer coordinates
(right/down positive); wheel is signed 8-bit, up positive. Button bits 0/1/2 are
left/right/middle. Status bits 0/1 mean keyboard/mouse present; bit 2 means a
stream reset and requires the receiver to release all keys/buttons and discard
partial scan prefixes. Send that flag after boot, device disconnect or overflow.

Send status every 100 ms. Coalesce mouse movement into at most 25 packets/s;
never discard accumulated motion silently. Keyboard packets preserve byte order
and may carry a prefix split across frames. Limit total traffic to 80 frames/s,
prioritizing keyboard and reset/status over mouse motion. An 8-byte frame takes
roughly 1.3 ms on this bus; the ceiling bounds average added traffic near 10%.
Actual arbitration may add latency; bound queues and report overload.

The Linux receiver must reject bad version/count/DLC, track sequences, release
held state on stream gaps and on 350 ms status timeout, and require a fresh
keyboard reset after a gap to avoid interpreting an orphan scan-code suffix.
Its input devices should expose keyboard keys/modifiers, mouse relative axes,
wheel and buttons through the kernel input subsystem. Mouse buttons are complete
snapshots in every mouse frame. No input packet invokes stock updater handoffs.

The board only supports transport. Linux CAN controller support and input event
mapping must be added separately while preserving independent physical
faceplate/display-open/disc-eject service, including under CAN flood and faults.
