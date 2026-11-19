# Order parts for one RNS-E PS/2-CAN board

**Stock update:** use [the revised sourcing plan](stock-update.md) based on
`myLists.xlsx`. It supplies headerless DigiKey and Mouser files, resolves all
five unavailable lines, and excludes the accidentally imported header row.
The original files described below remain the design-MPN baseline.

**24 order lines / 48 physical components / one PCB / no extra spares.**
These are distributor upload files, not submitted carts or orders.

## Upload

- **DigiKey:** open [My Lists](https://www.digikey.com/en/mylists/), choose Upload a List,
  and upload `digikey-1-board.csv`. Map **Part Number**, **Quantity** and
  **Customer Reference**. Part numbers are DigiKey cut-tape SKUs where available;
  the through-hole parts and tube IC use their bulk/tube SKUs. Review matching and
  stock, then add the list to your cart. Avoid Digi-Reel fees for this build.
- **Mouser:** open the [BOM Tool](https://www.mouser.com/bomtool/) and upload
  `mouser-1-board.csv`. Map **Manufacturer Part Number**, **Manufacturer**,
  **Quantity** and **Reference Designator**. These are manufacturer part numbers,
  not guessed Mouser stock numbers. Confirm the returned manufacturer/package
  matches, choose cut tape or individual units, then add to your cart.
- `bom-ordering-detail.csv` includes both supplier links, quantities, references,
  footprints and purchasing notes. The quick-paste text files contain tab-separated
  part number and quantity columns without a header. Prefer CSV upload, especially
  for the Nexperia SKU whose name contains a literal comma.

The manufacturer quantities are per component, not reels. If your import shows a
minimum order of hundreds/thousands, select cut tape instead of a full reel.
Keep MPN columns as text if opening the files in Excel; preserve leading zeros in
`0466.500NR`, slashes, and the comma in `PESD5V0S1BA,115`.

## Corrections made while checking parts against the board

| Reference | Correct order part | Reason |
|---|---|---|
| F1 | Littelfuse **0466.500NR** | The old 0467.500NRHF is 0603. The board requires 1206; the corrected part is 500 mA / 63 V. |
| Y1 | Abracon **ABL-16.000MHZ-B2** | The old ABLS-16.000MHZ-B2-T is surface mount. The board requires through-hole HC-49/US, 16 MHz, 18 pF. |
| D1 | Vishay **SS16-E3/61T** | Orderable replacement for the original Diodes SS16-13-F; same required SMA package, 60 V / 1 A Schottky rating and cathode pad 1. |

These changes are reflected in `../bom.csv`, `../connectivity.json` and the
source generator. They require **no copper, footprint or electrical-value changes**.
Schematic values remain 0.5 A / 63 V, 16 MHz / 18 pF and SS16, respectively.

Verification references:
[old F1 package](https://www.digikey.com/en/products/detail/littelfuse-inc/0467-500NRHF/2023643),
[correct F1](https://www.digikey.com/en/products/detail/littelfuse-inc/0466-500NR/521335),
[old Y1 package](https://www.digikey.com/en/products/detail/abracon-llc/ABLS-16-000MHZ-B2-T/675266),
[correct Y1](https://www.digikey.com/en/products/detail/abracon-llc/ABL-16-000MHZ-B2/675236),
[Vishay SS16 datasheet](https://www.vishay.com/docs/88746/ss12.pdf).

## Availability and fit notes

Listings retrieved on **2026-11-15** are sourcing guidance, not a live stock
reservation or quote. Pricing and lead times are intentionally left to the
supplier import tool; there is no claim that every line is immediately available.

- **U3 TJA1055T/2Z:** [DigiKey](https://www.digikey.com/en/products/detail/nxp-usa-inc/TJA1055T-2Z/10815724)
  showed zero stock; [Mouser 771-TJA1055T/2Z](https://www.mouser.com/en/ProductDetail/NXP-Semiconductors/TJA1055T-2Z?qs=qSfuJ%252Bfl%2Fd47IrA1fhktNg%3D%3D)
  showed 2,263 units. The full BOM is supplied for both distributors so you can
  compare availability before ordering.
- **D5-D8 PESD5V0S1BA,115** and **C6 GRM21BR61C106KE15L:** DigiKey listings
  showed backorder. Check Mouser's matches before checkout. No unreviewed
  automatic substitute is included in either order file.
- **J2/J3 MD-60S:** request date code **after 2022-03-03**. The manufacturer kept
  the same MPN while changing the PCB layout. A successful BOM match does not
  guarantee that an old-stock socket fits; compare the supplied connector with
  the [current drawing, page 3](https://www.sameskydevices.com/product/resource/md-s.pdf).
- **U1:** SOIC-20 wide body, not VQFN. **U2:** SOIC-18 wide body, not DIP or TSSOP.
  **U3:** TJA1055T/2Z as specified; do not substitute a high-speed CAN transceiver
  or a `/3` logic-interface variant automatically.

No purchase is required for TP1-TP4 (bare plated holes) or H1-H4 (mounting holes).
The PCB, optional M2 hardware, cables, PS/2 peripherals and 5 V UPDI programmer
are excluded. No socket is needed for the SOIC chips.

## Validation

The export groups the original reference designators by exact MPN, excludes TP
rows, checks for duplicated references, and round-trips both CSVs. Expected totals
are 24 lines, 48 components, and exactly one occurrence of every populated
reference. `build_order_files.py` reproduces the files from `../bom.csv`.
