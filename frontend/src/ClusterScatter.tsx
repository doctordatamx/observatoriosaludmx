import {useState} from 'react';
import {colors} from './ClusterTree';
export type Mds={points:{state:string;x:number;y:number}[];retained:number;distortion:number};
export default function ClusterScatter({mds,groups,states,entity,setEntity,k}:{mds:Mds;groups:Record<string,number>;states:Record<string,string>;entity:string;setEntity:(code:string)=>void;k:number}){
 const [hover,setHover]=useState('');
 const code=hover||entity;
 const info=mds.points.find(p=>p.state===code);
 const extent=(Math.max(...mds.points.flatMap(p=>[Math.abs(p.x),Math.abs(p.y)]))||1)*1.12;
 const px=(n:number)=>58+390*(n+extent)/(2*extent);
 const py=(n:number)=>22+390*(extent-n)/(2*extent);
 const fmt=(n:number)=>n.toLocaleString('es-MX',{maximumFractionDigits:3});
 const pct=(n:number)=>(n*100).toLocaleString('es-MX',{maximumFractionDigits:1})+' %';
 function toggle(id:string){setEntity(entity===id?'':id);}
 return <section className="cluster-tree cluster-scatter" aria-label="Dispersión MDS por entidad">
 <div className="cluster-tree-head"><div><h4>Dispersión MDS · 2 dimensiones</h4><p>Cada punto es una entidad. Selecciona un punto para resaltarlo también en el dendrograma.</p></div></div>
 <div className="cluster-tree-legend">{colors.slice(0,k).map((c,i)=><span key={c}><i style={{background:c}}/>Grupo {i+1}</span>)}</div>
 <div className="mds-layout">
 <svg viewBox="0 0 476 458" role="group" aria-label="Plano de coordenadas principales con una escala igual en los dos ejes">
 {[-1,-.5,0,.5,1].map(t=><g key={t}><line x1={px(t*extent)} x2={px(t*extent)} y1={22} y2={412} stroke={t===0?'#a5bac6':'#e4ebef'}/><line x1={58} x2={448} y1={py(t*extent)} y2={py(t*extent)} stroke={t===0?'#a5bac6':'#e4ebef'}/><text x={px(t*extent)} y={429} textAnchor="middle" className="cluster-axis-label">{fmt(t*extent)}</text><text x={50} y={py(t*extent)+3} textAnchor="end" className="cluster-axis-label">{fmt(t*extent)}</text></g>)}
 <text x={253} y={450} textAnchor="middle" className="cluster-axis-label">Dimensión 1</text><text transform="translate(13 218) rotate(-90)" textAnchor="middle" className="cluster-axis-label">Dimensión 2</text>
 {mds.points.map(p=>{
  const selected=p.state===entity, group=groups[p.state];
  return <circle className="mds-dot" key={p.state} cx={px(p.x)} cy={py(p.y)} r={selected?7:5.5} fill={colors[group-1]} stroke={selected?'#132c3b':'white'} strokeWidth={selected?2:1} opacity={entity&&!selected&&group!==groups[entity]?0.36:1}
   role="button" tabIndex={0} aria-pressed={selected} aria-label={(states[p.state]||p.state)+', grupo '+group} onMouseEnter={()=>setHover(p.state)} onMouseLeave={()=>setHover('')} onFocus={()=>setHover(p.state)} onBlur={()=>setHover('')} onClick={()=>toggle(p.state)} onKeyDown={e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();toggle(p.state);}}}><title>{states[p.state]||p.state} · Grupo {group}</title></circle>;
 })}
 </svg>
 <div className="mds-info">
 <p><b>{pct(mds.retained)}</b><br/>Variación de la configuración conservada en 2D</p>
 <p><b>{pct(mds.distortion)}</b><br/>Error relativo de las distancias representadas</p>
 <p aria-live="polite">{info?<><b>{states[code]||code}</b><br/>Grupo {groups[code]} · ({fmt(info.x)}, {fmt(info.y)})</>: 'Pasa el puntero o usa el teclado para identificar una entidad.'}</p>
 </div></div><p>La cercanía aproxima la similitud del perfil de causas. Los ejes no son indicadores epidemiológicos; el árbol y los grupos se calculan en el espacio completo.</p>
 </section>;
}
