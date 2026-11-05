import type {GeoIndex} from './Atlas';

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

export default function PublicMortality({view,geo,state}:{view:string;geo:GeoIndex|null;state:string}){
 const isAtlas=view==='atlas';
 const isCauses=view==='enfermedades';
 const selectedName=geo?.states[state];
 const rows=isCauses?leadingCauses:isAtlas
  ? [...Object.entries(stateDeaths).map(([code,count])=>[geo?.states[code]??code,count] as const),...otherResidence]
  : annualDeaths;
 return <section className="panel prose">
  <span className="eyebrow">INEGI · ESTADÍSTICAS DE DEFUNCIONES REGISTRADAS</span>
  <h2>{isCauses?'Cinco principales causas de defunción en 2024':isAtlas?'Defunciones por residencia habitual en 2024':'Defunciones registradas en México'}</h2>
  <p>{isCauses?'Grupos de causas del tabulado nacional. Los cruces por código CIE-10 están disponibles en la edición local.'
   :isAtlas?'Selecciona una entidad en el mapa para consultar su conteo. El total nacional incluye residencia en el extranjero y residencia sin especificar.'
   :'Serie nacional por año de registro. En 2024 se registraron 819,672 defunciones.'}</p>
  {isAtlas&&selectedName&&<p aria-live="polite"><strong>{selectedName} · {format.format(stateDeaths[state])}</strong></p>}
  <div className="table-scroll"><table>
   <thead><tr><th scope="col">{isCauses?'Grupo de causas':isAtlas?'Residencia habitual':'Año de registro'}</th><th scope="col">Defunciones registradas</th></tr></thead>
   <tbody>{rows.map(([label,count])=><tr key={label}><th scope="row">{label}</th><td>{format.format(count)}</td></tr>)}</tbody>
  </table></div>
  <p>Fuente: <a href={mortalitySource}>INEGI, reporte definitivo EDR 2024</a>.</p>
 </section>;
}
