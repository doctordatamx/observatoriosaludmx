export type WardTree={labels:string[];order:number[];merge:[number,number][];height:number[]};
export const colors=['#09786e','#375f9d','#a35324','#82508e'];
const format=(n:number)=>n.toLocaleString('es-MX',{maximumFractionDigits:3});
type Node={x:number;y:number;group:number};
export default function ClusterTree({tree,groups,states,k,entity,setEntity}:{tree:WardTree;groups:Record<string,number>;states:Record<string,string>;k:number;entity:string;setEntity:(code:string)=>void}){
 const active=groups[entity];
 const name=(code:string)=>states[code]||code;
 const width=760, origin=205, end=728, top=48, step=23;
 const height=top+tree.labels.length*step+22;
 const max=tree.height.at(-1)||1;
 const x=(value:number)=>origin+(end-origin)*value/max;
 const leaves:Node[]=[];
 tree.order.forEach((index,i)=>{leaves[index-1]={x:origin,y:top+i*step,group:groups[tree.labels[index-1]]};});
 const nodes:Node[]=[];
 const lines=tree.merge.map(([left,right],i)=>{
  const a=left<0?leaves[-left-1]:nodes[left-1];
  const b=right<0?leaves[-right-1]:nodes[right-1];
  const n={x:x(tree.height[i]),y:(a.y+b.y)/2,group:a.group===b.group?a.group:0};
  nodes.push(n);
  return {a,b,n,height:tree.height[i]};
 });
 const cutIndex=tree.labels.length-k;
 const lower=tree.height[cutIndex-1]??0, upper=tree.height[cutIndex];
 const cut=upper>lower?x((lower+upper)/2):null;
 function choose(code:string){setEntity(entity===code?'':code);}
 return <section className="cluster-tree" aria-label="Dendrograma de entidades">
 <div className="cluster-tree-head"><div><h4>Dendrograma interactivo</h4><p>Selecciona una entidad para resaltar su grupo. Las uniones más a la derecha ocurren a mayor altura de fusión.</p></div><label>Entidad<select aria-label="Seleccionar entidad en el dendrograma" value={entity} onChange={e=>setEntity(e.target.value)}><option value="">Todas las entidades</option>{tree.order.map(i=>{const code=tree.labels[i-1];return <option value={code} key={code}>{name(code)}</option>;})}</select></label></div>
 <div className="cluster-tree-legend">{colors.slice(0,k).map((c,i)=><span key={c}><i style={{background:c}}/>Grupo {i+1}</span>)}{cut!==null&&<span><i className="cut-key"/>Corte de {k} grupos</span>}</div>
 <p className="cluster-tree-selection" aria-live="polite">{active?<><b>{name(entity)} · Grupo {active}</b>{' — '}{tree.order.map(i=>tree.labels[i-1]).filter(c=>c!==entity&&groups[c]===active).map(name).join(' · ')||'Sin otras entidades en este grupo.'}</>:'Ninguna entidad seleccionada.'}</p>
 <div className="cluster-tree-scroll" tabIndex={0} aria-label="Área desplazable del dendrograma">
 <svg width={width} height={height} role="group" aria-label={'Árbol jerárquico de Ward, '+k+' grupos'}>
 <text x={origin} y={16} className="cluster-axis-label">Altura de fusión (Ward.D2)</text>
 {[0,.25,.5,.75,1].map(t=><g key={t}><line x1={x(t*max)} x2={x(t*max)} y1={34} y2={height-13} stroke="#e4ebef"/><text x={x(t*max)} y={30} textAnchor="middle" className="cluster-axis-label">{format(t*max)}</text></g>)}
 {cut!==null&&<line x1={cut} x2={cut} y1={34} y2={height-13} stroke="#725d36" strokeDasharray="5 4"/>}
 {lines.map(({a,b,n,height},i)=><path key={i} d={`M ${a.x} ${a.y} H ${n.x} V ${b.y} H ${b.x}`} stroke={n.group?colors[n.group-1]:'#8c9aa3'} opacity={active&&n.group&&n.group!==active?0.28:1} strokeWidth={active&&n.group===active?2.6:1.5} fill="none"><title>Altura de fusión: {format(height)}</title></path>)}
 {tree.order.map(i=>{
  const code=tree.labels[i-1],leaf=leaves[i-1],group=groups[code],selected=entity===code;
  return <g className="cluster-leaf" key={code} role="button" tabIndex={0} aria-pressed={selected} aria-label={name(code)+', grupo '+group} onClick={()=>choose(code)} onKeyDown={e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();choose(code);}}}>
   <title>{name(code)} · Grupo {group}</title><rect x={4} y={leaf.y-10} width={origin+3} height={20} rx={3} fill={selected?'#dcefed':'transparent'}/>
   <text x={10} y={leaf.y+4} fill="#243b49" opacity={active&&group!==active?0.53:1}>{name(code).length>30?name(code).slice(0,29)+'…':name(code)}</text>
   <circle cx={origin} cy={leaf.y} r={selected?5:3.5} fill={colors[group-1]}/>
  </g>;
 })}
 </svg></div>
 {cut===null&&<p>Hay un empate en la altura del corte; los colores muestran la asignación de Ward sin dibujar una línea de separación.</p>}
 </section>;
}
