#!/usr/bin/env python3
"""Package the NES-to-CAN adapter: its firmware and its design.

    python3 hardware/nes-can/package.py     (after `make -C firmware`)

Writes hardware/nes-can/out/nes-can-release/: nes-can.hex (the
ATtiny1616's firmware, firmware/build/), nes-can-hardware.zip (the KiCad
project, its generator and checks, Gerbers and BOM) and SHA256SUMS.  The
NES payloads that talk to it are packaged by the port's nes/package.py
(rnse-ports).
"""
from pathlib import Path
import hashlib
import shutil
import zipfile

HERE = Path(__file__).resolve().parent          # hardware/nes-can
OUT = HERE / 'out/nes-can-release'
OUT.mkdir(parents=True, exist_ok=True)
shutil.copy2(HERE / 'firmware/build/nes-can.hex', OUT / 'nes-can.hex')


def include(path):
    return (path.is_file() and not set(path.parts) & {'__pycache__', 'build', 'out'}
            and path.name != 'placement.kicad_pcb'
            and path.suffix not in ('.kicad_prl', '.lck'))


with zipfile.ZipFile(OUT / 'nes-can-hardware.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(HERE.rglob('*')):
        if include(path):
            archive.write(path, path.relative_to(HERE.parent))

files = sorted(path for path in OUT.iterdir() if path.is_file() and path.name != 'SHA256SUMS')
(OUT / 'SHA256SUMS').write_text(''.join(
    hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + path.name + '\n'
    for path in files))
print(OUT)
