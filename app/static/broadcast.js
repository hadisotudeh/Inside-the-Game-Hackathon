"use strict";
(() => {
  const stage=document.getElementById("analysis");
  function fitStage(){
    const scale=Math.min(window.innerWidth/1920,window.innerHeight/1080);
    stage.style.setProperty("--broadcast-scale",String(scale));
  }
  window.addEventListener("resize",fitStage);
  fitStage();
  function showLive(){document.querySelector(".broadcast-controls").open=false;}
  let playing=false;
  document.addEventListener("touchline:progress",()=>{if(!playing){playing=true;showLive();}});
  document.addEventListener("touchline:replay-reset",()=>{playing=false;});
  document.getElementById("play").addEventListener("click",()=>{
    if(document.getElementById("play").textContent==="Stop replay")showLive();
  });
})();
