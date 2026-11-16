import pathlib,pcbnew as p
D=pathlib.Path(__file__).resolve().parent
b=p.LoadBoard(str(D/'nes-can.kicad_pcb'))
for t in b.GetDrawings():
 if isinstance(t,p.PCB_TEXT) and t.GetText().startswith('NES PLAYER'):
  t.SetPosition(p.VECTOR2I(t.GetPosition().x,p.FromMM(100.8)))
p.SaveBoard(str(D/'nes-can.kicad_pcb'),b)
