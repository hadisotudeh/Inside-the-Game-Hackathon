"use strict";
const $ = id => document.getElementById(id);
const NS = "http://www.w3.org/2000/svg";
const xgFormatter = new Intl.NumberFormat("en-GB", {minimumFractionDigits:3, maximumFractionDigits:3, roundingMode:"trunc", useGrouping:false});
const formatXg = value => xgFormatter.format(value);
const colors = {home: "#2368ad", away: "#bd5929"};
let stream = null, match = null, shots = [], history = [], insights = [], count = 0;
let audience = "casual", filter = "all", running = false, loadVersion = 0, pendingAudience = null;
let lastUpdate = null, goalTimer;
let momentumTimer = null;
function scheduleMomentum() {
  if(momentumTimer!==null)return;
  momentumTimer=setTimeout(()=>{momentumTimer=null;drawMomentum();},100);
}
let teamLogos = {};
let selectedShotId = null;
let followLatestShot = true;
let currentPeriod = 1;
const channel = "BroadcastChannel" in window ? new BroadcastChannel("touchline-overlay") : null;
const send = (type, data) => channel?.postMessage({type, data});
function node(tag, attrs = {}, text = "") {
  const n = document.createElementNS(NS, tag);
  Object.entries(attrs).forEach(([k,v]) => n.setAttribute(k,v));
  if (text) n.textContent = text;
  return n;
}
function pitch(svg) {
  svg.replaceChildren();
  const g = node("g", {class:"pitch-line"});
  g.append(node("rect",{x:1,y:1,width:118,height:78,rx:0.5}),
    node("line",{x1:60,y1:1,x2:60,y2:79}),node("circle",{cx:60,cy:40,r:9.15}),
    node("circle",{cx:60,cy:40,r:.5}),
    node("rect",{x:1,y:18,width:18,height:44}),node("rect",{x:101,y:18,width:18,height:44}),
    node("rect",{x:1,y:30,width:6,height:20}),node("rect",{x:113,y:30,width:6,height:20}),
    node("circle",{cx:13,cy:40,r:.5}),node("circle",{cx:107,cy:40,r:.5}));
  svg.append(g);
}
function dateLabel(value) { return new Intl.DateTimeFormat("en-GB",{day:"numeric",month:"short",year:"numeric",timeZone:"UTC"}).format(new Date(value+"T00:00:00Z")); }
function clock(event) { return `${String(event.minute).padStart(2,"0")}:${String(event.second).padStart(2,"0")}`; }
function side(teamId) { return teamId === match?.home_team.id ? "home" : "away"; }

function attacksRight(teamId, period) {
  const homeRight = Number(period) % 2 === 1;
  return side(teamId)==="home" ? homeRight : !homeRight;
}
function toPitch(location, teamId, period) {
  if(!location || location.length<2)return null;
  return attacksRight(teamId,period) ? [...location] : [120-location[0],80-location[1],...location.slice(2)];
}
function periodName(period) { return ({1:"1st half",2:"2nd half",3:"Extra time, 1st half",4:"Extra time, 2nd half",5:"Shootout"})[period] || "Match"; }
function visiblePeriod() { return $("shotPeriod").value==="current" ? currentPeriod : $("shotPeriod").value==="all" ? null : Number($("shotPeriod").value); }
function periodShots() { const period=visiblePeriod();return shots.filter(s=>period===null||s.period===period); }

function teamNames(m) {
  $("matchDate").textContent = m.match_date ? dateLabel(m.match_date) : "2015/16";
  $("homeName").textContent = m.home_team.name; $("awayName").textContent = m.away_team.name;
  for (const [prefix, team] of [["home",m.home_team],["away",m.away_team]]) {
    $(prefix+"Short").textContent = team.name;
    $(prefix+"Legend").textContent = team.name;
    const logo=teamLogos[team.name], image=$(prefix+"Crest"), initial=$(prefix+"Initial");
    initial.textContent=team.name[0]; initial.hidden=false; image.hidden=true;
    const link=$(prefix+"CrestLink");
    link.setAttribute("aria-label",`${team.name} on Wikipedia`);
    if(logo){
      link.href=logo.wikipedia;
      image.onload=()=>{image.hidden=false;initial.hidden=true;};
      image.onerror=()=>{image.hidden=true;initial.hidden=false;};
      image.alt=`${team.name} crest`;image.src=logo.src;
      if(image.complete&&image.naturalWidth){image.hidden=false;initial.hidden=true;}
    }else{link.removeAttribute("href");image.removeAttribute("src");}
  }
  drawShots();
}
async function loadMatches() {
  const version = ++loadVersion;
  stop(); clearState(); $("play").disabled = true; $("retryFixtures").hidden=true;
  $("status").textContent = "Loading available fixtures…";
  $("match").replaceChildren(new Option("Loading fixtures…", ""));
  try {
    const response = await fetch("/matches");
    if (!response.ok) throw new Error("Could not load fixtures");
    const matches = await response.json();
    if (version !== loadVersion) return;
    $("match").replaceChildren(...matches.map(m => {
      const option = new Option(`${m.home_team.name} vs ${m.away_team.name} · ${dateLabel(m.match_date)}`,m.match_id);
      option.match = m; return option;
    }));
    if (!matches.length) throw new Error("No fixtures available");
    match = matches[0]; teamNames(match); $("play").disabled = false;
    $("status").textContent = "Choose a match, then start replay.";
  } catch (error) {
    if (version !== loadVersion) return;
    $("status").textContent = "StatsBomb fixtures unavailable. Check your connection and retry.";
    $("match").replaceChildren(new Option("StatsBomb unavailable", ""));
    $("retryFixtures").hidden=false;
  }
}
function stop() {
  stream?.close(); stream = null; running = false;
  $("play").textContent = count ? "Replay again" : "Start replay";
  $("liveBadge").textContent = "Stopped";
}
function clearState() {
  clearTimeout(momentumTimer); momentumTimer=null;
  shots = []; history = []; insights = []; count = 0; lastUpdate = null; selectedShotId=null;
  clearTimeout(goalTimer); $("goalFlash").hidden = true;
  currentPeriod=1; $("shotPeriod").value="current";
  followLatestShot=true; $("shotFramePanel").hidden=true; pitch($("shotFramePitch"));
  $("homeScore").textContent = $("awayScore").textContent = "0";
  $("homeXg").replaceChildren(document.createTextNode("0.000"),Object.assign(document.createElement("small"),{textContent:"xG"}));
  $("awayXg").replaceChildren(document.createTextNode("0.000"),Object.assign(document.createElement("small"),{textContent:"xG"}));
  $("homeShots").textContent = $("awayShots").textContent = "0 shots";
  $("clock").textContent = "00:00"; $("eventCount").textContent = "0 events";
  $("latestAction").textContent = "Waiting for kick-off";
  $("eventLabel").textContent = "No events yet";
  $("eventPlayer").textContent = "Event positions only";
  $("balanceLabel").textContent = "Waiting for kick-off";
  $("shotDetails").textContent = "Select a marker for the player, outcome and xG.";
  $("providerLabel").textContent = "Template commentary";
  pitch($("livePitch")); drawShots(); drawMomentum(); drawInsights(); send("reset",null);
}
function start() {
  if (!match) return;
  stop(); clearState(); running = true;
  $("play").textContent = "Stop replay"; $("liveBadge").textContent = "Replaying";
  $("status").textContent = "Connecting to the event stream…";
  const params = new URLSearchParams({speed:$("speed").value,insights:"true",audience});
  const connection = new EventSource(`/matches/${match.match_id}/stream?${params}`);
  stream = connection;
  const listen = (kind, handler) => connection.addEventListener(kind, e => {
    if (stream !== connection) return;
    try { handler(JSON.parse(e.data)); } catch (error) {
      stop(); $("status").textContent = "An update could not be displayed. Restart the replay.";
    }
  });
  listen("match", data => {match=data;teamNames(data);send("match",data);$("status").textContent="Replay in progress.";});
  listen("update", update);
  listen("insight", data => {insights.unshift(data); insights=insights.slice(0,8); drawInsights(); send("insight",data);});
  listen("complete", () => {stop(); clearTimeout(goalTimer); $("goalFlash").hidden=true; $("liveBadge").textContent="Full time";$("status").textContent="Full time. Select a shot to explore the chances.";send("complete",null);});
  connection.onerror = () => {
    if (stream !== connection) return;
    stop(); $("status").textContent = "Connection interrupted. Restart to begin a fresh replay; automatic reconnect is disabled.";
  };
}
function update(data) {
  lastUpdate = data; count++;
  const event = data.event, kind = event.type.name;
  $("clock").textContent = clock(event); $("eventCount").textContent = `${count.toLocaleString()} events`;
  $("latestAction").textContent = `${event.team?.name || "Match"} · ${kind}`;
  $("eventLabel").textContent = `${clock(event)} / ${kind}`;
  $("eventPlayer").textContent = event.player?.name || `Period ${event.period} · event positions`;
  if(data.score) {
    $("homeScore").textContent = data.score[String(match.home_team.id)] || 0;
    $("awayScore").textContent = data.score[String(match.away_team.id)] || 0;
  }
  if(currentPeriod!==event.period){currentPeriod=event.period;drawShots();}
  pitch($("livePitch"));
  if (event.location?.length >= 2) {
    const [x,y] = toPitch(event.location,event.team?.id,event.period);
    const c = colors[side(event.team?.id)];
    const end=toPitch(data.end_location,event.team?.id,event.period);
    if(end)$("livePitch").append(node("line",{x1:x,y1:y,x2:end[0],y2:end[1],class:"event-trail",style:`stroke:${c}`}));
    $("livePitch").append(node("circle",{cx:x,cy:y,r:3,fill:c,opacity:.12}),node("circle",{cx:x,cy:y,r:1.15,class:"event-ball"}));
  }
  const point = {...data.momentum, minute:event.minute+event.second/60, team_id:event.team?.id};
  history.push(point); scheduleMomentum();
  const m=data.momentum;
  $("balanceLabel").textContent = m.net_difference!=null ? `Net xT difference: ${m.net_difference>=0?"+":""}${m.net_difference.toFixed(3)}` : "Incomplete half: movement coordinates missing";
  if (data.shot_added && !shots.some(s=>s.event_id===data.shot_added.event_id)) {
    shots.push(data.shot_added); drawShots(); scheduleMomentum();
    if(followLatestShot)selectShot(data.shot_added,false);
    if(data.shot_added.outcome==="Goal") {$("goalFlash").hidden=false;clearTimeout(goalTimer);goalTimer=setTimeout(()=>$("goalFlash").hidden=true,1800);}
  }
  send("update",{event,score:data.score});
}
function selectShot(shot, inspect=true) {
  if(inspect){
    followLatestShot=false;
    if(visiblePeriod()!==null && visiblePeriod()!==shot.period){$("shotPeriod").value=String(shot.period);drawShots();}
  }
  renderShotFrame(shot);
  selectedShotId=shot.event_id;
  document.querySelectorAll('.shot-marker').forEach(marker=>{
    const selected=marker.dataset.eventId===selectedShotId;
    marker.classList.toggle('selected',selected);marker.setAttribute('aria-pressed',String(selected));
  });
  const team = side(shot.team_id)==="home" ? match.home_team : match.away_team;
  $("shotDetails").textContent = `${periodName(shot.period)} · ${shot.minute}′ ${shot.player?.name || team.name} · ${shot.outcome || "Unknown outcome"} · ${shot.xg===null?"xG unavailable":formatXg(shot.xg)+" xG"}${shot.shootout?" · Shootout (excluded from totals)":""}`;
  if(inspect)$("shotDetails").scrollIntoView({block:"nearest",behavior:"smooth"});
}

function renderShotFrame(shot) {
  $("shotFramePanel").hidden=false;
  const svg=$("shotFramePitch");pitch(svg);
  const attack=colors[side(shot.team_id)],defend=colors[side(shot.team_id)==="home"?"away":"home"];
  $("frameAttackKey").style.background=attack;$("frameDefendKey").style.background=defend;
  $("shotFrameCaption").textContent=`${periodName(shot.period)} · ${clock(shot)} · ${shot.player?.name || "Shot"} · ${shot.outcome || "Outcome unavailable"} · Attacking ${attacksRight(shot.team_id,shot.period)?"right →":"left ←"}`;
  $("followShot").textContent=followLatestShot?"Following latest shot":"Follow latest shot";
  $("followShot").setAttribute("aria-pressed",String(followLatestShot));
  const frame=shot.freeze_frame || [];
  $("shotFrameEmpty").hidden=frame.length>0;
  if(!frame.length)return;
  const shooterId=shot.player?.id;
  const entries=frame.filter(p=>!shooterId || p.player?.id!==shooterId);
  if(shot.location?.length>=2)entries.push({location:shot.location,player:shot.player,teammate:true,shooter:true});
  if(shot.location?.length>=2&&shot.end_location?.length>=2) {
    const start=toPitch(shot.location,shot.team_id,shot.period),end=toPitch(shot.end_location,shot.team_id,shot.period);
    svg.append(node("line",{x1:start[0],y1:start[1],x2:end[0],y2:end[1],class:"frame-shot-path"}));
  }
  entries.forEach(p=>{
    if(!p.location || p.location.length<2)return;
    const [x,y]=toPitch(p.location,shot.team_id,shot.period);
    const color=p.teammate===true?attack:p.teammate===false?defend:"#627079";
    const name=p.player?.name || "Unidentified player";
    const role=p.shooter?"Shooter":p.goalkeeper?"Goalkeeper":p.teammate===true?"Teammate":"Opponent";
    const marker=node("g",{class:"frame-player",tabindex:0,"aria-label":`${name}, ${role}`,role:"img"});
    if(p.shooter) {
      marker.append(node("circle",{cx:x,cy:y,r:2.8,fill:"none",stroke:color,"stroke-width":.6}),node("circle",{cx:x,cy:y,r:1.8,fill:color,stroke:"white","stroke-width":.45}));
    }else if(p.goalkeeper){
      marker.append(node("rect",{x:x-1.7,y:y-1.7,width:3.4,height:3.4,rx:.35,fill:color,stroke:"white","stroke-width":.45}));
    }else{
      marker.append(node("circle",{cx:x,cy:y,r:1.7,fill:color,stroke:"white","stroke-width":.45}));
    }
    marker.append(node("title",{},`${name} · ${role}`));
    const labelWidth=Math.min(66,Math.max(18,name.length*1.35));
    const labelX=Math.max(1,Math.min(119-labelWidth,x-labelWidth/2));
    const labelY=y<12?y+4:y-8;
    const label=node("g",{class:"frame-player-label","aria-hidden":"true"});
    label.append(node("rect",{x:labelX,y:labelY,width:labelWidth,height:5.5,rx:.7}),node("text",{x:labelX+labelWidth/2,y:labelY+3.8,"text-anchor":"middle"},name));
    marker.append(label);
    marker.addEventListener("mouseenter",()=>svg.append(marker));
    svg.append(marker);
  });
}
$("followShot").onclick=()=>{
  followLatestShot=true; $("shotPeriod").value="current"; drawShots();
  if(shots.length)selectShot(shots[shots.length-1],false);
};

function drawShots() {
  pitch($("shotPitch"));
  const period=visiblePeriod(),visible=periodShots();
  const plotted=visible.filter(s=>filter==="all"||side(s.team_id)===filter);
  $("shotEmpty").hidden=plotted.some(s=>s.location?.length>=2);
  $("shotEmpty").textContent="No shots to show for this period and team yet.";
  $("shotPeriodLabel").textContent=period===null?"Whole-match positions; ends change at halftime":periodName(period);
  $("shotDirections").textContent=period===null?"Attacking ends follow each shot’s period":`${match?.home_team.name||"Home"} ${attacksRight(match?.home_team.id,period)?"→":"←"} · ${match?.away_team.name||"Away"} ${attacksRight(match?.away_team.id,period)?"→":"←"}`;
  if(match)for(const [prefix,team] of [["home",match.home_team],["away",match.away_team]]){
    const attempts=visible.filter(s=>s.team_id===team.id&&!s.shootout);
    const xg=attempts.reduce((sum,s)=>sum+(s.xg||0),0);
    $(prefix+"Xg").firstChild.textContent=formatXg(xg);
    $(prefix+"Shots").textContent=`${attempts.length} shot${attempts.length===1?"":"s"}`;
  }
  visible.filter(s=>filter==="all"||side(s.team_id)===filter).forEach(s=>{
    if(!s.location || s.location.length<2) return;
    const color=colors[side(s.team_id)], goal=s.outcome==="Goal";
    const location=toPitch(s.location,s.team_id,s.period);
    const marker=node("circle",{cx:location[0],cy:location[1],r:1.1+Math.sqrt(s.xg||0)*4,
      fill:goal?color:"#f4f7f3",stroke:color,class:`shot-marker${s.event_id===selectedShotId?" selected":""}`,tabindex:0,role:"button",
      "aria-pressed":String(s.event_id===selectedShotId),"data-event-id":s.event_id,
      "aria-label":`${s.minute} minute, ${s.player?.name||"Player"}, ${s.outcome}, ${s.xg==null?"unknown":formatXg(s.xg)} xG`});
    marker.append(node("title",{},`${s.player?.name||"Player"} · ${s.outcome} · xG ${s.xg==null?"unknown":formatXg(s.xg)}`));
    marker.onclick=()=>selectShot(s);marker.onkeydown=e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();selectShot(s);}};
    $("shotPitch").append(marker);
  });
}
$("shotPeriod").onchange=drawShots;

function drawMomentum() {
  const svg=$("momentum");svg.replaceChildren();
  for(let i=0;i<=6;i++) svg.append(node("line",{x1:i*150,y1:4,x2:i*150,y2:146,stroke:"#e3e8e8","stroke-dasharray":"2 5"}));
  svg.append(node("line",{x1:0,y1:75,x2:900,y2:75,stroke:"#aebcbe","stroke-width":1}));
  const measured=history.filter(p=>Number.isFinite(p.net_difference));
  const max=Math.max(0.001,...measured.map(p=>Math.abs(p.net_difference)));
  const xAt=p=>Math.max(0,Math.min(900,p.minute*10));
  const yAt=value=>75-value/max*60;
  let previous=null;
  const curve=[], impulses={home:[],away:[]};
  history.forEach(p=>{
    if(!Number.isFinite(p.net_difference)){previous=null;return;}
    const x=xAt(p),y=yAt(p.net_difference);
    if(previous&&previous.period===p.period){
      const dt=Math.max(0,p.period_seconds-previous.period_seconds);
      let path=`M ${xAt(previous)} ${yAt(previous.net_difference)}`;
      // Bound sampling by visible distance, even for long gaps in the feed.
      const steps=Math.min(120,Math.max(1,Math.ceil(Math.abs(x-xAt(previous))*2)));
      for(let step=1;step<steps;step++){
        const elapsed=dt*step/steps;
        const px=xAt(previous)+(x-xAt(previous))*elapsed/dt;
        path+=` L ${px} ${yAt(previous.net_difference*2**(-elapsed/p.half_life_seconds))}`;
      }
      const before=previous.net_difference*2**(-dt/p.half_life_seconds);
      path+=` L ${x} ${yAt(before)} L ${x} ${y}`;
      curve.push(path);
    }
    if(Number.isFinite(p.action_value)&&p.action_value!==0){
      const before=p.net_difference-(p.team_id===match?.home_team.id?p.action_value:-p.action_value);
      impulses[side(p.team_id)].push(`M ${x} ${yAt(before)} L ${x} ${y}`);
    }
    previous=p;
  });
  // Three paths replace thousands of individual SVG nodes on every update.
  svg.append(node("path",{d:curve.join(" "),fill:"none",stroke:"#263f4a","stroke-width":1.6}));
  for(const team of ["home","away"])svg.append(node("path",{d:impulses[team].join(" "),fill:"none",stroke:colors[team],"stroke-width":2}));
  if(!measured.length){
    const seen=history.some(p=>p.source_values_seen>0);
    const message=!history.length?"Start replay to see attacking progression.":seen?"Movement coordinates missing in this half.":"Waiting for the first action.";
    svg.append(node("text",{x:450,y:56,"text-anchor":"middle",fill:"#627079","font-size":13},message));
  }
  // Dedicated home/away lanes keep shot identity independent of the net xT sign.
  shots.filter(s=>!s.shootout).forEach(s=>{
    const home=side(s.team_id)==="home", color=colors[home?"home":"away"];
    const xg=Number.isFinite(s.xg)?Math.max(0,Math.min(1,s.xg)):null;
    // Area grows linearly with xG; the minimum keeps low-xG shots selectable.
    const radius=Math.sqrt(25+119*(xg??0));
    const x=Math.max(radius,Math.min(900-radius,(s.minute+s.second/60)*10));
    const y=home?22:128;
    const label=`${clock(s)} · ${s.player?.name||"Shot"} · ${s.outcome||"Unknown outcome"} · ${xg===null?"xG unavailable":formatXg(s.xg)+" xG"}`;
    const marker=node("g",{class:"momentum-shot",transform:`translate(${x} ${y})`,
      tabindex:0,role:"button","aria-label":label,"data-event-id":s.event_id});
    marker.append(node("title",{},label),node("circle",{r:radius,fill:"white",stroke:color,"stroke-width":s.outcome==="Goal"?3:1.5}));
    const pattern=node("g",{transform:`scale(${radius/10})`,fill:"#263f4a",stroke:"#263f4a","stroke-width":.65,"aria-hidden":"true"});
    pattern.append(node("polygon",{points:"0,-4 3.8,-1.2 2.4,3.2 -2.4,3.2 -3.8,-1.2"}));
    for(let i=0;i<5;i++){
      const angle=(-90+i*72)*Math.PI/180;
      pattern.append(node("line",{x1:Math.cos(angle)*4,y1:Math.sin(angle)*4,x2:Math.cos(angle)*9,y2:Math.sin(angle)*9}));
    }
    marker.append(pattern);
    const inspect=()=>selectShot(s);
    marker.onclick=inspect;
    marker.onkeydown=e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();inspect();}};
    svg.append(marker);
  });
  svg.setAttribute("aria-label",measured.length?"Smoothed home-minus-away xT with a 15-second half-life; football markers show shots sized by xG, home above and away below":"xT momentum: waiting for a complete window");
}
function drawInsights() {
  if(!insights.length) {$("insightList").innerHTML='<div class="empty-insight"><div class="empty-rule" aria-hidden="true"></div><h3>No notes yet</h3><p>Start the replay. Notes will appear after shots, with a link to the chance behind each one.</p></div>';return;}
  $("insightList").replaceChildren(...insights.map(item=>{
    const article=document.createElement("article");article.className="insight";
    const meta=document.createElement("div");meta.className="insight-meta";
    const source=document.createElement("span");source.textContent=item.ai_generated?"Foundry":"Template";
    const stamp=document.createElement("span");const shot=shots.find(s=>s.event_id===item.as_of_event_id);stamp.textContent=shot?`${shot.minute}′`:"Note";
    meta.append(source,stamp);const text=document.createElement("p");text.textContent=item.text;
    const evidence=document.createElement("button");evidence.className="evidence";evidence.textContent="View shot →";
    evidence.onclick=()=>{if(shot){filter="all";document.querySelectorAll('[data-filter]').forEach(b=>{b.classList.toggle('active',b.dataset.filter==='all');b.setAttribute('aria-pressed',String(b.dataset.filter==='all'));});drawShots();selectShot(shot);}};
    article.append(meta,text,evidence);return article;
  }));
  const latest=insights[0];$("providerLabel").textContent=latest.ai_generated?"Generated with Microsoft Foundry":latest.fallback_reason?`Local fallback · ${latest.fallback_reason.replaceAll("_"," ")}`:"Template commentary · no model calls";
}
$("play").onclick=()=>{if(running){stop();$("status").textContent="Replay stopped. Starting again returns to kick-off.";}else start();};
$("reset").onclick=()=>{stop();clearState();$("liveBadge").textContent="Not started";$("status").textContent="Reset to kick-off.";};
$("retryFixtures").onclick=loadMatches;
$("match").onchange=()=>{stop();clearState();match=$("match").selectedOptions[0].match;teamNames(match);$("status").textContent="Match selected. Ready to replay.";};
$("speed").onchange=()=>{if(running){stop();$("status").textContent="Speed changed. Start a fresh replay to apply it.";}};
$("method").onclick=()=>{$("methodNote").hidden=!$("methodNote").hidden;$("method").setAttribute("aria-expanded",String(!$("methodNote").hidden));};
document.querySelectorAll('[data-filter]').forEach(button=>button.onclick=()=>{filter=button.dataset.filter;document.querySelectorAll('[data-filter]').forEach(b=>{b.classList.toggle('active',b===button);b.setAttribute('aria-pressed',String(b===button));});drawShots();});
function setAudience(value){audience=value;document.querySelectorAll('[data-audience]').forEach(b=>{b.classList.toggle('active',b.dataset.audience===value);b.setAttribute('aria-pressed',String(b.dataset.audience===value));});}
document.querySelectorAll('[data-audience]').forEach(button=>button.onclick=()=>{if(button.dataset.audience===audience)return;if(running){pendingAudience=button.dataset.audience;$("restartDialog").showModal();}else{setAudience(button.dataset.audience);if(count){clearState();$("status").textContent="Commentary style changed. Start a new replay to apply it.";}}});
$("cancelLens").onclick=()=>$("restartDialog").close();
$("confirmLens").onclick=()=>{setAudience(pendingAudience);$("restartDialog").close();start();};
if(channel)channel.onmessage=e=>{if(e.data.type==="hello"){send("reset",null);if(match)send("match",match);if(lastUpdate)send("update",{event:lastUpdate.event,score:lastUpdate.score});if(insights.length)send("insight",insights[0]);}};
window.addEventListener("pagehide",()=>{stream?.close();channel?.close();});
pitch($("livePitch"));pitch($("shotPitch"));drawMomentum();
async function initialize(){
  try{const r=await fetch("/static/assets/teams.json");if(r.ok)teamLogos=await r.json();}catch{}
  await loadMatches();
}
initialize();
