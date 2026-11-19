"""Place reference and connector legends in free silkscreen space."""
import pcbnew as p,pathlib,json,math
D=pathlib.Path(__file__).resolve().parent
project=(D/'ps2-can.kicad_pro').read_text();b=p.LoadBoard(str(D/'ps2-can.kicad_pcb'))
def box(item):
 r=item.GetBoundingBox();return tuple(p.ToMM(v) for v in [r.GetLeft(),r.GetTop(),r.GetRight(),r.GetBottom()])
def hit(a,c,g=.22):return a[0]<c[2]+g and a[2]>c[0]-g and a[1]<c[3]+g and a[3]>c[1]-g
occupied=[]
for fp in b.GetFootprints():
 for pad in fp.Pads():occupied.append(box(pad))
 for g in fp.GraphicalItems():
  if g.GetLayer()==p.F_SilkS:occupied.append(box(g))
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):occupied.append(box(t))
for t in b.GetDrawings():
 if t.GetLayer()==p.F_SilkS:occupied.append(box(t))
for fp in sorted(b.GetFootprints(),key=lambda f:f.GetReference()):
 if fp.GetReference().startswith('H'):continue
 t=fp.Reference();origin=fp.GetPosition();tx=p.ToMM(origin.x);ty=p.ToMM(origin.y)
 t.SetTextSize(p.VECTOR2I(p.FromMM(.8),p.FromMM(.8)));t.SetTextThickness(p.FromMM(.12));t.SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T));t.SetLayer(p.F_SilkS)
 options=sorted([(dx*.5,dy*.5) for dx in range(-10,11) for dy in range(-10,11)],key=lambda v:v[0]**2+v[1]**2)
 placed=False
 for dx,dy in options:
  t.SetPosition(p.VECTOR2I(p.FromMM(tx+dx),p.FromMM(ty+dy)));candidate=box(t)
  if candidate[0]<100.6 or candidate[2]>164.4 or candidate[1]<100.6 or candidate[3]>144.4:continue
  if any(hit(candidate,o) for o in occupied):continue
  occupied.append(candidate);placed=True;break
 if not placed:t.SetLayer(p.F_Fab);t.SetPosition(origin)
 t.SetVisible(True)
# Back-side permanent wiring legend (no bottom components).
for msg,x,y in [('RNS-E PS/2 CAN rev A',132,107),('J1: 1=+12V 2=GND 3=CANH 4=CANL',132,120),('J4: 1=5V 2=UPDI 3=GND',132,123),('100k FT-CAN / TJA1055',132,116)]:
 t=p.PCB_TEXT(b);t.SetText(msg);t.SetLayer(p.B_SilkS);t.SetMirrored(True);t.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)));t.SetTextSize(p.VECTOR2I(p.FromMM(.8),p.FromMM(.8)));t.SetTextThickness(p.FromMM(.12));b.Add(t)
p.SaveBoard(str(D/'ps2-can.kicad_pcb'),b);(D/'ps2-can.kicad_pro').write_text(project)
