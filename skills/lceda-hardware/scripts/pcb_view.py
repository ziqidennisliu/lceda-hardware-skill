#!/usr/bin/env python3
"""Read-only V4 PCB snapshot -> per-layer SVG, interactive HTML and physical stack.

No EDA connection or external dependencies. Positive filled copper only.
Unsupported geometry is reported; this is a review view, never manufacturing output.
"""
import argparse
from collections import Counter
import gzip
import hashlib
from html import escape
import json
import math
from pathlib import Path

MM = .0254


def records(source):
    for line in source.splitlines():
        if '||' not in line:
            continue
        head, body = line.split('||',1)
        if body == '|':
            continue
        yield json.loads(head), json.loads(body.rstrip('|'))


def points(path, scale):
    if len(path) < 2 or not all(isinstance(x,(float,int)) for x in path[:2]):
        raise ValueError('Unsupported path start')
    pts = [(path[0]*scale,path[1]*scale)]
    i = 2
    while i < len(path):
        if path[i] == 'L':
            i += 1
        elif path[i] == 'ARC':
            angle = math.radians(float(path[i+1]))
            end = (float(path[i+2])*scale,float(path[i+3])*scale)
            start = pts[-1]
            if math.dist(start,end) < 1e-10:
                raise ValueError('Ambiguous coincident-ended arc')
            if abs(angle) < 1e-10:
                pts.append(end)
            else:
                dx,dy = end[0]-start[0],end[1]-start[1]
                cx=(start[0]+end[0])/2-dy*.5/math.tan(angle/2)
                cy=(start[1]+end[1])/2+dx*.5/math.tan(angle/2)
                radius=math.hypot(start[0]-cx,start[1]-cy)
                start_angle=math.atan2(start[1]-cy,start[0]-cx)
                step=2*math.acos(max(-1,min(1,1-.002/max(radius,.002))))
                n=max(2,math.ceil(abs(angle)/max(step,1e-5)))
                pts.extend((cx+radius*math.cos(start_angle+angle*k/n),cy+radius*math.sin(start_angle+angle*k/n)) for k in range(1,n+1))
                pts[-1]=end
            i+=4
        elif isinstance(path[i],(int,float)) and i+1 < len(path):
            pts.append((float(path[i])*scale,float(path[i+1])*scale));i+=2
        else:
            raise ValueError(f'Unsupported path token {path[i]}')
    if not all(math.isfinite(v) for pt in pts for v in pt):
        raise ValueError('Non-finite geometry')
    return pts


def contours(obj, scale):
    if isinstance(obj,dict):
        obj=obj.get('complexPolygon',obj.get('polygon'))
    if not obj:
        raise ValueError('Empty contour')
    if isinstance(obj[0],(int,float)):
        obj=[obj]
    return [points(p,scale) for p in obj]


def dpath(paths, close=True):
    return ' '.join('M '+' L '.join(f'{x:.5f},{-y:.5f}' for x,y in path)+(' Z' if close else '') for path in paths)


def color(net):
    if net == 'GND': return '#82b899'
    digest=hashlib.sha256(net.encode()).digest()
    return f'hsl({int.from_bytes(digest[:2],"big")%360},58%,40%)'


def render(snapshot, output):
    source=list(records(snapshot['source']))
    layers={v['layerId']:v for h,v in source if h['type']=='LAYER'}
    physical=[]
    for h,v in source:
        if h['type']=='LAYER_PHYS':
            physical.append(dict(v,layerId=json.loads(h['id'])[1]))
    physical.sort(key=lambda x:x['zIndex'])
    active=[k for k,v in layers.items() if v.get('use') and v['layerType'] in ('TOP','BOTTOM','SIGNAL','PLANE')]
    order={v['layerId']:i for i,v in enumerate(physical)}
    active.sort(key=lambda k:order.get(k,10000+k))
    warnings=[]
    missing_physical=[k for k in active if k not in order]
    if missing_physical:
        warnings.append(f'Active copper missing physical stack records: {missing_physical}; fallback display order is NOT a verified physical stack')
    if any(layers[k]['layerType']=='PLANE' for k in active):
        warnings.append('Negative plane layers are not decoded; inspect native editor/Gerber')
    board=[]
    for h,v in source:
        if h['type']=='POLY' and layers.get(v.get('layerId'),{}).get('layerType') in ('BOARD_OUTLINE','OUTLINE'):
            board+=contours(v['path'],MM)
    if not board:
        raise ValueError('No supported native board outline; will not guess extents')
    xy=[p for c in board for p in c]
    x0,x1=min(p[0] for p in xy)-2,max(p[0] for p in xy)+2
    y0,y1=min(p[1] for p in xy)-2,max(p[1] for p in xy)+2
    vb=f'{x0} {-y1} {x1-x0} {y1-y0}'
    copper=snapshot['innerCopper']; parents={p['primitiveId']:p for p in copper['pours']}
    if copper['pours'] and not copper['poured']:
        warnings.append('POUR exists but no rebuilt POURED; no filled copper drawn')
    output.mkdir(parents=True,exist_ok=False)
    cards=[]
    for layer in active:
        svg=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="{escape(layers[layer]["layerName"])}">',
             f'<path d="{dpath(board)}" fill="#fafcfd" stroke="#334155" stroke-width=".12" fill-rule="evenodd"/>']
        for item in copper['poured']:
            parent=parents.get(item['pourPrimitiveId'])
            if not parent or parent['layer'] != layer: continue
            for fill in item['pourFills']:
                try:
                    path=dpath(contours(fill['path'],.254),bool(fill['fill']))
                    width=fill.get('lineWidth',0)*.254
                    style=f'fill="{color(parent["net"])}" opacity=".38"' if fill['fill'] else f'fill="none" stroke="{color(parent["net"])}" stroke-width="{width}"'
                    svg.append(f'<path data-net="{escape(parent["net"])}" d="{path}" {style} fill-rule="evenodd"/>')
                except (ValueError,KeyError,IndexError) as e:
                    warnings.append(f'Layer {layer} POURED skipped: {e}')
        for region in copper.get('regions',[]):
            if region['layer'] == layer:
                try: svg.append(f'<path d="{dpath(contours(region["complexPolygon"],MM))}" fill="none" stroke="#d97706" stroke-width=".08" stroke-dasharray=".35 .25"/>')
                except ValueError as e: warnings.append(f'Region skipped: {e}')
        for t in copper['lines']:
            if t['layer']==layer:
                svg.append(f'<path data-net="{escape(t["net"])}" d="M {t["startX"]*MM},{-t["startY"]*MM} L {t["endX"]*MM},{-t["endY"]*MM}" fill="none" stroke="{color(t["net"])}" stroke-width="{t["lineWidth"]*MM}" stroke-linecap="round"/>')
        for via in copper['vias']:
            if via.get('viaType') != 0:
                warnings.append('Blind/buried via span not rendered; inspect native view');continue
            svg.append(f'<circle data-net="{escape(via["net"])}" cx="{via["x"]*MM}" cy="{-via["y"]*MM}" r="{via["diameter"]*MM/2}" fill="{color(via["net"])}"/>')
            svg.append(f'<circle cx="{via["x"]*MM}" cy="{-via["y"]*MM}" r="{via["holeDiameter"]*MM/2}" fill="white"/>')
        for c in snapshot['components']:
            for pad in c['pads']:
                raw=pad['raw']; through=raw.get('hole') is not None
                if raw['layer']!=layer and not through: continue
                shape=raw['pad']; net=pad.get('net') or ''
                try:
                    kind,w,h=shape[0],float(shape[1])*MM,float(shape[2])*MM
                    trans=f'translate({pad["x"]*MM},{-pad["y"]*MM}) rotate({-pad.get("rotation",0)})'
                    if kind=='ELLIPSE': element=f'<ellipse cx="0" cy="0" rx="{w/2}" ry="{h/2}"'
                    elif kind in ('RECT','OVAL'):
                        radius=min(w,h)/2 if kind=='OVAL' else 0
                        element=f'<rect x="{-w/2}" y="{-h/2}" width="{w}" height="{h}" rx="{radius}"'
                    else: raise ValueError(f'unsupported pad {kind}')
                    svg.append(element+f' transform="{trans}" data-net="{escape(net)}" fill="{color(net)}"><title>{escape(c["ref"]+"."+str(pad["number"])+" "+net)}</title></'+('ellipse>' if kind=='ELLIPSE' else 'rect>'))
                    if through:
                        svg.append(f'<circle cx="{pad["x"]*MM}" cy="{-pad["y"]*MM}" r=".12" fill="white"/>')
                        warnings.append('PTH hole centers shown as markers, not drill dimensions; pad getter dimensions require native cross-check')
                except (ValueError,IndexError,TypeError) as e:
                    warnings.append(f'{c["ref"]}.{pad["number"]}: {e}')
            if c['layer']==layer:
                b=c['bbox']
                svg.append(f'<rect x="{b["minX"]*MM}" y="{-b["maxY"]*MM}" width="{(b["maxX"]-b["minX"])*MM}" height="{(b["maxY"]-b["minY"])*MM}" fill="none" stroke="#334155" stroke-width=".06"/>')
                svg.append(f'<text x="{c["x"]*MM}" y="{-c["y"]*MM}" font-size=".7" fill="#0f172a">{escape(c["ref"])}</text>')
        svg.append('</svg>')
        content='\n'.join(svg)
        (output/f'layer-{layer}.svg').write_text(content)
        name=escape(layers[layer]['layerName'])
        cards.append(f'<section><h2>{name} · ID {layer}</h2>{content}</section>')
    stack=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="'+str(50+36*len(physical))+'" viewBox="0 0 1000 '+str(50+36*len(physical))+'">']
    for i,p in enumerate(physical):
        item=layers.get(p['layerId'],{});typ=item.get('layerType','unknown'); y=20+i*36
        hue='#c79656' if p['layerId'] in active else '#d9e6ec'
        label=f'{item.get("layerName",p["layerId"])} | {p["thickness"]*MM:.5f} mm | {p.get("material","")}'
        stack.append(f'<rect x="10" y="{y}" width="210" height="24" fill="{hue}"/><text x="235" y="{y+17}" font-size="15">{escape(label)}</text>')
    stack.append('</svg>');stack=''.join(stack)
    (output/'stackup.svg').write_text(stack)
    report={'timestamp':snapshot.get('timestamp'),'pcb':snapshot.get('pcb'),'physical_records':physical,
            'copper_order':active,'physical_copper_count':sum(p['layerId'] in active for p in physical),
            'counts':{'components':len(snapshot['components']),**{k:len(v) for k,v in copper.items()}},
            'warnings':sorted(set(warnings)), 'scope':'Review SVG from actual snapshot, top projection for every layer; labels are annotations, not actual silkscreen. PTH holes schematic; no DRC or manufacturing signoff.'}
    html='''<!doctype html><meta charset="utf-8"><title>LCEDA layers</title><style>body{font:15px system-ui;margin:24px;color:#17354a;background:#eef3f6}header{position:sticky;top:0;background:#fff;padding:12px;z-index:2}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}section{background:white;padding:12px;border-radius:12px}section svg{width:100%;height:75vh}h2{font-size:18px}input{padding:8px}summary{cursor:pointer}</style>'''
    html+='<header><b>Actual snapshot · PCB layer review</b><p>Snapshot time: '+escape(str(snapshot.get('timestamp','unknown')))+'</p><p>All layers use top projection. Labels are annotations; PTH holes are markers. Not a manufacturing preview.</p><label>Highlight net <input id="net" placeholder="e.g. GND / SPI"></label></header>'
    html+='<details><summary>Physical stack (bars not to thickness scale)</summary>'+stack+'</details>'
    html+='<details><summary>Parser limitations</summary><pre>'+escape('\n'.join(report['warnings']))+'</pre></details><main>'+''.join(cards)+'</main>'
    html+='''<script>document.querySelector('#net').addEventListener('input',e=>{const q=e.target.value.toLowerCase();document.querySelectorAll('[data-net]').forEach(x=>{x.style.opacity=(!q||x.dataset.net.toLowerCase().includes(q))?'':'0.08';});});</script>'''
    (output/'index.html').write_text(html)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('snapshot',type=Path);p.add_argument('--output-dir',required=True,type=Path)
    a=p.parse_args();raw=a.snapshot.read_bytes()
    data=json.loads(gzip.decompress(raw) if a.snapshot.suffix=='.gz' else raw)
    report=render(data,a.output_dir)
    report['snapshot_sha256']=hashlib.sha256(raw).hexdigest()
    (a.output_dir/'view-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({'path':str((a.output_dir/'index.html').resolve()),'counts':report['counts'],'warnings':report['warnings']},ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
