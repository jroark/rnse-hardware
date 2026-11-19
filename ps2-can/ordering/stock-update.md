# Stock update from myLists.xlsx

Use these two **headerless** files for the revised one-board order:

| Distributor | File | Order lines | Pieces |
|---|---|---:|---:|
| DigiKey | [digikey-order-now.csv](digikey-order-now.csv) | 21 | 45 |
| Mouser | [mouser-order-now.csv](mouser-order-now.csv) | 2 | 3 |
| Combined | | 23 | 48 |

Start a fresh list when importing these complete files. Map columns **1 = distributor
part number, 2 = quantity, 3 = customer reference**. There is no header to skip:
the first row is a real component. Choose cut tape or individual units.

If preserving the existing DigiKey list instead, remove the erroneous **Part Number**
entry and the **five unavailable lines** below. Add the two lines in
[digikey-replacements-only.csv](digikey-replacements-only.csv), then order the
three pieces in the Mouser file separately. Do not also import the complete
DigiKey file into that existing list, which would duplicate parts.

## Five unavailable lines and their resolution

| References | Required qty | Original MPN | Revised sourcing |
|---|---:|---|---|
| C5 | 1 | GRM21BR61H106KE43L | Same part from Mouser, **81-GRM21BR61H106KE3L**. |
| C6 | 1 | GRM21BR61C106KE15L | Use a second **GRM21BR61H106KE43L** from Mouser: same 10 uF / X5R / 0805; voltage rating increases from 16 V to 50 V. |
| D5-D8 | 4 | PESD5V0S1BA,115 | MCC **ESD5V0D3B-TP**, DigiKey **ESD5V0D3B-TPMSCT-ND**. |
| R1-R4 | 4 | RC0805FR-07100RL | YAGEO **RC0805FR-07100RP**, DigiKey **YAG1318CT-ND**. |
| U3 | 1 | TJA1055T/2Z | Same specified part from Mouser, **771-TJA1055T/2Z**. |

Mouser combines C5 and C6 into a single line with quantity **2**. The other line
is U3, quantity **1**. Test pads, mounting holes and additional spares are excluded.
The source workbook is unchanged. Design MPNs remain recorded in the base BOM;
these files are an explicitly documented purchasing variant.

## Compatibility checks

- **C5/C6:** retain 10 uF and X5R in the same 2.0 × 1.25 mm 0805 case. C5 keeps
  its original 50 V part; C6 can use the same part on its 5 V rail. The regulator
  does not require an external output capacitor for stability. No PCB changes.
- **R1-R4:** retain 100 ohm, 1%, 0.125 W and 0805. The RC_P variant changes the
  termination composition; dimensions and electrical requirements match.
- **D5-D8:** MCC's manufacturer datasheet specifies bidirectional 5 V standoff,
  SOD-323, IEC 61000-4-2 ESD ratings of ±25 kV air/contact, and 50 pF maximum
  capacitance. Its lead span is 2.30-2.70 mm with 0.25-0.40 mm lead width. The board's
  standard SOD-323 land pattern has 0.60 x 0.45 mm pads at 2.10 mm centers
  (2.70 mm outer copper span), compatible with this package. MCC's suggested
  land pattern is different; it is not an exact match to that recommendation. This is a functional ESD alternate, not an identical
  surge specification: MCC specifies **15 V clamping at 8 A (8/20 us)**; the
  original Nexperia part specifies 14 V at 12 A. Use the manufacturer datasheet,
  not DigiKey's conflicting 13.5 V/500 W summary fields. The board is an untested
  prototype and no system ESD certification is implied.
- **U3:** retain TJA1055T/2Z, the 5 V fault-tolerant CAN transceiver in SO14.
  No substitution to a high-speed transceiver or a `/3` variant is included.
- **J2/J3:** the existing MD-60S date-code requirement remains: after 2022-03-03.

## Availability evidence

Checked 2026-11-15. The original unavailable items and the other unchanged stock
lines come from the user's DigiKey export. Replacement/source listings showed:

| Selected item | Supplier | Stock shown | Link |
|---|---|---:|---|
| RC0805FR-07100RP | DigiKey | 12,150 | [Product](https://www.digikey.com/en/products/detail/yageo/RC0805FR-07100RP/4935333) |
| ESD5V0D3B-TP | DigiKey | 57,285 | [Product](https://www.digikey.com/en/products/detail/mcc-micro-commercial-components/ESD5V0D3B-TP/2213549) |
| GRM21BR61H106KE43L | Mouser | 2,639 | [Product](https://www.mouser.com/en/ProductDetail/Murata-Electronics/GRM21BR61H106KE43L?qs=lYGu3FyN48cBZlIduWKclg%3D%3D) |
| TJA1055T/2Z | Mouser | 2,263 | [Product](https://www.mouser.com/en/ProductDetail/NXP-Semiconductors/TJA1055T-2Z?qs=qSfuJ%252Bfl%2Fd47IrA1fhktNg%3D%3D) |

These are retrieved listing snapshots, not stock reservations. Some search
snippets showed older stock than the opened product pages; selections use the
opened pages. Confirm availability in the newly imported lists before checkout.
The Samsung 50 V capacitor and Diodes DESD5V0S1BA-7 alternatives were rejected
because their opened DigiKey pages showed zero stock.

Manufacturer references:
[MCC ESD5V0D3B datasheet](https://www.mccsemi.com/pdf/Products/ESD5V0D3B%28SOD-323%29.pdf),
[Nexperia original ESD datasheet](https://assets.nexperia.com/documents/data-sheet/PESD5V0S1BA.pdf),
[TRACO TSR 1 datasheet](https://www.tracopower.com/sites/default/files/products/datasheets/tsr1_datasheet.pdf),
[Murata capacitor specification](https://www.mouser.com/datasheet/2/281/1/GRM21BR61H106KE43_01A-1986884.pdf).

The exported audit identifies the input workbook by its SHA-256. The source
mapping and export generator check that every populated reference is covered
exactly once and that the combined quantity remains 48.
