#!/usr/bin/env python3
"""Generate the editable KiCad design from one connectivity/placement source.
Run with KiCad's bundled Python (pcbnew). Route with Freerouting separately.
"""
import pcbnew as p, pathlib, uuid, json, csv, math
D=pathlib.Path(__file__).resolve().parent
LIB=pathlib.Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')
def uid(): return str(uuid.uuid4())
def q(s): return json.dumps(str(s))
parts=[]
root=uid()
def add(ref,val,fp,nets,xy,rot=0,names=None,mpn='',note=''):
    parts.append(dict(ref=ref,val=val,fp=fp,nets={str(k):v for k,v in nets.items()},xy=xy,rot=rot,names=names or {},mpn=mpn,note=note,id=uid()))
RFP='Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder'
CFP='Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder'
def r(n,val,a,b,x,y,rot=0): add('R'+str(n),val,RFP,{1:a,2:b},(x,y),rot,mpn={'4.7k':'RC0805FR-074K7L','10k':'RC0805FR-0710KL','100':'RC0805FR-07100RL','5.6k':'RC0805FR-075K6L','1k':'RC0805FR-071KL'}.get(val,''))
def c(n,val,a,b,x,y,rot=0): add('C'+str(n),val,CFP,{1:a,2:b},(x,y),rot,mpn={'100n':'C0805C104K5RACTU','27p':'C0805C270J5GACTU','10u/50V':'GRM21BR61H106KE43L','10u/16V':'GRM21BR61C106KE15L'}.get(val,''))
add('J1','VEHICLE','TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-4-5.08_1x04_P5.08mm_Horizontal',{1:'12V_SW',2:'GND',3:'CANH',4:'CANL'},(109.5,139),0,{1:'+12V switched',2:'GND',3:'CANH',4:'CANL'},'1715048')
for i,x in [(2,113),(3,130)]:
    pre='K' if i==2 else 'M'
    add('J'+str(i),'KEYBOARD' if i==2 else 'MOUSE','ps2-can:MD-60S_2022',{1:pre+'_DATA_EXT',2:None,3:'GND',4:pre+'_5V',5:pre+'_CLK_EXT',6:None},(x,101),0,{1:'DATA',2:'NC',3:'GND',4:'+5V',5:'CLOCK',6:'NC'},'MD-60S','Use date code after 2022-03-03')
add('J4','UPDI','Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical',{1:'5V',2:'UPDI',3:'GND'},(160,119),0,{1:'VTREF 5V',2:'UPDI',3:'GND'},'61300311121')
add('U1','ATtiny1616-SNR','Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm',{1:'5V',2:'CS_N',3:'CAN_INT_N',4:'K_CLK',5:'K_DATA',6:'M_CLK',7:'M_DATA',8:'CAN_EN',9:'CAN_STB',10:'CAN_ERR_N',11:'ACT_LED',12:None,13:None,14:None,15:None,16:'UPDI',17:'MOSI',18:'MISO',19:'SCK',20:'GND'},(113,124),0,dict(enumerate(['VDD','PA4 / SS','PA5','PA6','PA7','PB5','PB4','PB3','PB2','PB1','PB0','PC0','PC1','PC2','PC3','PA0 / UPDI','PA1 / MOSI','PA2 / MISO','PA3 / SCK','GND'],1)),'ATTINY1616-SNR')
add('U2','MCP2515-I/SO','Package_SO:SOIC-18W_7.5x11.6mm_P1.27mm',{1:'CAN_TX',2:'CAN_RX',3:None,4:'5V',5:'5V',6:'5V',7:'OSC2',8:'OSC1',9:'GND',10:None,11:None,12:'CAN_INT_N',13:'SCK',14:'MOSI',15:'MISO',16:'CS_N',17:'CAN_RESET_N',18:'5V'},(132,124),0,dict(enumerate(['TXCAN','RXCAN','CLKOUT','TX0RTS_N','TX1RTS_N','TX2RTS_N','OSC2','OSC1','VSS','RX1BF_N','RX0BF_N','INT_N','SCK','SI','SO','CS_N','RESET_N','VDD'],1)),'MCP2515-I/SO')
add('U3','TJA1055T/2Z','Package_SO:SOIC-14_3.9x8.7mm_P1.27mm',{1:None,2:'CAN_TX',3:'CAN_RX',4:'CAN_ERR_N',5:'CAN_STB',6:'CAN_EN',7:'WAKE_N',8:'RTH',9:'RTL',10:'5V',11:'CANH',12:'CANL',13:'GND',14:'VBAT'},(150,133),0,dict(enumerate(['INH','TXD','RXD','ERR_N','STB','EN','WAKE_N','RTH','RTL','VCC','CANH','CANL','GND','BAT'],1)),'TJA1055T/2Z')
add('U4','TSR 1-2450','Converter_DCDC:Converter_DCDC_TRACO_TSR-1_THT',{1:'VBAT',2:'GND',3:'5V'},(150,106),0,{1:'VIN',2:'GND',3:'+5V'},'TSR 1-2450')
add('F1','0.5A / 63V','Fuse:Fuse_1206_3216Metric_Pad1.42x1.75mm_HandSolder',{1:'12V_SW',2:'12V_FUSED'},(143,141),0,mpn='0466.500NR')
add('D1','SS16','Diode_SMD:D_SMA',{1:'VBAT',2:'12V_FUSED'},(151,141),0,{1:'K',2:'A'},'SS16-E3/61T')
add('D2','SMBJ18A','Diode_SMD:D_SMB',{1:'VBAT',2:'GND'},(159,141),0,{1:'K',2:'A'},'SMBJ18A')
for n,pre,x in [(2,'K',105),(3,'M',135)]:
    add('F'+str(n),'PTC 0.20A','Fuse:Fuse_1812_4532Metric',{1:'5V',2:pre+'_5V'},(x,113),0,mpn='1812L020/60DR')
for n,pre,x in [(1,'K',104),(3,'M',135)]:
    r(n,'100',pre+'_DATA_EXT',pre+'_DATA',x,116)
    r(n+1,'100',pre+'_CLK_EXT',pre+'_CLK',x,119)
for n,net,x,y in [(5,'K_DATA',104,122),(6,'K_CLK',104,125),(7,'M_DATA',139,116),(8,'M_CLK',139,119)]: r(n,'4.7k','5V',net,x,y,90)
r(9,'10k','5V','CS_N',120,115)
r(10,'10k','5V','CAN_RESET_N',139,122)
r(11,'10k','CAN_EN','GND',143,125)
r(12,'10k','CAN_STB','GND',143,128)
r(13,'5.6k','RTH','CANH',150,126)
r(14,'5.6k','RTL','CANL',157,128)
r(15,'10k','VBAT','WAKE_N',157,132)
r(16,'10k','5V','CAN_TX',122,134)
r(17,'1k','5V','PWR_LED',155,116)
r(18,'1k','ACT_LED','ACT_ANODE',120,137)
add('D3','POWER green','LED_SMD:LED_0805_2012Metric_Pad1.15x1.40mm_HandSolder',{1:'GND',2:'PWR_LED'},(155,119),0,{1:'K',2:'A'},'LTST-C170KGKT')
add('D4','ACT amber','LED_SMD:LED_0805_2012Metric_Pad1.15x1.40mm_HandSolder',{1:'GND',2:'ACT_ANODE'},(125,137),0,{1:'K',2:'A'},'LTST-C170KFKT')
# Individual bidirectional TVS: symmetric K1/K2 terminals.
for n,net,x,y in [(5,'K_DATA_EXT',105,107),(6,'K_CLK_EXT',117,107),(7,'M_DATA_EXT',124,107),(8,'M_CLK_EXT',136,107)]:
    add('D'+str(n),'PESD5V0S1BA','Diode_SMD:D_SOD-323',{1:net,2:'GND'},(x,y),90,{1:'K1',2:'K2'},'PESD5V0S1BA,115')
c(1,'100n','5V','GND',119,119,90)
c(2,'100n','5V','GND',138,127,90)
c(3,'100n','5V','GND',155,125)
c(4,'100n','VBAT','GND',160,135,90)
c(5,'10u/50V','VBAT','GND',143,106,90)
c(6,'10u/16V','5V','GND',157,107,90)
c(7,'100n','K_5V','GND',107,110)
c(8,'100n','M_5V','GND',132,110)
add('Y1','16MHz CL18pF','Crystal:Crystal_HC49-4H_Vertical',{1:'OSC1',2:'OSC2'},(130,134),0,mpn='ABL-16.000MHZ-B2')
c(9,'27p','OSC1','GND',128,130,90)
c(10,'27p','OSC2','GND',136,132,90)
# custom connector origin at front lip; top-view PCB holes per current MD-S datasheet p3
mod=['(footprint "MD-60S_2022" (version 20241229) (generator "rnse") (layer "F.Cu") (attr through_hole)',
 '(fp_text reference "REF**" (at 0 13) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
 '(fp_text value "MD-60S_2022" (at 0 15) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))']
for layer,margin in [('F.SilkS',0),('F.CrtYd',0.5),('F.Fab',0)]:
    mod.append(f'(fp_rect (start {-7-margin} {-margin}) (end {7+margin} {12.4+margin}) (stroke (width 0.15) (type default)) (fill none) (layer "{layer}"))')
for num,x,y in [(1,1.3,8.5),(2,-1.3,8.5),(3,3.4,8.5),(4,-3.4,8.5),(5,3.4,11),(6,-3.4,11)]:
    mod.append(f'(pad "{num}" thru_hole circle (at {x} {y}) (size 1.7 1.7) (drill 1.0) (layers "*.Cu" "*.Mask"))')
mod.append('(pad "" np_thru_hole oval (at 0 4.7) (size 2.2 0.7) (drill oval 2.2 0.7) (layers "*.Cu" "*.Mask"))')
mod.append(')'); (D/'ps2-can.pretty/MD-60S_2022.kicad_mod').write_text('\n'.join(mod))
# copy every footprint locally, so project does not depend on global library setup
for a in parts:
    lib,name=a['fp'].split(':')
    if lib!='ps2-can':
        source=LIB/(lib+'.pretty')/(name+'.kicad_mod')
        if not source.exists(): raise RuntimeError(str(source))
        (D/'ps2-can.pretty'/source.name).write_text(source.read_text())
    a['fp']='ps2-can:'+name
(D/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "ps2-can")(type "KiCad")(uri "${KIPRJMOD}/ps2-can.pretty")(options "")(descr "Project-local footprints")))\n')
board=p.BOARD(); board.SetCopperLayerCount(2)
nets={}
for name in sorted({n for a in parts for n in a['nets'].values() if n}):
    net=p.NETINFO_ITEM(board,name);board.Add(net);nets[name]=net
for a in parts:
    fp=p.FootprintLoad(str(D/'ps2-can.pretty'),a['fp'].split(':')[1]);fp.SetReference(a['ref']);fp.SetValue(a['val']);fp.SetFPID(p.LIB_ID('ps2-can',a['fp'].split(':')[1]))
    fp.SetPath(p.KIID_PATH('/'+root+'/'+a['id']));board.Add(fp);fp.SetPosition(p.VECTOR2I(p.FromMM(a['xy'][0]),p.FromMM(a['xy'][1])));fp.SetOrientationDegrees(a['rot'])
    for pad in fp.Pads():
        net=a['nets'].get(pad.GetNumber())
        if net:pad.SetNet(nets[net])
    fp.Value().SetVisible(False)
    fp.Reference().SetTextSize(p.VECTOR2I(p.FromMM(.8),p.FromMM(.8)));fp.Reference().SetTextThickness(p.FromMM(.12))
    # references off component, editable
    fp.Reference().SetPosition(fp.GetPosition()+p.VECTOR2I(0,p.FromMM(-2)))
for x,y in [(102.8,103),(162,103),(102.8,142),(162,142)]:
    fp=p.FootprintLoad(str(LIB/'MountingHole.pretty'),'MountingHole_2.2mm_M2');board.Add(fp);fp.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)));fp.SetReference('H'+str(len([f for f in board.GetFootprints() if f.GetReference().startswith('H')])+1));fp.SetAttributes(p.FP_BOARD_ONLY | p.FP_EXCLUDE_FROM_BOM); fp.Reference().SetVisible(False);fp.Value().SetVisible(False)
for a,b in [((100,100),(165,100)),((165,100),(165,145)),((165,145),(100,145)),((100,145),(100,100))]:
    s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(p.VECTOR2I(p.FromMM(a[0]),p.FromMM(a[1])));s.SetEnd(p.VECTOR2I(p.FromMM(b[0]),p.FromMM(b[1])));s.SetLayer(p.Edge_Cuts);s.SetWidth(p.FromMM(.05));board.Add(s)
for text,x,y,size in [('PS/2 KEYBOARD',111,102,0.8),('PS/2 MOUSE',130,102,.8),('RNS-E PS2 / CAN  rev A',132,143,.9),('1:+12  2:GND  3:H  4:L',113,133,.7),('1:5V 2:UPDI 3:GND',157,114,.7)]:
    t=p.PCB_TEXT(board);t.SetText(text);t.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)));t.SetTextSize(p.VECTOR2I(p.FromMM(size),p.FromMM(size)));t.SetTextThickness(p.FromMM(.12));t.SetLayer(p.F_Fab if size<.8 or 'rev A' in text else p.F_SilkS);board.Add(t)
# test points use labeled through-hole pads, also useful for hand probing
for i,(net,x,y) in enumerate([('5V',145,116),('GND',145,119),('CAN_TX',141,133),('CAN_RX',141,136)],1):
    fp=p.FootprintLoad(str(LIB/'TestPoint.pretty'),'TestPoint_THTPad_D1.5mm_Drill0.7mm');board.Add(fp);fp.SetReference('TP'+str(i));fp.SetValue(net);fp.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)))
    for pad in fp.Pads():pad.SetNet(nets[net])
    fp.Value().SetVisible(False);fp.Reference().SetVisible(False)
    add('TP'+str(i),net,'TestPoint:TestPoint_THTPad_D1.5mm_Drill0.7mm',{1:net},(x,y),mpn='TEST PAD',note='Bare plated test pad; do not purchase')
    parts[-1]['fp']='ps2-can:TestPoint_THTPad_D1.5mm_Drill0.7mm'
    fp.SetPath(p.KIID_PATH('/'+root+'/'+parts[-1]['id']))
    (D/'ps2-can.pretty/TestPoint_THTPad_D1.5mm_Drill0.7mm.kicad_mod').write_text((LIB/'TestPoint.pretty/TestPoint_THTPad_D1.5mm_Drill0.7mm.kicad_mod').read_text())
# Pack small components around fixed mechanical/IC placements. All assembly on top.
def bounds(fp):
    shapes=[g.GetBoundingBox() for g in fp.GraphicalItems() if g.GetLayer()==p.F_CrtYd]
    if not shapes: shapes=[fp.GetBoundingBox(False,False)]
    return (min(p.ToMM(b.GetLeft()) for b in shapes),min(p.ToMM(b.GetTop()) for b in shapes),max(p.ToMM(b.GetRight()) for b in shapes),max(p.ToMM(b.GetBottom()) for b in shapes))
def overlap(a,b,gap=.18):return a[0]<b[2]+gap and a[2]>b[0]-gap and a[1]<b[3]+gap and a[3]>b[1]-gap
fixed={'U1','U2','U3','U4','J1','J2','J3','J4'}
occupied=[bounds(fp) for fp in board.GetFootprints() if fp.GetReference() in fixed or fp.GetReference().startswith('H')]
movable=[fp for fp in board.GetFootprints() if fp.GetReference() not in fixed and not fp.GetReference().startswith('H')]
movable.sort(key=lambda fp: -((bounds(fp)[2]-bounds(fp)[0])*(bounds(fp)[3]-bounds(fp)[1])))
for fp in movable:
    original=fp.GetPosition();tx=p.ToMM(original.x);ty=p.ToMM(original.y)
    best=None
    for angle in [0,90]:
        fp.SetOrientationDegrees(angle);fp.SetPosition(p.VECTOR2I(0,0));box=bounds(fp)
        for ix in range(203,328):
            x=ix*.5
            for iy in range(203,288):
                y=iy*.5;b=(box[0]+x,box[1]+y,box[2]+x,box[3]+y)
                if b[0]<101 or b[1]<101 or b[2]>164 or b[3]>144:continue
                if any(overlap(b,o) for o in occupied):continue
                score=(x-tx)**2+(y-ty)**2
                if best is None or score<best[0]:best=(score,x,y,angle,b)
    if best is None:raise RuntimeError('No legal placement for '+fp.GetReference())
    _,x,y,angle,b=best;fp.SetOrientationDegrees(angle);fp.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)));occupied.append(b)
    fp.Reference().SetVisible(False)
    for a in parts:
        if a['ref']==fp.GetReference():a['xy']=(x,y);a['rot']=angle
# put all component designators on fabrication layer; assembly drawing includes them
for fp in board.GetFootprints():
    fp.Reference().SetLayer(p.F_Fab);fp.Reference().SetVisible(True)
    fp.Reference().SetPosition(fp.GetPosition())
board.GetDesignSettings().m_CopperEdgeClearance=p.FromMM(.3)
p.SaveBoard(str(D/'ps2-can.kicad_pcb'),board)
p.ExportSpecctraDSN(board,str(D/'ps2-can.dsn'))
# Explicit manufacturing widths; pcbnew standalone export has no loaded netclasses.
dsn=(D/'ps2-can.dsn').read_text().replace('(width 200)', '(width 250)').replace('(clearance 50 (type smd_smd))','(clearance 200 (type smd_smd))')
(D/'ps2-can.dsn').write_text(dsn)
# generated block symbols: actual numbered pins, typed IC signals, explicit NCs
syms=[]; instances=[]
# group by functional section, positions independent of PCB
ordered=sorted(parts,key=lambda a: (0 if a['ref'] in ['J1','F1','D1','D2','U4','C5','C6'] else 1 if a['ref'] in ['U1','U2','U3','Y1','J4'] else 2,a['ref'][0],int(''.join(c for c in a['ref'] if c.isdigit()))))
for idx,a in enumerate(ordered):
    symname=a['ref']; count=len(a['nets']); left=(count+1)//2; h=max(5.08,(left+1)*2.54); width=10.16 if count>6 else 7.62
    pintext=[];positions=[]
    for k,num in enumerate(a['nets']):
        side=0 if k<left else 1; j=k if side==0 else k-left
        px=(-width-2.54) if side==0 else width+2.54;py=h/2-2.54*(j+1);ang=0 if side==0 else 180
        typ='passive'
        if a['ref']=='U1': typ='power_in' if num in ['1','20'] else 'bidirectional'
        if a['ref']=='U2': typ='power_in' if num in ['9','18'] else ('output' if num in ['1','3','10','11','12','15'] else 'input')
        if a['ref']=='U3': typ='power_in' if num in ['10','13','14'] else ('output' if num in ['1','3','4'] else 'input' if num in ['2','5','6','7'] else 'passive')
        if a['ref']=='U4':typ='power_out' if num=='3' else 'power_in'
        name=a['names'].get(int(num),a['names'].get(num,num))
        pintext.append(f'(pin {typ} line (at {px} {py} {ang}) (length 2.54) (name {q(name)} (effects (font (size 1 1)))) (number {q(num)} (effects (font (size 1 1)))))')
        positions.append((num,px,py,side))
    drawing=f'(rectangle (start {-width} {h/2}) (end {width} {-h/2}) (stroke (width 0.254)(type default)) (fill (type background)))'
    if count==2 and a['ref'][0] in 'RCFY':
        def line(x1,y1,x2,y2):return f'(polyline (pts (xy {x1} {y1})(xy {x2} {y2}))(stroke(width 0.254)(type default))(fill(type none)))'
        drawing=line(-width,0,-2.54,0)+line(2.54,0,width,0)
        if a['ref'][0]=='C':
            drawing=line(-width,0,-.635,0)+line(.635,0,width,0)+line(-.635,-2.54,-.635,2.54)+line(.635,-2.54,.635,2.54)
        else:
            drawing+='(rectangle(start -2.54 1.27)(end 2.54 -1.27)(stroke(width 0.254)(type default))(fill(type background)))'
            if a['ref'][0]=='F':drawing+=line(-2.54,0,2.54,0)
            if a['ref'][0]=='Y':drawing+=line(-3.175,-2.54,-3.175,2.54)+line(3.175,-2.54,3.175,2.54)
    definition=f'''(symbol "{symname}" (pin_names (offset 0.5) {"hide" if count==2 and a["ref"][0]!="D" else ""}) (in_bom yes) (on_board yes)
(property "Reference" "{a['ref']}" (at 0 {h/2+2} 0) (effects (font (size 1.27 1.27))))
(property "Value" {q(a['val'])} (at 0 {-h/2-2} 0) (effects (font (size 1.27 1.27))))
(symbol "{symname}_0_1" {drawing})
(symbol "{symname}_1_1" {''.join(pintext)}))'''
    syms.append(definition)
    x=35.56+(idx%8)*69.85;y=40.64+(idx//8)*45.72
    instances.append(f'''(symbol (lib_id "ps2-can:{symname}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{a['id']}")
(property "Reference" {q(a['ref'])} (at {x} {y-h/2-2} 0) (effects (font (size 1.27 1.27))))
(property "Value" {q(a['val'])} (at {x} {y+h/2+2} 0) (effects (font (size 1.27 1.27))))
(property "Footprint" {q(a['fp'])} (at {x} {y} 0) (effects (font (size 1 1)) hide))
(instances (project "ps2-can" (path "/{root}" (reference {q(a['ref'])}) (unit 1)))))''')
    for num,px,py,side in positions:
        X=x+px;Y=y-py;net=a['nets'][num]
        if net is None: instances.append(f'(no_connect (at {X} {Y}) (uuid "{uid()}"))');continue
        end=X+(-5.08 if side==0 else 5.08)
        instances.append(f'(wire (pts (xy {X} {Y}) (xy {end} {Y})) (stroke (width 0)(type default)) (uuid "{uid()}"))')
        instances.append(f'(label {q(net)} (at {end} {Y} 0) (effects (font (size 1 1)) (justify {"right" if side==0 else "left"} bottom)) (uuid "{uid()}"))')
# power flags for passive upstream power paths
for net,x in [('GND',35.56),('VBAT',105.41)]:
    name='FLAG_'+net
    syms.append(f'(symbol "{name}" (pin_names hide) (pin_numbers hide) (in_bom no)(on_board no)(property "Reference" "#FLG" (at 0 0 0)(effects(font(size 1 1)) hide))(property "Value" "PWR_FLAG" (at 0 2 0)(effects(font(size 1 1))))(symbol "{name}_1_1" (pin power_out line (at 0 0 90)(length 0)(name "pwr" (effects(font(size 1 1))))(number "1" (effects(font(size 1 1)))))))')
    instances.append(f'(symbol (lib_id "ps2-can:{name}")(at {x} 393.7 0)(unit 1)(in_bom no)(on_board no)(uuid "{uid()}")(property "Reference" "#FLG0{x}" (at {x} 393.7 0)(effects(font(size 1 1)) hide))(property "Value" "PWR_FLAG" (at {x} 390.525 0)(effects(font(size 1 1)) hide))(instances(project "ps2-can"(path "/{root}"(reference "#FLG0{x}")(unit 1)))))')
    instances.append(f'(label "{net}" (at {x} 393.7 0)(effects(font(size 1 1))(justify left bottom))(uuid "{uid()}"))')
(D/'ps2-can.kicad_sym').write_text('(kicad_symbol_lib (version 20241209)(generator "rnse")\n'+'\n'.join(syms)+')\n')
cache='\n'.join(s.replace('(symbol "'+a+'"','(symbol "ps2-can:'+a+'"',1) for s,a in [(s, s.split('"')[1]) for s in syms])
(D/'ps2-can.kicad_sch').write_text(f'''(kicad_sch (version 20250114) (generator "rnse") (uuid "{root}") (paper "A2")
(title_block (title "RNS-E PS/2 keyboard + mouse / fault-tolerant CAN") (rev "A") (comment 1 "5 V ATtiny1616 + MCP2515 + TJA1055T; 100 kbit/s") (comment 2 "Net-label interconnect; see README for bring-up and termination"))
(lib_symbols {cache})\n'''+ '\n'.join(instances)+')\n')
(D/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "ps2-can")(type "KiCad")(uri "${KIPRJMOD}/ps2-can.kicad_sym")(options "")(descr "Project symbols")))\n')
project={'meta':{'filename':'ps2-can.kicad_pro','version':1},'board':{'design_settings':{'rules':{'min_clearance':.2,'min_track_width':.15,'min_via_diameter':.6,'min_through_hole_diameter':.3,'min_copper_edge_clearance':.3}}},'net_settings':{'classes':[{'name':'Default','clearance':.2,'track_width':.25,'via_diameter':.6,'via_drill':.3,'bus_width':12,'line_style':0,'microvia_diameter':.3,'microvia_drill':.1,'wire_width':6,'schematic_color':'rgba(0, 0, 0, 0.000)','pcb_color':'rgba(0, 0, 0, 0.000)'}],'meta':{'version':3}}}
(D/'ps2-can.kicad_pro').write_text(json.dumps(project,indent=2))
with (D/'bom.csv').open('w') as f:
    w=csv.writer(f);w.writerow(['Reference','Value','MPN','Footprint','Purchase search','Notes'])
    for a in parts:w.writerow([a['ref'],a['val'],a['mpn'],a['fp'],'https://www.digikey.com/en/products?keywords='+a['mpn'],a['note']])
(D/'connectivity.json').write_text(json.dumps(parts,indent=2))
print('Generated',len(parts),'components;',len(nets),'nets')
