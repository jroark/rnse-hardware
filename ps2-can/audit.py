"""Validate schematic/PCB pin nets and record actual routed widths (KiCad Python)."""
import pcbnew as p, pathlib, xml.etree.ElementTree as ET, json,collections
D=pathlib.Path(__file__).resolve().parent
b=p.LoadBoard(str(D/'ps2-can.kicad_pcb'))
x=ET.parse(D/'reports/schematic.xml')
expected={(n.attrib['ref'],n.attrib['pin']):net.attrib['name'] for net in x.findall('.//nets/net') for n in net.findall('node') if not n.attrib['ref'].startswith('#')}
actual={(f.GetReference(),pad.GetNumber()):pad.GetNetname() for f in b.GetFootprints() for pad in f.Pads() if pad.GetNumber()}
errors=[(key,net,actual.get(key)) for key,net in expected.items() if actual.get(key)!=net]
assert not errors,errors
widths=collections.defaultdict(list)
for t in b.GetTracks():
 if not isinstance(t,p.PCB_VIA):widths[t.GetNetname()].append(p.ToMM(t.GetWidth()))
report={'schematic_pad_nets_checked':len(expected),'mismatches':errors,'board_mm':[65,45], 'minimum_copper_track_width_mm':min(w for ws in widths.values() for w in ws),'routed_widths_mm':{n:sorted(set(round(w,4) for w in ws)) for n,ws in sorted(widths.items())}}
(D/'reports/connectivity-and-widths.json').write_text(json.dumps(report,indent=2))
print('Verified',len(expected),'pin/net assignments; minimum track width',report['minimum_copper_track_width_mm'])
