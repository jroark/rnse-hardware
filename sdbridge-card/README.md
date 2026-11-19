# RNS-E 192 SD bridge card · Rev A

This is the slot-powered version of the Pico SD bridge. The assembled carrier has the outline of a full-size SD card. A bare RP2040 and 2 MiB Winbond flash sit inside it. The phone plugs into a USB-A receptacle wired behind the modified cage. All wiring stays behind the cage and clear of the screen opening.

Open **sdbridge-card.kicad_pro** in KiCad 10 with its standard libraries installed. The project includes local symbols and a card-side contact footprint. The CAD and electrical checks below are complete. The new assembly still needs qualification in an actual 192.

- **PCB order** — [Gerbers, drill, layer job and fabrication notes](manufacturing/sdbridge-card-revA.zip). Quote the **0.40 mm** finished stack and selective hard gold explicitly.
- **PCB assembly** — [BOM with manufacturer part numbers](manufacturing/bom.csv) and [top-side placement](manufacturing/placement.csv). J1 is the nine-finger pattern. TP1–7 are bare probe pads.
- **Carrier** — [dimensioned assembly](mechanical/assembly.svg), [carrier STEP](mechanical/carrier.step), [tray STL](mechanical/tray.stl), [lid STL](mechanical/lid.stl) and [solid fit gauge](mechanical/fit-gauge.stl). STL dimensions are millimetres. The KiCad board outline is the insert. Both insulating shell halves are required for the finished profile.
- **Installation** — [rear cage wiring drawing](mechanical/cage-wiring.svg). It identifies tails by electrical continuity, since the board-side tail order depends on the socket.

## Cage wiring

Use the second slot for the bridge if the first slot holds the viewer software. Disconnect power and remove all cards before altering the cage. Identify each spring and its solder tail with a continuity meter. On the contact face, the finger beside the diagonal corner is pin **9**. The narrow finger at the far end of the row is pin **8**.

| Card finger | Card circuit | Back of the modified cage |
|---|---|---|
| 1 · DAT3 | Isolated gold land | Original connection |
| 2 · CMD | R2, 100 Ω to GP3 | Original connection |
| 3, 6 · VSS | Ground | Common return for card, VBUS source and USB-A pin 4 |
| 4 · VDD | Slot 3.3 V to RP2040 and flash | Original 3.3 V connection |
| 5 · CLK | R1, 100 Ω to GP2 | Original connection |
| 7 · DAT0 | R3, 100 Ω to GP4 | Original connection |
| **8 · DAT1** | **R4, 27 Ω to USB_DP** | **Isolated tail to USB-A pin 3, D+** |
| **9 · DAT2** | **R5, 27 Ω to USB_DM** | **Isolated tail to USB-A pin 2, D−** |

Lift or otherwise isolate just tails 8 and 9 from their original RNS-E data traces. Leave both springs able to move. Verify an open circuit from each lifted tail to its former board pad and between the two lifted tails, with the card and harness disconnected. Attach the two data wires as a short USB pair, with strain relief on the stationary housing. Check continuity end to end to the **numbered pins of the actual receptacle**.

Supply USB-A pin 1 from a separate switched, regulated, current-limited **5 V** source behind the cage, sized for the phone and cable. Join its return to card ground. Sequence phone VBUS with the powered bridge, including shutdown. The card uses only slot 3.3 V. Verify isolation between USB 5 V and SD pin 4 before applying power. Mark the modified socket for this bridge because the original four-bit SD data path has been repurposed.

## Mechanical assembly

The latch, fixed write-enable profile, card-detect edge, recessed contact channels and 22 mm lower shoulder are in the carrier. The electronic insert measures **21.50 × 30.60 mm**. The assembled outline measures **24.00 × 32.00 × 2.10 mm**. The geometry follows the card views and contact numbering in figures 2-1 and 2-2 of the SanDisk manual. [SanDisk SD Card Product Manual, revision 2.2](https://www.openimpulse.com/blog/wp-content/uploads/wpsc/downloadables/SD-Card-Simplified-Specification.pdf)

1. Make the solid gauge at 1:1. For the installed parts, use dimensionally stable insulating material suitable for the cabin temperature, such as precision-machined polycarbonate. The lid has a **0.10 mm roof** over U1 and Y1. Confirm the manufacturing process can hold it. Remove sharp edges, support marks and flash, especially at the nose and latch.
2. Check the unpowered gauge in the actual cage against a known-good card. Match insertion force, latched depth, card-detect switch operation and push-to-release. With the gauge fully latched, check screen closing and reopening and inspect for rub marks. Stop if it binds. A successful gauge test qualifies the outline only.
3. Program and bench-test the PCB before closing the lid. Seat it gold face down on the hard lands. Use small amounts of nonconductive adhesive in the two underside reservoirs and hold the board flat against the lands while curing. Keep adhesive out of the spring channels. Verify that all nine fingers are exposed.
4. Fit the lid with its pockets toward the components. Use **0.025 mm** bond film on the mating perimeter. Keep the seam flush. Check that the lid stays flat over U1 under light pressure and that the carrier cannot separate during removal.
5. Inspect the finished card. Target 24.00 and 32.00 mm within ±0.05 mm, and 2.10 mm within ±0.04 mm. From the gold datum the tray floor reaches −0.55 mm, lid exterior +1.55 mm and U1 pocket roof +1.45 mm. Hold the assembled roof within ±0.02 mm and measure the populated height before bonding. With a 0.44 mm finished PCB, 0.90 mm IC, 0.06 mm solder stand-off and 0.01 mm seating allowance, the limiting roof clearance is **0.02 mm**. Reject interference, warping, contamination or any protruding adhesive. Repeat the gauge checks with the actual bonded assembly.

The parametric carrier source reads the KiCad placement CSV. Run `python mechanical/carrier.py` with CadQuery 2.8 to regenerate the mechanical solids after placement changes. Use KiCad's STEP export with user origin **100 × 100 mm** to place the populated PCB into the shell's coordinate system. Align the lowest gold surface to Z = 0.

## Programming and checkout

Use the **Pico** firmware target. GP25 drives the active-high green LED. GP0 carries the 115200 baud UART log. The existing design uses GP2–4 for the one-bit SD interface. [Prototype and firmware](../../docs/sdbridge.md) · [Raspberry Pi RP2040 hardware design guide](https://datasheets.raspberrypi.com/rp2040/hardware_design_with_rp2040.pdf)

| Pad | TP1 | TP2 | TP3 | TP4 | TP5 | TP6 | TP7 |
|---|---|---|---|---|---|---|---|
| Signal | GND | 3.3 V | SWDIO | SWCLK | RUN | BOOTSEL | GP0 TX |

1. On the bench, outside the cage, power TP2 from a regulated current-limited 3.3 V supply with return at TP1. Verify the core regulator comes up and confirm SWD identification. BOOTSEL connects to flash CS through R8. For USB boot, ground TP6, pulse TP5 low and release reset, then release TP6. A bench USB fixture connects PC D+, D− and GND to fingers 8, 9 and 3/6. Keep PC VBUS isolated from the card. Copy `sdbridge/out/pico/SDLINK.UF2` to the boot volume. Building SDLINK requires the existing build's `AA_CERT` and `AA_KEY` inputs.
2. Disconnect the bench supply before seating the card in the powered installation. On the unit, test cold power-up with the card latched and insertion after startup. Measure slot 3.3 V and card current during flash boot, enumeration and sustained transfer. Capture the GP0 log on the bench or an instrumented open fixture. Confirm the first SD negotiation completes from slot power.
3. Verify a complete read and content check of `LINKTEST.BIN`. Connect the phone, confirm USB full-speed enumeration and the Android Auto handshake, and exercise simultaneous USB video reception and SD reads. Repeat after a phone disconnect and a head-unit power cycle.
4. This delivery contains card hardware only. For a head-unit hardware run, use a verified image with responsive physical display and disc-eject handling during reads and error screens. In the SDK, `panel_service()` polls the faceplate. `KEY_DISPLAY` calls `display_toggle()`. The separate `KEY_CD_EJECT` calls `cd_eject()`, which issues ATAPI ALLOW MEDIUM REMOVAL then START STOP UNIT with LoEj set. Verify screen opening and actual disc expulsion with the bridge installed. Keep stock updater handoffs out of the test. [Faceplate and ATAPI path](../../sdk/src/cd.c) · [Display motor control](../../sdk/src/display.c)

## Verification record

KiCad 10.0.8 ERC and DRC passed with zero warnings or errors, zero unconnected pads and zero schematic parity issues. The exported B.Mask contains nine finger openings. All 44 finished drill holes clear the nine gold wipe surfaces. The placement file and BOM cover the same 29 populated designators. The existing Pico SDLINK UF2 targets RP2040 flash and fits within the 2 MiB device. The nominal populated STEP model measured 1.33 mm above its lowest gold surface. A solid intersection check found zero overlap with either shell half. Physical cage fit, screen travel, contact reliability, slot supply margin, USB signal quality and operation of this board revision remain bench and hardware tests.
