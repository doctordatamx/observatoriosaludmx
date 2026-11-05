import {useEffect,useRef} from 'react';
import * as echarts from 'echarts/core';
import type {EChartsOption} from 'echarts';
import {LineChart,BarChart} from 'echarts/charts';
import {GridComponent,TooltipComponent,LegendComponent} from 'echarts/components';
import {SVGRenderer} from 'echarts/renderers';
import {ArrowDownToLine} from 'lucide-react';

echarts.use([LineChart,BarChart,GridComponent,TooltipComponent,LegendComponent,SVGRenderer]);

export default function Chart({title,kicker,option,summary,footer,wide=false}:{title:string;kicker:string;option:EChartsOption;summary:string;footer?:string;wide?:boolean}){
 const el=useRef<HTMLDivElement>(null);const chart=useRef<echarts.EChartsType|null>(null);
 useEffect(()=>{if(!el.current)return;chart.current=echarts.init(el.current,undefined,{renderer:'svg'});const ro=new ResizeObserver(()=>chart.current?.resize());ro.observe(el.current);return()=>{ro.disconnect();chart.current?.dispose();};},[]);
 useEffect(()=>{const {media, ...options} = option;
  chart.current?.setOption(media?{baseOption:options,media}:options,true);},[option]);
 return <section className={`panel ${wide?'wide':''}`}><div className="panel-head"><div><span className="eyebrow">{kicker}</span><h3>{title}</h3></div><button className="icon-button" aria-label={`Descargar ${title} como SVG`} title="Descargar SVG" onClick={()=>{const svg=chart.current?.getDataURL({type:'svg',backgroundColor:'#fff'});if(svg){const a=document.createElement('a');a.href=svg;a.download=`${title}.svg`;a.click();}}}><ArrowDownToLine size={17}/></button></div><div ref={el} className="chart" role="img" aria-label={summary}/><p className="chart-note">{summary}{footer&&<><br/>{footer}</>}</p></section>;
}
