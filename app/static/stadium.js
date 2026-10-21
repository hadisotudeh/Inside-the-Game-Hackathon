"use strict";
// Grounds match the replay's 2015/16 season, including clubs that have since moved.
(() => {
  const background=document.getElementById("stadiumBackground");
  const credit=document.getElementById("stadiumCredit");
  const cache=new Map();
  let request=0, currentTeam=null;
  const grounds=fetch("/static/assets/stadiums.json").then(r=>{
    if(!r.ok)throw Error("Stadium list unavailable");
    return r.json();
  }).catch(()=>({}));
  const plainText=value=>new DOMParser().parseFromString(value||"","text/html").body.textContent.trim();
  async function wiki(params){
    const query=new URLSearchParams({action:"query",format:"json",formatversion:"2",origin:"*",...params});
    const response=await fetch(`https://en.wikipedia.org/w/api.php?${query}`,{signal:AbortSignal.timeout(10000)});
    if(!response.ok)throw Error("Stadium image unavailable");
    const data=await response.json();
    if(data.error)throw Error("Stadium image unavailable");
    return data.query?.pages?.[0];
  }
  async function findPhoto(stadium){
    const page=await wiki({titles:stadium,redirects:"1",prop:"pageimages",piprop:"name|thumbnail",pithumbsize:"1920",pilicense:"free"});
    if(!page?.pageimage||!page.thumbnail?.source)throw Error("No stadium photo");
    const file=await wiki({titles:`File:${page.pageimage}`,prop:"imageinfo",iiprop:"url|extmetadata",iiextmetadatafilter:"Artist|LicenseShortName|LicenseUrl|ImageDescription"});
    const info=file?.imageinfo?.[0], meta=info?.extmetadata;
    if(!info?.descriptionurl||!meta?.LicenseShortName?.value)throw Error("Missing image credit");
    const imageUrl=new URL(page.thumbnail.source), sourceUrl=new URL(info.descriptionurl);
    if(imageUrl.protocol!=="https:"||!imageUrl.hostname.endsWith(".wikimedia.org")||sourceUrl.protocol!=="https:")throw Error("Invalid photo URL");
    const artist=plainText(meta.Artist?.value)||"Wikimedia contributors";
    const license=plainText(meta.LicenseShortName.value);
    return {url:imageUrl.href,source:sourceUrl.href,stadium,artist,license};
  }
  async function showStadium(team){
    if(team===currentTeam)return;
    currentTeam=team;
    const version=++request;
    background.style.backgroundImage="none";
    background.classList.remove("loaded");
    credit.hidden=true;
    try{
      const stadium=(await grounds)[team];
      if(!stadium)return;
      if(!cache.has(stadium))cache.set(stadium,findPhoto(stadium).catch(error=>{cache.delete(stadium);throw error;}));
      const photo=await cache.get(stadium);
      const image=new Image();
      image.src=photo.url;
      await image.decode();
      if(version!==request)return;
      background.style.backgroundImage=`url(${JSON.stringify(photo.url)})`;
      background.classList.add("loaded");
      credit.href=photo.source;
      credit.textContent=`${stadium} · Photo: ${photo.artist} · ${photo.license} · Wikimedia`;
      credit.title="View the original photo, author and license. Background image is displayed at reduced opacity for readability.";
      credit.hidden=false;
    }catch{
      // Keep a neutral background when Wikimedia or the image is unavailable.
      if(version===request)currentTeam=null;
    }
  }
  document.addEventListener("touchline:match",event=>showStadium(event.detail.home_team.name));
})();
