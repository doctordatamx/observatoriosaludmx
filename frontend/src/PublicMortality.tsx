import type {GeoIndex} from './Atlas';
import type {ReactNode} from 'react';
import {Activity, ArrowUpRight, HeartPulse, ShieldCheck, SlidersHorizontal, Stethoscope} from 'lucide-react';
import Chart from './Chart';

const mortalitySource = 'https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2025/edr/EDR2024-def_RR.pdf';

// INEGI, EDR 2024, gráfica 1 y cuadros 1 y 2 (reporte 44/25).
const publicSources = {
 panorama: {label:'Defunciones', agency:'INEGI', icon:HeartPulse, url:mortalitySource,
  totals:[1086743,1122249,847716,799869,819672]},
 egresos: {label:'Egresos institucionales', agency:'DGIS', icon:Stethoscope,
  url:'http://www.dgis.salud.gob.mx/contenidos/basesdedatos/da_egresoshosp_gobmx.html', totals:[1937344,2088779,2479897,2591278,2649236]},
 urgencias: {label:'Urgencias', agency:'DGIS', icon:Activity,
  url:'http://www.dgis.salud.gob.mx/contenidos/basesdedatos/da_urgencias_gobmx.html', totals:[5284803,5383305,7074271,7806625,7989731]},
 lesiones: {label:'Lesiones', agency:'DGIS', icon:ShieldCheck,
  url:'http://www.dgis.salud.gob.mx/contenidos/basesdedatos/da_lesiones_gobmx.html', totals:[496335,622798,749528,934009,1074543]},
};
type PublicSource = keyof typeof publicSources;
const sourceEntries = Object.entries(publicSources) as [PublicSource,(typeof publicSources)[PublicSource]][];
export const publicViews = ['enfermedades','atlas',...Object.keys(publicSources)];
const residence = [
 7592, 22934, 4237, 5824, 19733, 5614, 31622, 27302, 67080, 10445, 41001,
 18824, 18523, 54987, 99701, 30644, 15835, 7430, 36807, 29098, 42266, 12960,
 9300, 19360, 17160, 19757, 16105, 21600, 7685, 61341, 16215, 10304,
];
export const stateDeaths = Object.fromEntries(residence.map((count,index)=>[
 String(index+1).padStart(2,'0'), count,
]));
const otherResidence = [['Extranjero',1501],['No especificada',8885]] as const;
const leadingCauses = [
 ['Enfermedades del corazón',192518], ['Diabetes mellitus',112577],
 ['Tumores malignos',95108], ['Enfermedades del hígado',40645], ['Accidentes',39919],
] as const;
const format = new Intl.NumberFormat('es-MX');

export default function PublicMortality({view,geo,state,year,onYear,onState,navigate,children}:{
 view:string;geo:GeoIndex|null;state:string;year:number;onYear:(year:number)=>void;
 onState:(state:string)=>void;navigate:(view:string)=>void;children?:ReactNode;
}){
 const isAtlas=view==='atlas';
 const isCauses=view==='enfermedades';
 const activeSource:PublicSource = view==='egresos'||view==='urgencias'||view==='lesiones'?view:'panorama';
 const source = publicSources[activeSource];
 const annualCounts = source.totals.map((count,index)=>[2020+index,count] as const);
 const selectedYear = isAtlas||isCauses||!annualCounts.some(([y])=>y===year)?2024:year;
 const total = source.totals[selectedYear-2020];
 const selectedName=geo?.states[state];
 const rows=isCauses?leadingCauses:isAtlas
  ? [...Object.entries(stateDeaths).map(([code,count])=>[geo?.states[code]??code,count] as const),...otherResidence]
  : annualCounts;
 return <>
 <section className="source-cards" aria-label="Fuentes del observatorio">
  {sourceEntries.map(([target,{label,icon:Icon,totals,agency}])=><button key={target} className={target===activeSource?'source-card selected':'source-card'} onClick={()=>navigate(target)}>
   <div><span className="card-symbol"><Icon size={19}/></span><ArrowUpRight size={16}/></div>
   <span className="card-label">{label}</span><strong>{format.format(totals[selectedYear-2020])}</strong>
   <small>{selectedYear} · {agency}</small>
  </button>)}
 </section>
 <section className="filters panel">
  <div className="filter-heading"><b><SlidersHorizontal size={17}/> Configura tu consulta</b></div>
  <div className="filter-grid">
   <label>Fuente<select value={activeSource} onChange={e=>navigate(e.target.value)}>{sourceEntries.map(([id,item])=><option key={id} value={id}>{item.label} · {item.agency}</option>)}</select></label>
   <label>Periodo<select value={selectedYear} onChange={e=>onYear(Number(e.target.value))}>
    {(isAtlas||isCauses?annualCounts.slice(-1):annualCounts).map(([y])=><option key={y}>{y}</option>)}
   </select></label>
   {isAtlas&&<label>Entidad<select value={state} onChange={e=>onState(e.target.value)}>
    <option value="">México</option>{Object.entries(geo?.states??{}).map(([code,name])=><option key={code} value={code}>{code} · {name}</option>)}
   </select></label>}
  </div>
 </section>
 <div className="context-bar"><span>{source.agency} · {source.label} · {selectedYear}</span><span>{isAtlas?'Residencia habitual':isCauses?'Grupos de causas nacionales':'Serie nacional anual'}</span></div>
 {children}
 {!isAtlas&&<div className="chart-grid"><Chart wide kicker={source.agency}
  title={isCauses?'Principales causas de defunción':`${source.label} por año de registro`}
  summary={isCauses?'Cinco grupos de causas del tabulado nacional de 2024.':'Serie nacional de 2020 a 2024. El color oscuro identifica el periodo seleccionado.'}
  option={{
   grid:{left:12,right:18,top:16,bottom:14,containLabel:true},
   tooltip:{trigger:'axis',confine:true,valueFormatter:v=>format.format(Number(v))},
   xAxis:isCauses?{type:'value',axisLabel:{hideOverlap:true}}:{type:'category',data:annualCounts.map(([y])=>String(y))},
   yAxis:isCauses?{type:'category',inverse:true,data:leadingCauses.map(([label])=>label),axisLabel:{width:105,overflow:'truncate'}}:{type:'value',axisLabel:{hideOverlap:true}},
   series:[{type:'bar',barMaxWidth:32,data:isCauses?leadingCauses.map(([,n])=>n):annualCounts.map(([y,n])=>({value:n,itemStyle:{color:y===selectedYear?'#15576b':'#54a6a6'}})),itemStyle:{color:'#167c80'}}],
  }}/></div>}
 <section className="panel prose">
  <span className="eyebrow">{source.agency} · SERIE DE REGISTROS</span>
  <h2>{isCauses?'Cinco principales causas de defunción en 2024':isAtlas?'Defunciones por residencia habitual en 2024':`${source.label} en México`}</h2>
  <p>{isCauses?'Grupos de causas del tabulado nacional. Los cruces por código CIE-10 están disponibles en la edición local.'
   :isAtlas?'Selecciona una entidad en el mapa para consultar su conteo. El total nacional incluye residencia en el extranjero y residencia sin especificar.'
   :`Serie nacional por año de registro. En ${selectedYear} se contabilizaron ${format.format(total)} registros.`}</p>
  {isAtlas&&selectedName&&<p aria-live="polite"><strong>{selectedName} · {format.format(stateDeaths[state])}</strong></p>}
  <div className="table-scroll"><table>
   <thead><tr><th scope="col">{isCauses?'Grupo de causas':isAtlas?'Residencia habitual':'Año de registro'}</th><th scope="col">Registros</th></tr></thead>
   <tbody>{rows.map(([label,count])=><tr key={label}><th scope="row">{label}</th><td>{format.format(count)}</td></tr>)}</tbody>
  </table></div>
  {activeSource!=='panorama'&&<p>El Observatorio calculó un total por año a partir de los registros de Datos Abiertos de la Secretaría de Salud / DGIS. La cobertura depende de las unidades que reportaron. La publicación es independiente.</p>}
  <p>Fuente: <a href={source.url}>{activeSource==='panorama'?'INEGI, reporte definitivo EDR 2024':'Secretaría de Salud / DGIS, archivos anuales de Datos Abiertos'}</a>.</p>
 </section></>;
}
