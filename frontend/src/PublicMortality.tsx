import type {GeoIndex} from './Atlas';
import type {ReactNode} from 'react';
import {Activity, ArrowUpRight, HeartPulse, ShieldCheck, SlidersHorizontal, Stethoscope} from 'lucide-react';
import Chart from './Chart';

const mortalitySource = 'https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2025/edr/EDR2024-def_RR.pdf';

// INEGI, EDR 2024, gráfica 1 y cuadros 1 y 2 (reporte 44/25).
const annualDeaths = [
 [2020, 1086743], [2021, 1122249], [2022, 847716], [2023, 799869], [2024, 819672],
] as const;
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
 const selectedYear=isAtlas||isCauses?2024:annualDeaths.find(([y])=>y===year)?.[0]??2024;
 const total=annualDeaths.find(([y])=>y===selectedYear)![1];
 const selectedName=geo?.states[state];
 const rows=isCauses?leadingCauses:isAtlas
  ? [...Object.entries(stateDeaths).map(([code,count])=>[geo?.states[code]??code,count] as const),...otherResidence]
  : annualDeaths;
 const cards=[
  ['panorama','Defunciones',HeartPulse],['egresos','Egresos institucionales',Stethoscope],
  ['urgencias','Urgencias',Activity],['lesiones','Lesiones',ShieldCheck],
 ] as const;
 return <>
 <section className="source-cards" aria-label="Fuentes del observatorio">
  {cards.map(([target,label,Icon])=><button key={target} className={target==='panorama'?'source-card selected':'source-card'} onClick={()=>navigate(target)}>
   <div><span className="card-symbol"><Icon size={19}/></span><ArrowUpRight size={16}/></div>
   <span className="card-label">{label}</span><strong>{target==='panorama'?format.format(total):'Sin publicar'}</strong>
   <small>{target==='panorama'?`${selectedYear} · INEGI`:'Disponible en la edición local'}</small>
  </button>)}
 </section>
 <section className="filters panel">
  <div className="filter-heading"><b><SlidersHorizontal size={17}/> Configura tu consulta</b></div>
  <div className="filter-grid">
   <label>Fuente<select value="defunciones" disabled><option value="defunciones">Defunciones · INEGI</option></select></label>
   <label>Periodo<select value={selectedYear} onChange={e=>onYear(Number(e.target.value))}>
    {(isAtlas||isCauses?annualDeaths.slice(-1):annualDeaths).map(([y])=><option key={y}>{y}</option>)}
   </select></label>
   {isAtlas&&<label>Entidad<select value={state} onChange={e=>onState(e.target.value)}>
    <option value="">México</option>{Object.entries(geo?.states??{}).map(([code,name])=><option key={code} value={code}>{code} · {name}</option>)}
   </select></label>}
  </div>
 </section>
 <div className="context-bar"><span>INEGI · Defunciones registradas · {selectedYear}</span><span>{isAtlas?'Residencia habitual':isCauses?'Grupos de causas nacionales':'Serie nacional anual'}</span></div>
 {children}
 {!isAtlas&&<div className="chart-grid"><Chart wide kicker="DEFUNCIONES REGISTRADAS · INEGI"
  title={isCauses?'Principales causas de defunción':'Defunciones por año de registro'}
  summary={isCauses?'Cinco grupos de causas del tabulado nacional de 2024.':'Serie nacional de 2020 a 2024. El color oscuro identifica el periodo seleccionado.'}
  option={{
   grid:{left:12,right:18,top:16,bottom:14,containLabel:true},
   tooltip:{trigger:'axis',confine:true,valueFormatter:v=>format.format(Number(v))},
   xAxis:isCauses?{type:'value',axisLabel:{hideOverlap:true}}:{type:'category',data:annualDeaths.map(([y])=>String(y))},
   yAxis:isCauses?{type:'category',inverse:true,data:leadingCauses.map(([label])=>label),axisLabel:{width:105,overflow:'truncate'}}:{type:'value',axisLabel:{hideOverlap:true}},
   series:[{type:'bar',barMaxWidth:32,data:isCauses?leadingCauses.map(([,n])=>n):annualDeaths.map(([y,n])=>({value:n,itemStyle:{color:y===selectedYear?'#15576b':'#54a6a6'}})),itemStyle:{color:'#167c80'}}],
  }}/></div>}
 <section className="panel prose">
  <span className="eyebrow">INEGI · ESTADÍSTICAS DE DEFUNCIONES REGISTRADAS</span>
  <h2>{isCauses?'Cinco principales causas de defunción en 2024':isAtlas?'Defunciones por residencia habitual en 2024':'Defunciones registradas en México'}</h2>
  <p>{isCauses?'Grupos de causas del tabulado nacional. Los cruces por código CIE-10 están disponibles en la edición local.'
   :isAtlas?'Selecciona una entidad en el mapa para consultar su conteo. El total nacional incluye residencia en el extranjero y residencia sin especificar.'
   :`Serie nacional por año de registro. En ${selectedYear} se registraron ${format.format(total)} defunciones.`}</p>
  {isAtlas&&selectedName&&<p aria-live="polite"><strong>{selectedName} · {format.format(stateDeaths[state])}</strong></p>}
  <div className="table-scroll"><table>
   <thead><tr><th scope="col">{isCauses?'Grupo de causas':isAtlas?'Residencia habitual':'Año de registro'}</th><th scope="col">Defunciones registradas</th></tr></thead>
   <tbody>{rows.map(([label,count])=><tr key={label}><th scope="row">{label}</th><td>{format.format(count)}</td></tr>)}</tbody>
  </table></div>
  <p>Fuente: <a href={mortalitySource}>INEGI, reporte definitivo EDR 2024</a>.</p>
 </section></>;
}
