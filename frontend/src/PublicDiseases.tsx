import {useEffect,useMemo,useState} from 'react';
import {matchesDisease} from './diseaseSearch';
import Chart from './Chart';

type Dataset={id:string;source:string;year:number;partial:boolean;cutoffs:string[];url:string;counts:Record<string,number>};
type Data={updated:string;causes:Record<string,string>;datasets:Dataset[];suppression_minimum:number};
const names:Record<string,string>={defunciones:'Defunciones',egresos:'Egresos institucionales',urgencias:'Urgencias',lesiones:'Lesiones',sectorial:'Egresos sectoriales'};
export default function PublicDiseases(){
 const [data,setData]=useState<Data|null>(null),[error,setError]=useState('');
 const [query,setQuery]=useState(''),[source,setSource]=useState('defunciones'),[year,setYear]=useState(2024),[cause,setCause]=useState('');
 useEffect(()=>{const c=new AbortController();fetch(import.meta.env.BASE_URL+'analysis/diseases.json',{signal:c.signal}).then(r=>{if(!r.ok)throw Error('No se pudo cargar el catálogo.');return r.json();}).then(setData).catch(e=>{if(!c.signal.aborted)setError(e.message);});return()=>c.abort();},[]);
 const available=data?.datasets.filter(d=>d.source===source)??[];
 const selected=available.find(d=>d.year===year)??available.at(-1);
 const codes=useMemo(()=>[...new Set(available.flatMap(d=>Object.keys(d.counts)))].sort().filter(code=>matchesDisease(code,data?.causes[code]??'',query)),[data,source,query]);
 if(error)return <section className="panel" role="alert">{error}</section>;
 if(!data)return <p role="status">Cargando enfermedades…</p>;
 const rows=codes.filter(code=>!cause||code===cause).map(code=>({code,count:selected?.counts[code]}));
 const trend=available.slice().sort((a,b)=>a.year-b.year);
 return <>
 <section className="filters panel"><h2>Buscar enfermedades por nombre o CIE-10</h2>
 <div className="filter-grid">
 <label>Fuente<select value={source} onChange={e=>{setSource(e.target.value);setCause('');}}>{Object.entries(names).map(([id,name])=><option key={id} value={id}>{name}</option>)}</select></label>
 <label>Periodo<select value={selected?.year??year} onChange={e=>setYear(Number(e.target.value))}>{available.map(d=><option key={d.year} value={d.year}>{d.year}{d.partial?' · parcial':''}</option>)}</select></label>
 <label>Buscar enfermedad<input value={query} placeholder="Ca de colon, hepatocarcinoma, C18…" onChange={e=>{setQuery(e.target.value);setCause('');}}/></label>
 <label>Categoría CIE-10<select value={cause} onChange={e=>setCause(e.target.value)}><option value="">Todas las coincidencias</option>{codes.map(code=><option key={code} value={code}>{code} · {data.causes[code]??'Categoría sin etiqueta'}</option>)}</select></label>
 </div><p className="chart-note">Conteos nacionales anuales por categoría. Valores omitidos por protección o ausencia se muestran como no disponibles. C22 incluye varios tumores del hígado y vías biliares intrahepáticas.</p>
 </section>
 {cause&&<Chart title={'Evolución anual · '+cause} kicker={names[source]} summary="Los periodos parciales se indican en el eje. Los valores no disponibles interrumpen la serie."
 option={{tooltip:{trigger:'axis',confine:true},grid:{left:65,right:20,bottom:40},xAxis:{type:'category',data:trend.map(d=>String(d.year)+(d.partial?'*':''))},yAxis:{type:'value'},series:[{type:'line',connectNulls:false,data:trend.map(d=>d.counts[cause]??null)}]}}/>}
 <section className="panel"><h3>{names[source]} · {selected?.year}{selected?.partial?' · corte parcial '+selected.cutoffs.join(', '):''}</h3>
 <div className="table-scroll"><table><thead><tr><th>CIE-10</th><th>Descripción</th><th>Registros</th></tr></thead><tbody>{rows.map(({code,count})=><tr key={code}><td><button className="code-link" onClick={()=>setCause(code)}>{code}</button></td><td>{data.causes[code]??'Categoría sin etiqueta'}</td><td>{count===undefined?'No disponible':count.toLocaleString('es-MX')}</td></tr>)}</tbody></table></div>
 {!rows.length&&<p role="status">Sin coincidencias. Prueba otro nombre o código.</p>}
 <p className="chart-note"><a href={selected?.url}>Fuente original · Secretaría de Salud / DGIS</a> · Agregación por Doctor Data MX · Procesado {data.updated}.</p>
 </section></>;
}
