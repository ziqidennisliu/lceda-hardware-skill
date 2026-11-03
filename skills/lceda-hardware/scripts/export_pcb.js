// Read-only editor payload. Query current version API before reuse on other versions.
const args = __CLI__.args;
if (!args?.projectUuid || !args?.pcbUuid) throw Error('Explicit projectUuid and pcbUuid required');
const project = await eda.dmt_Project.getCurrentProjectInfo();
const pcb = await eda.dmt_Pcb.getCurrentPcbInfo();
if (project?.uuid !== args.projectUuid || pcb?.uuid !== args.pcbUuid) throw Error('Target identity mismatch; no export');
const source = await eda.sys_FileManager.getDocumentSource();
if (!source) throw Error('No native document source');
const first = source.split('\n')[0].split('||')[1];
const header = JSON.parse(first.replace(/\|$/, ''));
if (header.docType !== 'PCB' || header.uuid !== pcb.uuid) throw Error('Current source is not target PCB');
const components = [];
for (const c of await eda.pcb_PrimitiveComponent.getAll()) {
  const id = c.getState_PrimitiveId();
  const pads = await eda.pcb_PrimitiveComponent.getAllPinsByPrimitiveId(id);
  components.push({id, ref:c.getState_Designator(), x:c.getState_X(), y:c.getState_Y(),
    rotation:c.getState_Rotation(), layer:c.getState_Layer(), state:c,
    bbox:await eda.pcb_Primitive.getPrimitivesBBox([id]),
    pads:pads.map(p=>({id:p.getState_PrimitiveId(), number:p.getState_PadNumber(),
      x:p.getState_X(), y:p.getState_Y(), rotation:p.getState_Rotation(), net:p.getState_Net(), raw:p}))});
}
const body = {schema_version:1,timestamp:new Date().toISOString(),project,pcb,source,components,
  units:{pcb:'mil',poured:'10mil',physical_thickness:'mil'},
  strings:await eda.pcb_PrimitiveString.getAll(),attributes:await eda.pcb_PrimitiveAttribute.getAll(),
  innerCopper:{lines:await eda.pcb_PrimitiveLine.getAll(),vias:await eda.pcb_PrimitiveVia.getAll(),
    pours:await eda.pcb_PrimitivePour.getAll(),poured:await eda.pcb_PrimitivePoured.getAll(),regions:await eda.pcb_PrimitiveRegion.getAll()}};
// Native export regenerates DOCHEAD client/updateTime/version even on a read.
// Ignore only those observed export metadata fields; keep every content record.
function stableSource(text) {
  return text.split('\n').map(line=>{
    const i=line.indexOf('||'); if(i<0)return line;
    const head=JSON.parse(line.slice(0,i)); if(head.type!=='DOCHEAD')return line;
    const body=JSON.parse(line.slice(i+2).replace(/\|$/,''));
    delete body.client; delete body.updateTime; delete body.version;
    return JSON.stringify(head)+'||'+JSON.stringify(body);
  }).join('\n');
}
if (stableSource(await eda.sys_FileManager.getDocumentSource()) !== stableSource(source)) throw Error('Document changed during export; discard and retry when stable');
const reader = new Blob([JSON.stringify(body)]).stream().pipeThrough(new CompressionStream('gzip')).getReader();
let encoded='', bytes=0;
for (;;) { const chunk=await reader.read(); if(chunk.done)break; bytes+=chunk.value.length;
  for(let i=0;i<chunk.value.length;i+=32768)encoded+=String.fromCharCode(...chunk.value.slice(i,i+32768)); }
return {gzip:btoa(encoded),bytes,components:components.length,pcbUuid:pcb.uuid};
