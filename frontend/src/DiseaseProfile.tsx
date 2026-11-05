import {useEffect,useMemo,useState} from 'react';
import {ArrowDownToLine, ArrowUpRight, HeartPulse} from 'lucide-react';
import {countProfile,profileFile,type ProfileCube,type ProfileScope} from './profileData';
type Year = {id:string;year:number;file:string;partial:boolean;cutoffs:string|string[]};
type Partitions = {datasets:Record<string,{states:Record<string,{file:string}>}>};
type Point = {year:number;partial:boolean;cutoff:string;count:number|null;status:string};
type Props = {
 scope:ProfileScope; name:string; source:string; field:string; geography:string; territory:string;
 selected:Year; years:Year[]; partitions:Partitions|null; cube:ProfileCube;
 states:Record<string,string>; municipalities:Record<string,string>; eligible:string[]; eligibilityByYear:Record<string,string[]>|null;
 load:(file:string,signal:AbortSignal)=>Promise<ProfileCube>; openAtlas:()=>void;
};
const fmt=(n:number)=>new Intl.NumberFormat('es-MX').format(n);
const cut=(d:Year)=>Array.isArray(d.cutoffs)?d.cutoffs.join(', '):d.cutoffs;
export default function DiseaseProfile(p:Props){
 const {scope,selected,years,partitions,load}=p;
 const [trend,setTrend]=useState<Point[]|null>(null);
 const [busy,setBusy]=useState(false);
 const [trendKey,setTrendKey]=useState(0);
 const [peer,setPeer]=useState('');
 const [comparison,setComparison]=useState<{count:number;denominator:number}|null>(null);
 const [comparisonError,setComparisonError]=useState(false);
 const current=useMemo(()=>countProfile(p.cube,scope),[p.cube,scope]);
 const options=scope.municipality?p.eligible.filter(k=>k.startsWith(scope.state)&&k!==scope.municipality).map(k=>[k,p.municipalities[k]||k]):Object.entries(p.states).filter(([k])=>/^(0[1-9]|[12][0-9]|3[0-2])$/.test(k)&&k!==scope.state);
 const peerLabel=options.find(([k])=>k===peer)?.[1];
 useEffect(()=>{
  if(!trendKey)return;
  const controller=new AbortController();
  setBusy(true);setTrend(null);
  async function run(){
   const rows:Point[]=[];
   for(const d of years){
    if(controller.signal.aborted)return;
    const eligible=!scope.municipality||p.eligibilityByYear?.[d.id]?.includes(scope.municipality);
    const file=eligible?profileFile(d.file,partitions?.datasets[d.id]?.states[scope.state]?.file,scope):undefined;
    let count:number|null=null,status=eligible?'Sin partición municipal disponible':'Municipio sin correspondencia validada para este año';
    if(file)try{
     count=countProfile((d.id===selected.id?p.cube:await load(file,controller.signal)),scope)?.count??null;
     status=count===null?'Sin desagregación municipal':'Disponible';
    }catch{status='No se pudo cargar el agregado';}
    rows.push({year:d.year,partial:d.partial,cutoff:cut(d),count,status});
   }
   if(!controller.signal.aborted){setTrend(rows);setBusy(false);}
  }
  void run();
  return ()=>controller.abort();
 },[trendKey,years,partitions,scope,load,selected.id,p.cube,p.eligibilityByYear]);
 useEffect(()=>{
  setComparison(null);setComparisonError(false);
  if(!peer||!peerLabel)return;
  const c=new AbortController();
  const target={...scope,state:scope.municipality?scope.state:peer,municipality:scope.municipality?peer:''};
  const file=profileFile(selected.file,partitions?.datasets[selected.id]?.states[scope.state]?.file,target);
  if(!file){setComparisonError(true);return;}
  void (file!==selected.file?Promise.resolve(p.cube):load(file,c.signal)).then(cube=>{
   if(!c.signal.aborted){const result=countProfile(cube,target);setComparison(result);setComparisonError(!result);}
  }).catch(()=>{if(!c.signal.aborted)setComparisonError(true);});
  return ()=>c.abort();
 },[peer,peerLabel,scope,selected,partitions,p.cube,load]);
 function exportTrend(){
  if(!trend)return;
  const data=[['anio','registros','periodo_parcial','corte','estado_del_dato','cie10','fuente','geografia','entidad','municipio','sexo','grupo_edad_indice'],...trend.map(r=>[r.year,r.count??'',r.partial?'sí':'no',r.cutoff,r.status,scope.cause,p.source,p.geography,scope.state,scope.municipality,scope.sex,scope.age])];
  const url=URL.createObjectURL(new Blob(['\uFEFF'+data.map(row=>row.map(v=>'"'+String(v).replaceAll('"','""')+'"').join(',')).join('\r\n')],{type:'text/csv;charset=utf-8'}));
  const a=document.createElement('a');a.href=url;a.download='perfil-'+scope.cause+'-serie-anual.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 }
 const max=Math.max(1,...(trend||[]).map(r=>r.count??0));
 return <div className="disease-profile">
 <section className="panel disease-summary">
 <div className="disease-title"><HeartPulse size={25}/><div><span className="eyebrow">FICHA DESCRIPTIVA · CIE-10 {scope.cause}</span><h2>{p.name}</h2></div><button className="outline" onClick={p.openAtlas}>Ver en atlas <ArrowUpRight size={15}/></button></div>
 <p>{p.source} · {selected.year}{selected.partial?' · corte parcial '+cut(selected):''} · {p.territory}</p>
 <p>Campo analizado: <b>{p.field}</b>. Geografía: {p.geography.toLowerCase()}.</p>
 {current&&<p><b>{fmt(current.count)}</b> de {fmt(current.denominator)} registros del mismo universo filtrado{current.denominator?' ('+(100*current.count/current.denominator).toLocaleString('es-MX',{maximumFractionDigits:2})+' %)':''}. Proporción de registros, no prevalencia.</p>}
 </section>
 <section className="panel disease-section"><div className="disease-section-head"><div><span className="eyebrow">MISMA FUENTE Y MISMOS FILTROS</span><h3>Evolución anual</h3></div><div className="export-buttons">{trend&&<button className="outline" onClick={exportTrend}><ArrowDownToLine size={15}/> CSV anual</button>}<button className="outline" disabled={busy} onClick={()=>setTrendKey(x=>x+1)}>{busy?'Cargando…':trend?'Actualizar serie':'Cargar serie anual'}</button></div></div>
 <p>Se consultan los archivos anuales de esta fuente. Los cortes parciales se muestran por separado y los faltantes no se tratan como cero. La cobertura puede cambiar entre años.</p>
 {busy&&<p role="status">Leyendo un agregado por vez…</p>}
 {trend&&<div className="table-scroll"><table><thead><tr><th>Año</th><th>Registros</th><th>Disponibilidad</th></tr></thead><tbody>{trend.map(r=><tr key={r.year}><td>{r.year}{r.partial?' · parcial':''}</td><td>{r.count===null?'—':<div className="profile-bar"><span style={{width:(100*r.count/max)+'%'}} className={r.partial?'partial':''}/><b>{fmt(r.count)}</b></div>}</td><td>{r.status}{r.partial&&r.cutoff?' · corte '+r.cutoff:''}</td></tr>)}</tbody></table></div>}
 </section>
 <section className="panel disease-section"><div className="disease-section-head"><div><span className="eyebrow">{selected.year} · {p.geography.toUpperCase()}</span><h3>Comparación territorial</h3></div></div>
 <p>Compara conteos con el mismo año, fuente, causa, edad y sexo. Los tamaños de población y la cobertura pueden diferir; no es una comparación de riesgo.</p>
 {!scope.state?<p>Elige una entidad en los filtros para activar el comparador.</p>:<label className="profile-peer">{scope.municipality?'Otro municipio de la entidad':'Otra entidad'}<select aria-label="Territorio de comparación" value={peer} onChange={e=>setPeer(e.target.value)}><option value="">Selecciona un territorio</option>{options.map(([k,n])=><option value={k} key={k}>{k} · {n}</option>)}</select></label>}
 {peer&&peerLabel&&(comparisonError?<p role="status">No hay un agregado disponible para el comparador.</p>:comparison?<div className="profile-pair"><div><span>{p.territory}</span><b>{current?fmt(current.count):'—'}</b></div><div><span>{peerLabel}</span><b>{fmt(comparison.count)}</b></div></div>:<p role="status">Cargando comparación…</p>)}
 </section>
 </div>;
}
