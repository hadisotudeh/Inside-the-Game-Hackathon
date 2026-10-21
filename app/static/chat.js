"use strict";
(() => {
  const form=document.getElementById("chatForm"), input=document.getElementById("chatQuestion");
  const send=document.getElementById("chatSend"), reply=document.getElementById("chatReply");
  const status=document.getElementById("chatStatus");
  let context=null, controller=null, version=0;
  function clearChat(){
    version++;controller?.abort();controller=null;context=null;
    send.disabled=false;
    reply.replaceChildren();
    status.textContent="";
  }
  document.addEventListener("touchline:replay-reset",clearChat);
  document.addEventListener("touchline:context",event=>{context=event.detail;});
  async function ask(question){
    if(!context){status.textContent="Start the replay before asking a question.";return;}
    if(controller)return;
    const submitted=JSON.parse(JSON.stringify(context)), mode="simple";
    const token=++version;
    controller=new AbortController();send.disabled=true;
    reply.replaceChildren(Object.assign(document.createElement("p"),{className:"chat-asked",textContent:question}));
    status.textContent="Checking the match data…";
    try{
      const response=await fetch("/chat",{method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({question,mode,snapshot:submitted}),signal:controller.signal});
      const data=await response.json();
      if(token!==version)return;
      if(!response.ok)throw Error(typeof data.detail==="string"?data.detail:"Could not answer. Try again.");
      reply.append(Object.assign(document.createElement("p"),{textContent:data.text}));
      if(data.evidence?.length){
        const evidence=document.createElement("p");evidence.className="chat-evidence";
        evidence.textContent="Evidence: "+data.evidence.map(event=>`${event.minute}′ ${event.action}`).join(" · ");reply.append(evidence);
      }
      const stamp=`${String(submitted.clock.minute).padStart(2,"0")}:${String(submitted.clock.second).padStart(2,"0")}`;
      status.textContent=`Agent Framework + Gemini · ${mode==="simple"?"Casual fan":"Analyst"} · As of ${stamp}`;
      input.value="";
    }catch(error){if(token===version&&error.name!=="AbortError")status.textContent=error.message;}
    finally{if(token===version){controller=null;send.disabled=false;}}
  }
  form.addEventListener("submit",event=>{event.preventDefault();const question=input.value.trim();if(question)ask(question);});
  document.querySelectorAll("[data-question]").forEach(button=>button.addEventListener("click",()=>ask(button.dataset.question)));
})();
