import os; os.makedirs('gh',exist_ok=True); os.makedirs('art',exist_ok=True)
import json,re
a=open('app5.html',encoding='utf-8').read()
def rep(x,y,cnt=1):
    global a
    assert x in a, x[:80]
    a=a.replace(x,y,cnt)
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
useTiles(0);''')
rep('map.setMaxBounds(L.latLngBounds([37.38, 126.60], [37.73, 127.24]));','map.setMaxBounds(L.latLngBounds([37.30, 126.50], [37.80, 127.30]));')
# --- recalc: instant estimate, then OSRM road estimate
rep('''function recalc(){
  state.at = new Date(); state.sp = speedNow(state.at);
  CAFES.forEach((c,i) => state.est[i] = estimate(state.origin, c, state.sp));
  document.getElementById("whereT").textContent = state.label;
  document.getElementById("whereS").textContent = `${clock(state.at)} 출발 · ${state.sp.l} 기준 차량 예상`;
  renderAll();
}''','''let osrmRun = 0;
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
