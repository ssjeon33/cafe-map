import os; os.makedirs('gh',exist_ok=True); os.makedirs('art',exist_ok=True)
import json,re
a=open('app5.html',encoding='utf-8').read()
def rep(x,y,cnt=1):
    global a
    assert x in a, x[:80]
    a=a.replace(x,y,cnt)
# --- vector map libs (self-hosted in vendor/)
rep('<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>',
 '<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>\n<link rel="stylesheet" href="vendor/maplibre-gl.css">\n<script src="vendor/maplibre-gl.js"></script>\n<script src="vendor/leaflet-maplibre-gl.js"></script>')
# --- CSS: tiles pastel filter + attribution
rep('.leaflet-control-attribution{display:none}',
 '.leaflet-tile-pane{filter:var(--tilef)}\n.leaflet-bottom.leaflet-right{bottom:calc(var(--peek) + var(--sab))}\n.leaflet-control-attribution{font-size:10px;background:var(--glass)!important}')
# --- modal: GPS option first + help text
rep('<button type="button" class="opt" id="useHome">',
 '<button type="button" class="opt" id="useGps"><span class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="12" r="4"></circle><path d="M12 2v3M12 19v3M2 12h3M19 12h3"></path></svg></span><span class="tx"><b>현재 위치 (GPS)</b><small>움직이면 자동으로 다시 계산해요</small></span></button>\n    <button type="button" class="opt" id="useHome">')
rep('이 링크에서는 GPS를 쓸 수 없어 출발지를 직접 골라요. 고른 곳은 다음에도 기억해요.','처음엔 GPS로 현재 위치를 잡아요. 다른 곳에서 출발하려면 여기서 고르면 되고, 고른 곳은 다음에도 기억해요.')
# --- speed model: add OSRM multiplier
rep('if (wk) return (h >= 10 && h < 21) ? { v:24, l:"주말 낮" } : { v:31, l:"주말 한산" };','if (wk) return (h >= 10 && h < 21) ? { v:24, l:"주말 낮", m:1.35 } : { v:31, l:"주말 한산", m:1.15 };')
rep('if (h >= 7 && h < 10) return { v:18, l:"출근 시간" };','if (h >= 7 && h < 10) return { v:18, l:"출근 시간", m:1.6 };')
rep('if (h >= 17 && h < 20) return { v:17, l:"퇴근 시간" };','if (h >= 17 && h < 20) return { v:17, l:"퇴근 시간", m:1.7 };')
rep('if (h >= 10 && h < 17) return { v:23, l:"평일 낮" };','if (h >= 10 && h < 17) return { v:23, l:"평일 낮", m:1.35 };')
rep('if (h >= 20 && h < 23) return { v:27, l:"저녁" };','if (h >= 20 && h < 23) return { v:27, l:"저녁", m:1.25 };')
rep('return { v:34, l:"심야" };','return { v:34, l:"심야", m:1.1 };')
# --- map: custom basemap into a group, tiles on top
rep('const map = L.map("map", { zoomControl:false, attributionControl:false, minZoom:10, maxZoom:17, zoomSnap:0.5, preferCanvas:false });\n',
 'const map = L.map("map", { zoomControl:false, attributionControl:true, minZoom:10, maxZoom:18, zoomSnap:0.5, preferCanvas:false });\nmap.attributionControl.setPrefix(false);\nconst baseGroup = L.layerGroup().addTo(map);\n')
rep('fillOpacity:1 }, interactive:false }).addTo(map)));\nconst dongLayer','fillOpacity:1 }, interactive:false }).addTo(baseGroup)));\nconst dongLayer')
rep('{ style:{ color:MAPC[theme].dong, weight:.8, fill:false }, interactive:false }).addTo(map);','{ style:{ color:MAPC[theme].dong, weight:.8, fill:false }, interactive:false }).addTo(baseGroup);')
rep('lineCap:"round", lineJoin:"round" }, interactive:false }).addTo(map);\n  L.marker([37.552, 126.875], { icon:L.divIcon({ className:"", html:\'<div class="lbl-han">한강</div>\', iconSize:null }), interactive:false }).addTo(map);',
    'lineCap:"round", lineJoin:"round" }, interactive:false }).addTo(baseGroup);\n  L.marker([37.552, 126.875], { icon:L.divIcon({ className:"", html:\'<div class="lbl-han">한강</div>\', iconSize:null }), interactive:false }).addTo(baseGroup);')
rep('''function labelsByZoom(){
  const z = map.getZoom();''','''let tilesOk = false;
function labelsByZoom(){
  const z = map.getZoom();
  if (tilesOk){ if (map.hasLayer(guGroup)) map.removeLayer(guGroup); if (map.hasLayer(dongGroup)) map.removeLayer(dongGroup); return; }''')
rep('map.on("zoomend", labelsByZoom);','''map.on("zoomend", labelsByZoom);
/* 실제 지도 타일 (키 없음): OSM → 안 되면 Esri → 둘 다 안 되면 자체 지도 */
const TILES = [
  { url:"https://tile.openstreetmap.org/{z}/{x}/{y}.png", opt:{ maxZoom:19, attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' } },
  { url:"https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}", opt:{ maxZoom:19, attribution:'Tiles &copy; Esri' } }
];
let tileLayer = null;
function useTiles(ix){
  if (tileLayer){ map.removeLayer(tileLayer); tileLayer = null; }
  if (ix >= TILES.length){ tilesOk = false; if (!map.hasLayer(baseGroup)) baseGroup.addTo(map); labelsByZoom(); return; }
  let errs = 0, oks = 0;
  tileLayer = L.tileLayer(TILES[ix].url, TILES[ix].opt).addTo(map);
  tileLayer.bringToBack();
  tileLayer.on("tileload", () => { if (++oks === 3 && !tilesOk){ tilesOk = true; map.removeLayer(baseGroup); labelsByZoom(); } });
  tileLayer.on("tileerror", () => { if (++errs >= 4 && oks < 3) useTiles(ix + 1); });
}
/* 벡터 지도(MapLibre + OpenFreeMap): 테마 색으로 직접 칠하고 지하철역을 항상 표시. 안 되면 아래 이미지 타일로 대체 */
const GLC = {
  citrus:{ bg:"#f1faf8", land:"#f6fbfa", park:"#cfeedd", wood:"#c4e8d6", water:"#a8e2db", road:"#ffffff", roadCase:"#d3e6e2", major:"#ffe9c7", majorCase:"#f3cf94", bld:"#dcebe7", bldLine:"#c5dcd7", rail:"#b7c9c5", text:"#3f4e4c", sub:"#5f6e6b", halo:"#f7fcfb", waterText:"#1f8f84", stn:"#2b3a38", stnText:"#1d2b2a", civic:"#fbf3e4", bound:"#bfdcd6" },
  lavender:{ bg:"#f7f4ea", land:"#faf8f1", park:"#d6eadf", wood:"#cbe3d6", water:"#cddbf2", road:"#ffffff", roadCase:"#e0dae6", major:"#e6e0f5", majorCase:"#c7bfe2", bld:"#ebe6ee", bldLine:"#d9d2df", rail:"#c6c1d2", text:"#474b5f", sub:"#62667c", halo:"#faf8f3", waterText:"#4f6fa6", stn:"#34384a", stnText:"#262a3b", civic:"#f3ecdf", bound:"#d5cddc" }
};
let glLayer = null, glSrc = null;
function glStyle(k){
  const T = GLC[k] || GLC.citrus, st = JSON.parse(JSON.stringify(glSrc.raw));
  const drop = new Set(["natural_earth","building-3d","poi_r20","poi_r7","poi_transit","road_one_way_arrow","road_one_way_arrow_opposite","highway-shield-non-us","highway-shield-us-interstate","road_shield_us","road_area_pattern","airport"]);
  st.layers = st.layers.filter(l => !drop.has(l.id) && !/transit_rail/.test(l.id));
  st.sources = { openmaptiles:{ type:"vector", tiles:glSrc.tj.tiles.map(u => u.replace("https://", "ofm://")), minzoom:glSrc.tj.minzoom || 0, maxzoom:glSrc.tj.maxzoom || 14, attribution:'<a href="https://openfreemap.org" target="_blank" rel="noopener">OpenFreeMap</a> &copy; <a href="https://www.openmaptiles.org/" target="_blank" rel="noopener">OpenMapTiles</a> Data from <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>' } };
  st.glyphs = String(st.glyphs).replace("https://", "ofm://"); delete st.sprite;
  const ko = ["coalesce", ["get","name:ko"], ["get","name"]];
  st.layers.forEach(l => {
    const id = l.id; l.paint = l.paint || {}; l.layout = l.layout || {};
    if (l.type === "background") l.paint["background-color"] = T.bg;
    else if (l.type === "fill"){
      if (id === "water") l.paint = { "fill-color":T.water };
      else if (id === "building"){ l.paint = { "fill-color":T.bld, "fill-outline-color":T.bldLine }; l.minzoom = 14; }
      else if (/wood/.test(id)) l.paint = { "fill-color":T.wood, "fill-opacity":.7 };
      else if (id === "park" || /grass|pitch|track|cemetery/.test(id)) l.paint = { "fill-color":T.park, "fill-opacity":.75 };
      else if (/residential/.test(id)) l.paint = { "fill-color":T.land, "fill-opacity":.6 };
      else if (/hospital|school/.test(id)) l.paint = { "fill-color":T.civic, "fill-opacity":.6 };
      else l.paint = { "fill-color":T.land };
    } else if (l.type === "line"){
      if (/^waterway/.test(id)) l.paint["line-color"] = T.water;
      else if (id === "park_outline" || /rail_hatching/.test(id)) l.layout.visibility = "none";
      else if (/boundary/.test(id)) l.paint["line-color"] = T.bound;
      else if (/major_rail/.test(id)) l.paint["line-color"] = T.rail;
      else if (/aeroway/.test(id)) l.paint["line-color"] = T.roadCase;
      else if (/_casing$/.test(id)) l.paint["line-color"] = /motorway|trunk_primary/.test(id) ? T.majorCase : T.roadCase;
      else if (/motorway|trunk_primary/.test(id)) l.paint["line-color"] = T.major;
      else if (/path_pedestrian/.test(id)) l.paint["line-color"] = T.roadCase;
      else l.paint["line-color"] = T.road;
    } else if (l.type === "symbol"){
      l.layout["text-field"] = ko; l.layout["text-font"] = ["Noto Sans Regular"]; delete l.layout["icon-image"];
      l.paint = { "text-color":/water/.test(id) ? T.waterText : /label_(city|town|state|village|other)/.test(id) ? T.text : T.sub, "text-halo-color":T.halo, "text-halo-width":1.6 };
      if (id === "poi_r1") l.minzoom = 15;
    }
  });
  const stn = ["all", ["==", ["get","class"], "railway"], ["in", ["get","subclass"], ["literal", ["subway","station","light_rail","halt"]]]];
  st.layers.push(
    { id:"jss_stn", type:"circle", source:"openmaptiles", "source-layer":"poi", minzoom:10.5, filter:stn, paint:{ "circle-radius":["interpolate",["linear"],["zoom"],10.5,2.2,15,5], "circle-color":"#ffffff", "circle-stroke-color":T.stn, "circle-stroke-width":1.6 } },
    { id:"jss_stn_label", type:"symbol", source:"openmaptiles", "source-layer":"poi", minzoom:11.5, filter:stn, layout:{ "text-field":["concat", ko, "역"], "text-font":["Noto Sans Bold"], "text-size":["interpolate",["linear"],["zoom"],11.5,10.5,15,13], "text-anchor":"top", "text-offset":[0,0.7], "text-padding":3 }, paint:{ "text-color":T.stnText, "text-halo-color":"#ffffff", "text-halo-width":1.8 } }
  );
  return st;
}
async function useGL(){
  try{
    if (!window.maplibregl || !L.maplibreGL) throw new Error("no gl lib");
    const cv = document.createElement("canvas"); if (!(cv.getContext("webgl2") || cv.getContext("webgl"))) throw new Error("no webgl");
    const j = async u => { const r = await fetch(u); if (!r.ok) throw new Error(u + " " + r.status); return r.json(); };
    const [raw, tj] = await Promise.all([j("https://tiles.openfreemap.org/styles/liberty"), j("https://tiles.openfreemap.org/planet")]);
    if (!tj.tiles || !tj.tiles.length) throw new Error("no tiles");
    glSrc = { raw, tj };
    /* 타일을 메인 스레드에서 받아 워커에 넘긴다(일부 브라우저에서 워커 요청이 막히는 경우 대비) */
    maplibregl.addProtocol("ofm", async (p, ac) => { const r = await fetch(p.url.replace("ofm://", "https://"), { signal:ac.signal }); if (!r.ok) throw new Error("tile " + r.status); return { data:await r.arrayBuffer() }; });
    try{ await Promise.race([Promise.all([document.fonts.load('400 14px "Paperlogy"'), document.fonts.load('700 14px "Paperlogy"')]), new Promise(r => setTimeout(r, 2500))]); }catch(e){}
    map.createPane("glPane").style.zIndex = 150;
    glLayer = L.maplibreGL({ style:glStyle(theme), pane:"glPane", localIdeographFontFamily:"'Paperlogy','Apple SD Gothic Neo','Noto Sans KR',sans-serif" }).addTo(map);
    let done = false, timer = null, shown = 0;
    const fail = () => { if (done) return; done = true; glRestyle = null; try{ map.removeLayer(glLayer); }catch(e){} glLayer = null; useTiles(0); };
    /* 화면이 실제로 그려지는 동안에만 10초를 센다(백그라운드 탭에서는 지도가 멈춰 있으므로 기다린다) */
    const tick = () => { if (done) return; if (!document.hidden) shown++; if (shown >= 10) fail(); else timer = setTimeout(tick, 1000); };
    requestAnimationFrame(() => { timer = setTimeout(tick, 1000); });
    glLayer.getMaplibreMap().once("load", () => {
      if (done) return; done = true; clearTimeout(timer);
      tilesOk = true; if (map.hasLayer(baseGroup)) map.removeLayer(baseGroup); labelsByZoom();
    });
    glRestyle = k => { if (glLayer) glLayer.getMaplibreMap().setStyle(glStyle(k)); };
  }catch(e){ glRestyle = null; useTiles(0); }
}
useGL();''')
rep('map.setMaxBounds(L.latLngBounds([37.38, 126.60], [37.73, 127.24]));','map.setMaxBounds(L.latLngBounds([37.30, 126.50], [37.80, 127.30]));')
# --- recalc: instant estimate, then OSRM road estimate
rep('''function recalc(){
  state.at = new Date(); state.sp = speedNow(state.at);
  CAFES.forEach((c,i) => state.est[i] = estimate(state.origin, c, state.sp));
  document.getElementById("whereT").textContent = state.label;
  document.getElementById("whereS").textContent = `${clock(state.at)} 출발 · ${state.sp.l} 기준 차량 예상`;
  renderAll();
}''','''let homeReq = false;
async function homeTimes(){
  if (homeReq) return; homeReq = true;
  const c0 = LS.get("homeCache", null);
  if (c0 && c0.n === CAFES.length && Date.now() - c0.t < 14 * 86400000){ state.home = c0.dur; return; }
  const coords = [[HOME.lng,HOME.lat], ...CAFES.map(c => [c.lng, c.lat])].map(p => p[0].toFixed(5) + "," + p[1].toFixed(5)).join(";");
  let dur = null;
  for (const host of ["https://routing.openstreetmap.de/routed-car", "https://router.project-osrm.org"]){
    try{
      const r = await fetch(`${host}/table/v1/driving/${coords}?destinations=0&annotations=duration`);
      const d = await r.json();
      if (r.ok && d.code === "Ok"){ dur = d.durations.map(x => x[0]).slice(1); break; }
    }catch(e){}
  }
  if (!dur){ homeReq = false; return; }
  LS.set("homeCache", { t:Date.now(), n:CAFES.length, dur });
  state.home = dur; if (state.origin) renderAll();
}
let osrmRun = 0;
async function roadTimes(){
  const my = ++osrmRun, o = state.origin, at = state.at, sp = state.sp;
  const key = (Math.round(o.lat/0.003)*0.003).toFixed(3) + "," + (Math.round(o.lng/0.003)*0.003).toFixed(3);
  const c0 = LS.get("roadCache", null);
  let dur = null, dist = null;
  if (c0 && c0.k === key && c0.n === CAFES.length && Date.now() - c0.t < 6 * 3600000){ dur = c0.dur; dist = c0.dist; }
  else {
    const coords = [[o.lng,o.lat], ...CAFES.map(c => [c.lng, c.lat])].map(p => p[0].toFixed(5) + "," + p[1].toFixed(5)).join(";");
    for (const host of ["https://routing.openstreetmap.de/routed-car", "https://router.project-osrm.org"]){
      try{
        const r = await fetch(`${host}/table/v1/driving/${coords}?sources=0&annotations=duration,distance`);
        const d = await r.json();
        if (r.ok && d.code === "Ok"){ dur = d.durations[0].slice(1); dist = d.distances ? d.distances[0].slice(1) : []; break; }
      }catch(e){}
    }
    if (dur) LS.set("roadCache", { k:key, t:Date.now(), n:CAFES.length, dur, dist });
  }
  if (my !== osrmRun || !dur) return;
  CAFES.forEach((c,i) => {
    if (dur[i] == null) return;
    const min = Math.max(2, Math.round(dur[i] * sp.m / 60 + 1));
    state.est[i] = { km: hav(o, c), road: dist[i] != null ? dist[i] / 1000 : state.est[i].road, min, base: dur[i] };
  });
  state.road = true;
  document.getElementById("whereS").textContent = `${clock(at)} 출발 · ${sp.l} 도로 기준 차량 예상`;
  renderAll();
}
function recalc(){
  state.at = new Date(); state.sp = speedNow(state.at); state.road = false;
  homeTimes();
  CAFES.forEach((c,i) => state.est[i] = estimate(state.origin, c, state.sp));
  document.getElementById("whereT").textContent = state.label;
  document.getElementById("whereS").textContent = `${clock(state.at)} 출발 · ${state.sp.l} 기준 차량 예상`;
  renderAll();
  roadTimes();
}''')
# --- origin: GPS
rep('''function setOrigin(o, label, fit){''','''let watchId = null;
function stopGps(){ if (watchId != null && navigator.geolocation){ navigator.geolocation.clearWatch(watchId); watchId = null; } }
function startGps(manual){
  if (!("geolocation" in navigator)){ if (manual) toast("이 브라우저는 위치를 지원하지 않아요"); return; }
  stopGps();
  let first = true;
  watchId = navigator.geolocation.watchPosition(p => {
    const o = { lat:p.coords.latitude, lng:p.coords.longitude };
    if (first){ first = false; setOrigin(o, "현재 위치", true, true); return; }
    if (state.label === "현재 위치" && hav(state.origin, o) > 0.3){ state.origin = o; LS.set("origin", { o, label:"현재 위치" }); drawMe(); recalc(); }
  }, err => {
    stopGps();
    if (manual) toast(err.code === 1 ? "위치 권한이 꺼져 있어요. 브라우저 설정에서 허용해 주세요" : "위치를 찾지 못했어요");
  }, { enableHighAccuracy:true, maximumAge:30000, timeout:12000 });
}
function setOrigin(o, label, fit, keepGps){
  if (!keepGps) stopGps();''')
rep('document.getElementById("useHome").addEventListener("click", () => { closeW();','document.getElementById("useGps").addEventListener("click", () => { closeW(); startGps(true); });\ndocument.getElementById("useHome").addEventListener("click", () => { closeW();')
rep('''const saved = LS.get("origin", null);
if (saved && saved.o) setOrigin(saved.o, saved.label); else setOrigin({ lat:HOME.lat, lng:HOME.lng }, HOME.name);''','''const saved = LS.get("origin", null);
if (saved && saved.o) setOrigin(saved.o, saved.label, true, true); else setOrigin({ lat:HOME.lat, lng:HOME.lng }, HOME.name, true, true);
if (!saved || saved.label === "현재 위치") startGps(false);''')
base=json.load(open('basemap.json'))
for g in base['gu']:
  n=g['n']
  if n.startswith('부천시'): n='부천 '+n[3:]
  else:
    m=re.match(r'^(.+시)(.+구)$',n)
    if m: n=m.group(2)
  g['n']=n
css=open('leaflet.css',encoding='utf-8').read()
d=open('cafes.json',encoding='utf-8').read()
out=a.replace('/*LEAFLETCSS*/',css).replace('/*CAFES*/[]',d).replace('/*BASE*/{}',json.dumps(base,ensure_ascii=False,separators=(',',':')))
open('gh/index.html','w',encoding='utf-8').write(out)
b=open('app5.html',encoding='utf-8').read()
for x,y in [
 ('<button type="button" class="opt" id="useHome">','<a class="opt" id="gpsLink" href="https://ssjeon33.github.io/cafe-map/" target="_blank" rel="noopener"><span class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="12" r="4"></circle><path d="M12 2v3M12 19v3M2 12h3M19 12h3"></path></svg></span><span class="tx"><b>현재 위치 (GPS)</b><small>GPS가 되는 주소로 새로 열어요</small></span></a>\n    <button type="button" class="opt" id="useHome">'),
 ('이 링크에서는 GPS를 쓸 수 없어 출발지를 직접 골라요. 고른 곳은 다음에도 기억해요.','이 claude.ai 링크에서는 GPS가 막혀 있어요. 위의 “현재 위치”를 누르거나 ssjeon33.github.io/cafe-map 주소로 열면 GPS로 바로 계산해요.'),
 ('.opt{display:flex;','.opt{text-decoration:none;color:inherit;display:flex;')]:
  assert x in b, x[:60]; b=b.replace(x,y,1)
open('art/index.html','w',encoding='utf-8').write(b.replace('/*LEAFLETCSS*/',css).replace('/*CAFES*/[]',d).replace('/*BASE*/{}',json.dumps(base,ensure_ascii=False,separators=(',',':'))))
print('built',len(out)//1024,'KB')
