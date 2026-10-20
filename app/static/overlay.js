"use strict";
const $=id=>document.getElementById(id);
let match=null,logos={};
function setCrests(){
 for(const [side,team] of [["Home",match.home_team],["Away",match.away_team]]){
   const image=$("overlay"+side+"Crest"),logo=logos[team.name];
   image.hidden=true;image.onerror=()=>image.hidden=true;
   if(logo){image.alt=team.name+" crest";image.src=logo.src;image.hidden=false;}
 }
}
fetch("/static/assets/teams.json").then(r=>r.json()).then(data=>{logos=data;if(match)setCrests();}).catch(()=>{});
if("BroadcastChannel" in window){
  const channel=new BroadcastChannel("touchline-overlay");
  channel.onmessage=({data:{type,data}})=>{
    if(type==="reset"){$("overlayText").textContent="Following the match. Waiting for the next insight.";$("overlayScore").textContent="0 : 0";$("overlayClock").textContent="00:00";$("overlayProvider").textContent="OVERLAY PREVIEW · SAME BROWSER";$("overlayEvidence").textContent="Event-based replay";}
    if(type==="match"){match=data;setCrests();$("overlayHome").textContent=data.home_team.name;$("overlayAway").textContent=data.away_team.name;}
    if(type==="update"&&match){$("overlayScore").textContent=`${data.score?.[String(match.home_team.id)]||0} : ${data.score?.[String(match.away_team.id)]||0}`;$("overlayClock").textContent=`${String(data.event.minute).padStart(2,"0")}:${String(data.event.second).padStart(2,"0")}`;}
    if(type==="insight"){$("overlayText").textContent=data.text;$("overlayProvider").textContent=data.ai_generated?"MICROSOFT FOUNDRY · MATCH INSIGHT":"LOCAL TEMPLATE · MATCH INSIGHT";$("overlayEvidence").textContent=`Based on event ${data.as_of_event_id}`;}
    if(type==="complete")$("overlayClock").textContent="FT";
  };
  channel.postMessage({type:"hello"});
  window.addEventListener("pagehide",()=>channel.close());
}else $("overlayText").textContent="This browser does not support local overlay synchronization. Use the main matchroom.";
