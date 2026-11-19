"""Build the Rev A carrier, pocketed lid and solid fit gauge using CadQuery 2.8.

Run after exporting placement.csv. Dimensions are mm. The origin is at card
centre, on the gold face. Viewed from above the ICs, insertion is along +Y.
"""
import csv
from pathlib import Path
import cadquery as cq

OUT = Path(__file__).resolve().parent
PCB = [(-10.75,15.35),(7.53,15.35),(10.75,12.13),(10.75,-15.25),(-10.75,-15.25)]
# Nominal assembly Z datums, including the perimeter adhesive.
BASE, SHOULDER, SEAM, LID_BASE, TOP = -.55, .23, .58, .605, 1.55

def profile(z, height):
    # R1 rear and leading left corners, R0.5 tangencies along keyed nose.
    w = cq.Workplane("XY", origin=(0,0,z)).moveTo(-11,-16).lineTo(11,-16)
    w = w.threePointArc((11.707107,-15.707107),(12,-15)).lineTo(12,4.5)
    w = w.lineTo(11.25,4.5).lineTo(11.25,6).lineTo(12,6).lineTo(12,11.792893)
    w = w.threePointArc((11.96194,11.984235),(11.853553,12.146447))
    w = w.lineTo(8.146447,15.853553).threePointArc((7.984235,15.96194),(7.792893,16))
    w = w.lineTo(-11,16).threePointArc((-11.707107,15.707107),(-12,15))
    # Fixed write-enable slider profile.
    w = w.lineTo(-12,5.05).lineTo(-11.25,5.05).lineTo(-11.25,1.5).lineTo(-12,1.5)
    return w.lineTo(-12,-15).threePointArc((-11.707107,-15.707107),(-11,-16)).close().extrude(height)

def box(x, y, z, dx, dy, dz):
    return cq.Workplane("XY", origin=(x,y,z)).box(dx,dy,dz,centered=(True,True,False))

def prism(points, z, h, allowance=0):
    w = cq.Workplane("XY", origin=(0,0,z)).polyline(points).close()
    if allowance:
        w = w.offset2D(allowance, kind="intersection")
    return w.extrude(h)

def lower_envelope():
    body = profile(BASE, SHOULDER-BASE).intersect(box(0,0,BASE,22,33,1))
    # Open-ended channels permit spring travel. A common channel serves
    # contacts 7 and 8, whose centre spacing is smaller than the other fingers.
    for x,width,back in [(x,1.95,9.7) for x in [6.875,4.375,1.875,-.625,-3.125,-5.625]] + [
            (-8.9,3.25,9.7),(9.375,1.95,7.65)]:
        body = body.cut(box(x,(18+back)/2,BASE-.01,width,18-back,-BASE+.01))
    return body.union(profile(SHOULDER,SEAM-SHOULDER))

def make_parts():
    outer = lower_envelope()
    tray = outer.cut(prism(PCB,0,2,.10))
    # Shallow adhesive reservoirs leave broad, hard seats at z=0.
    for x in (-6,6):
        tray = tray.cut(box(x,-8,-.06,4,7,.08))
    lid = profile(LID_BASE,TOP-LID_BASE)
    # Generate underside pockets from actual placement. Leave solid webs
    # between component groups to support the thin roof over the QFN.
    bodies = {"U1":(7,7,1.45),"U2":(3,2,1.23),"Y1":(3.2,2.5,1.45),
              "D1":(1.0,.5,1.30),"C":(1,.5,1.18),"R":(1,.5,1.12)}
    with (OUT.parent/"manufacturing"/"placement.csv").open() as f:
        for row in csv.DictReader(f):
            ref = row["Ref"]
            dx,dy,roof = bodies[ref if ref in bodies else ref[0]]
            angle = float(row["Rot"])
            x,y = float(row["PosX"])-100, float(row["PosY"])+100
            tool = box(0,0,LID_BASE-.01,dx+.90,dy+.90,roof-LID_BASE+.01)
            lid = lid.cut(tool.rotate((0,0,0),(0,0,1),angle).translate((x,y,0)))
    gauge = outer.union(profile(SEAM,TOP-SEAM))
    return tray,lid,gauge

if __name__ == "__main__":
    tray,lid,gauge = make_parts()
    for name,part in [("tray",tray),("lid",lid),("fit-gauge",gauge)]:
        assert len(part.solids().vals()) == 1 and part.val().isValid()
        cq.exporters.export(part,str(OUT/(name+".stl")),tolerance=.012,angularTolerance=.08)
    assembly = cq.Assembly(name="SD_carrier")
    assembly.add(tray,name="Tray",color=cq.Color(.17,.20,.22))
    assembly.add(lid,name="Lid",color=cq.Color(.75,.80,.82,.65))
    assembly.export(str(OUT/"carrier.step"))
