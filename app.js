// emblemSvg() comes from emblems.js
let DATA = null;
let viewedDate = null;
const STORAGE_KEY = "tamilnal-prefs-v1";
const WEEKDAYS_TA = ["ஞாயிற்றுக்கிழமை","திங்கட்கிழமை","செவ்வாய்க்கிழமை","புதன்கிழமை","வியாழக்கிழமை","வெள்ளிக்கிழமை","சனிக்கிழமை"];

function loadPrefs() {
  try { const r = localStorage.getItem(STORAGE_KEY); if (r) return JSON.parse(r); } catch (e) {}
  return { categories: ["amman","ekadasi","pradosham"], leadDays: 1, notifsEnabled: false };
}
function savePrefs(p) { localStorage.setItem(STORAGE_KEY, JSON.stringify(p)); }
let prefs = loadPrefs();

function midnight(d) { const x = new Date(d); x.setHours(0,0,0,0); return x; }
function toStr(d) { return midnight(d).toLocaleDateString("en-CA"); }
function todayStr() { return toStr(new Date()); }
function daysBetween(aStr, bStr) { return Math.round((new Date(aStr+"T00:00:00") - new Date(bStr+"T00:00:00"))/86400000); }
function fmtGreg(ds) { return new Date(ds+"T00:00:00").toLocaleDateString("en-US",{month:"long",day:"numeric",year:"numeric"}); }
function emblemFor(d) { return (d && d.icon) ? d.icon : "generic"; }

function computeTamil(dateStr) {
  const anchors = (DATA.meta && DATA.meta.monthAnchors) || [];
  for (const a of anchors) {
    const diff = daysBetween(dateStr, a.startDate);
    if (diff >= 0 && diff < a.days) return { tamilMonth: a.tamilMonth, tamilDay: diff+1 };
  }
  return null;
}

function renderNiche(entry) {
  const niche = document.getElementById("niche");
  const credit = document.getElementById("photoCredit");
  if (entry && entry.photo) {
    // show the deity painting framed; keep emblem as instant fallback if the image fails
    niche.classList.add("has-photo");
    niche.innerHTML =
      '<div class="photo-frame">' +
      '<img class="deity-photo" src="' + entry.photo + '" alt="" ' +
      'onerror="this.closest(&quot;.niche&quot;).classList.remove(&quot;has-photo&quot;);this.closest(&quot;.niche&quot;).innerHTML=window.__emblemFallback||&quot;&quot;;" />' +
      '</div>';
    window.__emblemFallback = emblemSvg(emblemFor(entry));
    if (credit) credit.textContent = entry.photoCredit || "";
  } else {
    niche.classList.remove("has-photo");
    niche.innerHTML = emblemSvg(emblemFor(entry));
    if (credit) credit.textContent = "";
  }
}

function renderHeroForDate(dateStr) {
  const entry = DATA.days.find(d => d.date === dateStr);
  const dObj = new Date(dateStr+"T00:00:00");
  const tamil = computeTamil(dateStr);

  document.getElementById("tamilMonth").textContent = entry ? entry.tamilMonth : (tamil ? tamil.tamilMonth : "—");
  document.getElementById("tamilDay").textContent   = entry ? entry.tamilDay   : (tamil ? tamil.tamilDay   : "–");
  document.getElementById("weekday").textContent = (entry && entry.weekdayFull) ? entry.weekdayFull : WEEKDAYS_TA[dObj.getDay()];
  document.getElementById("gregorianDate").textContent = fmtGreg(dateStr);

  // panchangam strip — nakshatram + tithi (from computed data)
  const nakEl = document.getElementById("nakVal");
  const tithiEl = document.getElementById("tithiVal");
  if (nakEl) nakEl.textContent = entry && entry.nakshatra ? entry.nakshatra : "—";
  if (tithiEl) tithiEl.textContent = entry && entry.tithi ? entry.tithi : "—";

  const rel = daysBetween(dateStr, todayStr());
  const relEl = document.getElementById("relPill");
  if (rel === 0) relEl.textContent = "இன்று · Today";
  else if (rel === 1) relEl.textContent = "நாளை · Tomorrow";
  else if (rel === -1) relEl.textContent = "நேற்று · Yesterday";
  else if (rel > 1) relEl.textContent = rel + " நாட்களில் · in " + rel + " days";
  else relEl.textContent = (-rel) + " நாட்கள் முன் · " + (-rel) + " days ago";

  const tag = document.getElementById("confidenceTag");
  if (tag) tag.style.display = "none";   // badge removed entirely per design
  if (entry) {
    renderNiche(entry);
    document.getElementById("occasionTitle").textContent = entry.title || "";
    document.getElementById("occasionLine").innerHTML = (entry.oneLiner ? entry.oneLiner : "") + (entry.oneLinerEn ? '<span class="en">' + entry.oneLinerEn + '</span>' : "");
    // Daily-blessing days get a softer visual treatment
    document.getElementById("heroCard").classList.toggle("is-daily", !!entry.daily);
    renderStarChip(entry);
    renderTempleBtn(entry);
  } else {
    document.getElementById("niche").classList.remove("has-photo");
    document.getElementById("niche").innerHTML = emblemSvg("generic");
    var _cr = document.getElementById("photoCredit"); if (_cr) _cr.textContent = "";
    document.getElementById("occasionTitle").textContent = "—";
    document.getElementById("occasionLine").innerHTML = "";
    document.getElementById("heroCard").classList.remove("is-daily");
    document.getElementById("starChip").style.display = "none";
    document.getElementById("templeBtn").style.display = "none";
  }
  document.getElementById("todayBtn").style.display = (rel === 0) ? "none" : "inline-flex";
}

// Show the nakshatram's presiding deity as a small chip — but only when it's NOT already
// the main image (i.e. on festival days), so the star deity is never erased by a festival.
function renderStarChip(entry) {
  const chip = document.getElementById("starChip");
  const showable = entry.starImage && entry.starDeity && !entry.daily &&
                   entry.photo && entry.starImage !== entry.photo;
  if (!showable) { chip.style.display = "none"; return; }
  document.getElementById("starChipImg").innerHTML =
    '<img src="' + entry.starImage + '" alt="" loading="lazy">';
  document.getElementById("starChipNak").textContent = entry.nakshatra || "";
  document.getElementById("starChipDeity").textContent = entry.starDeity || "";
  chip.style.display = "inline-flex";
}

// Offer to find the nearest relevant temple via Google Maps (opens Maps; location handled there).
let _templeQuery = null;
function renderTempleBtn(entry) {
  const btn = document.getElementById("templeBtn");
  if (!entry.temple || !entry.temple.q) { btn.style.display = "none"; _templeQuery = null; return; }
  _templeQuery = entry.temple.q;
  document.getElementById("templeBtnLabel").textContent =
    "அருகில் " + (entry.temple.ta || "கோயில்") + " · Nearby " + (entry.temple.en || "temple");
  btn.style.display = "inline-flex";
}
function openTempleSearch() {
  if (!_templeQuery) return;
  const url = "https://www.google.com/maps/search/?api=1&query=" +
              encodeURIComponent(_templeQuery + " near me");
  window.open(url, "_blank", "noopener");
}

function shiftDate(delta) { const d = new Date(viewedDate); d.setDate(d.getDate()+delta); viewedDate = midnight(d); renderHeroForDate(toStr(viewedDate)); }
function goToday() { viewedDate = midnight(new Date()); renderHeroForDate(todayStr()); }
function jumpTo(ds) { if (!ds) return; viewedDate = new Date(ds+"T00:00:00"); renderHeroForDate(ds); closeSheet(); }

function renderUpcoming() {
  const list = document.getElementById("upcomingList"); list.innerHTML = "";
  const rows = DATA.days
    .filter(d => d.title && !d.daily && daysBetween(d.date, todayStr()) > 0)
    .filter(d => d.always || d.tags.some(t => prefs.categories.includes(t)) || prefs.categories.length === 0)
    .sort((a,b) => a.date.localeCompare(b.date)).slice(0,8);
  if (!rows.length) { list.innerHTML = '<li class="upcoming-item"><span class="up-text"><span class="up-title">விரைவில் நிகழ்வுகள் இல்லை</span><span class="up-sub">Nothing coming up in the loaded range.</span></span></li>'; return; }
  rows.forEach(d => {
    const n = daysBetween(d.date, todayStr());
    const whenTa = n === 1 ? "நாளை" : n + " நாட்களில்";
    const whenEn = n === 1 ? "tomorrow" : "in " + n + " days";
    const hi = d.confidence === "verified" && (d.tags.includes("ekadasi") || d.tags.includes("amavasai") || d.tags.includes("pournami"));
    const li = document.createElement("li");
    li.className = "upcoming-item" + (hi ? " hi" : "");
    li.tabIndex = 0; li.setAttribute("role","button");
    li.addEventListener("click", () => jumpTo(d.date));
    li.addEventListener("keydown", e => { if (e.key==="Enter"||e.key===" ") { e.preventDefault(); jumpTo(d.date); } });
    // Use the real deity photo as the thumbnail (falls back to emblem only if missing)
    const thumb = d.photo
      ? '<span class="up-thumb"><img src="' + d.photo + '" alt="" loading="lazy" onerror="this.parentNode.classList.add(&quot;is-emblem&quot;);this.parentNode.innerHTML=&quot;&quot;;"></span>'
      : '<span class="up-thumb is-emblem">' + emblemSvg(emblemFor(d)) + '</span>';
    const nakBit = d.nakshatra ? ('<span class="up-nak">' + d.nakshatra + '</span>') : '';
    li.innerHTML = thumb +
      '<span class="up-text">' +
        '<span class="up-title">' + d.title + '</span>' +
        '<span class="up-sub">' + fmtGreg(d.date) + nakBit + '</span>' +
      '</span>' +
      '<span class="up-when">' + whenTa + '<small>' + whenEn + '</small></span>';
    list.appendChild(li);
  });
}

function renderCategories() {
  const grid = document.getElementById("categoryGrid"); grid.innerHTML = "";
  DATA.eventCategories.forEach(cat => {
    const active = prefs.categories.includes(cat.id);
    const chip = document.createElement("button");
    chip.className = "category-chip" + (active ? " active" : "");
    chip.innerHTML = '<span class="chip-emblem">' + emblemSvg(cat.icon) + '</span><span class="chip-label">' + cat.label + '<span class="en">' + cat.labelEn + '</span></span>';
    chip.addEventListener("click", () => {
      if (prefs.categories.includes(cat.id)) prefs.categories = prefs.categories.filter(c => c !== cat.id);
      else prefs.categories.push(cat.id);
      savePrefs(prefs); chip.classList.toggle("active"); renderUpcoming();
    });
    grid.appendChild(chip);
  });
  document.getElementById("leadTime").value = String(prefs.leadDays);
}

function openSheet() { document.getElementById("settingsSheet").classList.add("open"); document.getElementById("sheetBackdrop").classList.add("open"); }
function closeSheet() { document.getElementById("settingsSheet").classList.remove("open"); document.getElementById("sheetBackdrop").classList.remove("open"); }

function updateNotifStatus() {
  const el = document.getElementById("notifStatus");
  if (!("Notification" in window)) { el.textContent = "இந்த சாதனத்தில் அறிவிப்புகள் ஆதரிக்கப்படவில்லை · Not supported here."; return; }
  if (Notification.permission === "granted" && prefs.notifsEnabled) el.textContent = "✓ அறிவிப்புகள் இயக்கத்தில் · Reminders are on.";
  else if (Notification.permission === "denied") el.textContent = "தடுக்கப்பட்டது — சாதன அமைப்புகளில் மாற்றவும் · Blocked in settings.";
  else el.textContent = "";
}
async function enableNotifications() {
  if (!("Notification" in window)) { updateNotifStatus(); return; }
  const p = await Notification.requestPermission();
  if (p === "granted") { prefs.notifsEnabled = true; savePrefs(prefs); new Notification("இன்று · Tamil Nal", { body: "நினைவூட்டல்கள் இயக்கப்பட்டன 🪔", icon: "icons/icon-192.png" }); }
  updateNotifStatus();
}

function wireSwipe() {
  const hero = document.getElementById("heroCard");
  let x0 = null, y0 = null;
  hero.addEventListener("touchstart", e => { x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }, {passive:true});
  hero.addEventListener("touchend", e => {
    if (x0 === null) return;
    const dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) shiftDate(dx < 0 ? 1 : -1);
    x0 = y0 = null;
  }, {passive:true});
}

async function init() {
  DATA = await (await fetch("data.json")).json();
  viewedDate = midnight(new Date());
  // header year labels from meta
  if (DATA.meta) {
    var yl = document.getElementById("tamilYearLabel");
    if (yl && DATA.meta.tamilYearFull) yl.textContent = DATA.meta.tamilYearFull;
    var kl = document.getElementById("yearLabel");
    if (kl && DATA.meta.kaliyugam) kl.textContent = "கலியுகம் " + DATA.meta.kaliyugam;
  }
  renderHeroForDate(todayStr());
  renderUpcoming(); renderCategories(); updateNotifStatus();

  document.getElementById("prevDay").addEventListener("click", () => shiftDate(-1));
  document.getElementById("nextDay").addEventListener("click", () => shiftDate(1));
  document.getElementById("todayBtn").addEventListener("click", goToday);
  var _tb = document.getElementById("templeBtn");
  if (_tb) _tb.addEventListener("click", openTempleSearch);
  document.getElementById("jumpDate").addEventListener("change", e => jumpTo(e.target.value));
  var _jb = document.getElementById("jumpBtn");
  if (_jb) _jb.addEventListener("click", function() {
    var inp = document.getElementById("jumpDate");
    if (inp.showPicker) { try { inp.showPicker(); } catch(e) { inp.focus(); } }
    else inp.focus();
  });
  document.getElementById("settingsBtn").addEventListener("click", openSheet);
  document.getElementById("closeSheet").addEventListener("click", closeSheet);
  document.getElementById("sheetBackdrop").addEventListener("click", closeSheet);
  document.getElementById("enableNotifs").addEventListener("click", enableNotifications);
  document.getElementById("leadTime").addEventListener("change", e => { prefs.leadDays = Number(e.target.value); savePrefs(prefs); });

  document.addEventListener("keydown", e => {
    if (e.target.tagName === "INPUT" || e.target.tagName === "SELECT") return;
    if (e.key === "ArrowLeft") shiftDate(-1);
    else if (e.key === "ArrowRight") shiftDate(1);
    else if (e.key === "t" || e.key === "T") goToday();
  });

  wireSwipe();
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(()=>{});
}
init();
