#!/bin/sh
# Makes the PCB order: manufacturing/sdbridge-card-revB.zip, with the
# Gerbers, drill file and layer job exported from sdbridge-card.kicad_pcb
# by KiCad's command-line tool, and manufacturing/fabrication.txt.  The
# ZIP is generated, never committed.
#
#   sh sdbridge-card/fab.sh        (KiCad 10; KICAD_CLI=path to override)
set -e
here=$(cd "$(dirname "$0")" && pwd)
cli=${KICAD_CLI:-$(command -v kicad-cli || echo /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli)}
[ -x "$cli" ] || { echo "fab.sh: kicad-cli not found (install KiCad 10 or set KICAD_CLI)" >&2; exit 1; }
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
"$cli" pcb export gerbers --no-protel-ext \
    --layers F.Cu,B.Cu,F.Mask,B.Mask,F.Paste,F.Silkscreen,Edge.Cuts \
    -o "$out/" "$here/sdbridge-card.kicad_pcb" >/dev/null
"$cli" pcb export drill -o "$out/" "$here/sdbridge-card.kicad_pcb" >/dev/null
cp "$here/manufacturing/fabrication.txt" "$out/"
zip="$here/manufacturing/sdbridge-card-revB.zip"
rm -f "$zip"
(cd "$out" && zip -q -X "$zip" sdbridge-card-*.gbr sdbridge-card-job.gbrjob sdbridge-card.drl fabrication.txt)
echo "$zip"
