import ClusterScatter, {type Mds} from './ClusterScatter';
import ClusterTree, {type WardTree} from './ClusterTree';
import {useEffect,useState} from 'react';
type Dataset={id:string;source:string;year:number};
type Index={datasets:Dataset[];vintage:string;minimum_records:number;queen_edges:number;rook_edges:number};
type Cluster={k:number;silhouette:number;stability:number;groups:Record<string,number>};
type Month={month:number;n:number;den:number;share:number;typical:number;lo:number;hi:number;baseline:string;flag:'above'|'below'|'inside'};
type Model=Dataset&{geography:string;coverage:string;entities:number;sha256:string;cluster_codes:string[];clusters:Cluster[];dendrogram:WardTree|null;mds:Mds|null;moran:Record<string,{queen:number;rook:number|null;n:number;rook_n:number|null}>;anomalies:Record<string,Month[]>};
const number=(n:number)=>new Intl.NumberFormat('es-MX').format(n);
const decimal=(n:number|null)=>n==null?'—':n.toLocaleString('es-MX',{maximumFractionDigits:3});
const percent=(n:number)=>decimal(n*100)+' %';
const months=['','Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
async function read<T>(file:string,signal:AbortSignal):Promise<T>{
 const r=await fetch(import.meta.env.BASE_URL+'data/lab/'+file,{signal});
 if(!r.ok)throw Error('No se pudo cargar el análisis.');
 return r.json();
}
export default function Laboratory({sources,causes,states,initial,onSelection}:{sources:Record<string,string>;causes:Record<string,string>;states:Record<string,string>;initial:{source:string;year:number;cause:string};onSelection:(v:Partial<{source:string;year:number;cause:string}>)=>void}){
 const [index,setIndex]=useState<Index|null>(null),[model,setModel]=useState<Model|null>(null);
 const {source,year}=initial;const cause=initial.cause||'E11';const [query,setQuery]=useState(''),[k,setK]=useState(3);
 const [error,setError]=useState(''),[retry,setRetry]=useState(0);
 useEffect(()=>{const c=new AbortController();setError('');read<Index>('index.json',c.signal).then(setIndex).catch(()=>{if(!c.signal.aborted)setError('No se pudo cargar el catálogo del Laboratorio.');});return()=>c.abort();},[retry]);
 const years=index?.datasets.filter(d=>d.source===source)||[];
 const selected=years.find(d=>d.year===year)||years.at(-1);
 useEffect(()=>{if(selected&&selected.year!==year)onSelection({year:selected.year});},[selected?.year,year,onSelection]);
 useEffect(()=>{
  if(!selected)return;
  const c=new AbortController();setModel(null);setError('');
  read<Model>(selected.id+'.json',c.signal).then(m=>{if(!c.signal.aborted)setModel(m);}).catch(()=>{if(!c.signal.aborted)setError('No se pudo cargar el análisis del periodo.');});
  return()=>c.abort();
 },[selected?.id,retry]);
 const data=model?.id===selected?.id?model:null;
 const [selection,setSelection]=useState({id:"",code:""});
 const entity=selection.id===data?.id?selection.code:"";
 const setEntity=(code:string)=>setSelection({id:data?.id||"",code});
 const group=data?.clusters.find(x=>x.k===k);
 const moran=data?.moran[cause];const anomaly=data?.anomalies[cause];
 const matching=Object.keys(causes).filter(c=>(c+' '+causes[c]).toLocaleLowerCase('es-MX').includes(query.toLocaleLowerCase('es-MX')));
 return <div className="lab">
 <section className="panel filters"><h2>Configura el análisis</h2><p className="lab-note">Solo años sin corte parcial. Todas las edades y sexos; el laboratorio no aplica filtros municipales ni demográficos de otras vistas.</p><div className="lab-controls">
 <label>Fuente<select aria-label="Fuente del laboratorio" value={source} onChange={e=>onSelection({source:e.target.value,year:0})}>{Object.entries(sources).map(([id,name])=><option key={id} value={id}>{name}</option>)}</select></label>
 <label>Año<select aria-label="Año del laboratorio" value={selected?.year??''} onChange={e=>onSelection({year:Number(e.target.value)})}>{years.map(y=><option key={y.id}>{y.year}</option>)}</select></label>
 <label>Buscar categoría<input placeholder="Nombre o CIE-10" value={query} onChange={e=>setQuery(e.target.value)}/></label>
 <label>CIE-10<select aria-label="Categoría del laboratorio" value={cause} onChange={e=>onSelection({cause:e.target.value})}>{!matching.includes(cause)&&<option value={cause}>{cause} · {causes[cause]||'Código sin etiqueta'}</option>}{matching.map(c=><option key={c} value={c}>{c} · {causes[c]}</option>)}</select></label>
 </div></section>
 {error?<section className="panel disease-section" role="alert"><p>{error}</p><button className="outline" onClick={()=>setRetry(x=>x+1)}>Reintentar</button></section>:!data?<p role="status" className="lab-note">Cargando análisis…</p>:<>
 <p className="lab-note">{data.coverage} · {data.year} · {data.geography}. Son resultados descriptivos; la cobertura y la codificación pueden explicar los patrones.</p>
 <section className="panel disease-section"><span className="eyebrow">COMPOSICIÓN DE REGISTROS</span><h3>Agrupamiento de entidades</h3><p>Ward con las 12 categorías más registradas y el resto, usando proporciones transformadas por raíz cuadrada. Este modelo usa el perfil completo; el selector CIE-10 no cambia los grupos.</p>
 <label className="profile-peer">Número de grupos<select aria-label="Número de grupos" value={k} onChange={e=>setK(Number(e.target.value))}>{[2,3,4].map(x=><option key={x}>{x}</option>)}</select></label>
 {group?<><div className="lab-metrics"><div><b>{data.entities}</b><span>Entidades analizadas</span></div><div><b>{decimal(group.silhouette)}</b><span>Silueta media</span></div><div><b>{percent(group.stability)}</b><span>Estabilidad al retirar categorías</span></div></div>{data.mds&&<ClusterScatter key={data.id} mds={data.mds} groups={group.groups} states={states} entity={entity} setEntity={setEntity} k={k}/>} {data.dendrogram&&<ClusterTree key={data.id} tree={data.dendrogram} groups={group.groups} states={states} k={k} entity={entity} setEntity={setEntity}/>}<div className="lab-groups">{Array.from({length:k},(_,i)=><div key={i}><b>Grupo {i+1}</b><p>{Object.entries(group.groups).filter(([,g])=>g===i+1).map(([s])=>states[s]||s).join(' · ')}</p></div>)}</div><p>Categorías utilizadas: {data.cluster_codes.join(', ')}. Los números de grupo son etiquetas, no rangos de gravedad.</p></>:<p>Datos insuficientes o perfiles sin variación para agrupar.</p>}</section>
 <section className="panel disease-section"><span className="eyebrow">PATRÓN ENTRE VECINOS · {cause}</span><h3>Autocorrelación espacial</h3><p>Índice global de Moran sobre la proporción de registros de la categoría por entidad. Se contrastan dos definiciones de vecindad: cualquier contacto y frontera compartida. {index?.queen_edges===index?.rook_edges&&index&&`En este marco ambas producen las mismas ${index.queen_edges} conexiones.`}</p>
 {moran?<div className="lab-metrics"><div><b>{decimal(moran.queen)}</b><span>I · contacto ({moran.n} entidades)</span></div><div><b>{decimal(moran.rook)}</b><span>I · frontera ({moran.rook_n??'—'} entidades)</span></div></div>:<p>Sin estimación: categoría ausente, proporciones constantes o entidades vecinas insuficientes.</p>}
 <p>Geometrías sin simplificar: {index?.vintage}. Entidades con al menos {number(index?.minimum_records||0)} registros; se excluyen las que quedan sin vecinos. No hay prueba de significación ni detección de focos locales.</p></section>
 <section className="panel disease-section"><span className="eyebrow">REFERENCIA HISTÓRICA NACIONAL · {cause}</span><h3>Meses fuera del rango histórico</h3><p>Compara la proporción mensual con el rango del mismo mes en al menos tres años previos de la misma fuente. Un mes fuera del rango merece revisión; no es una alerta de brote.</p>
 {anomaly?.length?<div className="table-scroll"><table><thead><tr><th>Mes</th><th>Registros de la categoría</th><th>Proporción observada</th><th>Mediana y rango previo</th><th>Periodos de referencia</th><th>Resultado</th></tr></thead><tbody>{anomaly.map(m=><tr key={m.month}><td>{months[m.month]}</td><td>{number(m.n)} / {number(m.den)}</td><td>{percent(m.share)}</td><td>{percent(m.typical)} ({percent(m.lo)}–{percent(m.hi)})</td><td>{m.baseline}</td><td>{m.flag==='above'?'Por encima':m.flag==='below'?'Por debajo':'Dentro del rango'}</td></tr>)}</tbody></table></div>:<p>No hay meses evaluables para esta categoría y año. Se requieren tres años previos observados y mediana histórica de al menos 20 registros de la categoría.</p>}</section>
 <p className="lab-note">Archivo de origen: SHA-256 <code>{data.sha256}</code>. <a href={import.meta.env.BASE_URL+'docs/MODELOS_AVANZADOS.md'} download>Métodos y límites</a>.</p>
 </>}
 </div>;
}
