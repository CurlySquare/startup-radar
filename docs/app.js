/* Startup Radar – Frontend
 * Liest die JSON-Dateien des Agenten und baut daraus Datenbank und Briefing.
 * Sicherheit: Alle Inhalte stammen aus dem Web (über das Sprachmodell). Deshalb wird
 * jeder Text escaped und jeder Link auf http(s) geprüft, bevor er in die Seite kommt.
 */
(function () {
  "use strict";

  const FIELDS = {
    retail: "Retail-Tech / Handel",
    food: "Food-Tech / Produktion",
    circular: "Kreislaufwirtschaft / Recycling",
    cloud_ai: "Cloud / Cyber Security / Data & AI",
    logistics: "Logistik & Supply Chain",
  };
  const MATURITY = ["", "Idee / Prototyp", "Pilotphase", "Marktreife", "Skalierung", "Etabliert"];
  const FIT = ["", "Kein Bezug", "Randbezug", "Sparten-Fit", "Kernprozess-Fit", "Konzern-Fit"];
  const MATURITY_LONG = [
    "Kein Produkt am Markt; Technologie oder Prototyp in Entwicklung (typisch Pre-Seed)",
    "Erstes Produkt, Pilot- oder Testkunden, noch kein belegter regulärer Umsatz (typisch Pre-Seed/Seed)",
    "Produkt am Markt mit zahlenden Kunden, frühes Wachstum (typisch Seed/Series A)",
    "Mehrere Märkte oder große Referenzkunden, Ausbau von Team und Vertrieb (typisch Series B/C)",
    "Breiter Kundenstamm in mehreren Ländern, erprobtes Geschäftsmodell (typisch Series C+)",
  ];
  const FIT_LONG = [
    "Kein Anwendungsfall in einer der fünf Sparten erkennbar",
    "Nur Unterstützungsfunktion (z. B. Personal, allgemeines Marketing) oder Nische, kein Kernprozess",
    "Konkreter Anwendungsfall in genau einer Sparte, z. B. in Filiale, Werk, Sortieranlage, Rechenzentrum oder Lager",
    "Kernprozess einer Sparte mit messbarem Nutzen (Kosten, Warenverfügbarkeit, Recyclingquote, Sicherheit), kurzfristig pilotierbar",
    "Nutzen in mindestens zwei Sparten oder als gemeinsame Plattform, skalierbar auf tausende Standorte, vereinbar mit europäischer Datensouveränität",
  ];
  const AREA_SHORT = { retail: "Handel", food: "Produktion", circular: "Kreislaufwirtschaft", cloud_ai: "Digital", logistics: "Logistik" };

  const $ = (id) => document.getElementById(id);
  const state = { startups: [], byId: {}, lastRun: null };

  // ---------- Hilfsfunktionen ----------
  function esc(value) {
    return String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }
  function safeUrl(url) {
    try {
      const u = new URL(url);
      return u.protocol === "https:" || u.protocol === "http:" ? u.href : null;
    } catch (e) { return null; }
  }
  function host(url) {
    try { return new URL(url).hostname.replace(/^www\./, ""); } catch (e) { return ""; }
  }
  function link(url, text) {
    const u = safeUrl(url);
    return u ? `<a href="${esc(u)}" target="_blank" rel="noopener noreferrer nofollow">${esc(text)}</a>` : esc(text);
  }
  function fmtDate(iso) {
    if (!iso) return "–";
    const d = new Date(iso + "T12:00:00");
    return d.toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit", year: "numeric" });
  }
  function dots(score, cls) {
    let html = `<span class="dots ${cls}" aria-hidden="true">`;
    for (let i = 1; i <= 5; i++) html += `<i class="${i <= score ? "on" : ""}"></i>`;
    return html + "</span>";
  }
  function scoreHtml(obj, cls, labels) {
    if (!obj) return "–";
    return `<span class="score" title="${esc(labels[obj.score])}">${dots(obj.score, cls)}<span>${obj.score}<span class="sr"> von 5</span></span></span>`;
  }
  function factValue(fact) {
    if (!fact || fact.value === null || fact.value === undefined) return '<span class="muted" title="nicht belegt">–</span>';
    const src = safeUrl(fact.source);
    return esc(fact.value) + (src ? ` <span class="src">${link(src, "Quelle ↗")}</span>` : "");
  }
  function nextMonday() {
    const d = new Date();
    const add = ((8 - d.getDay()) % 7) || 7;
    d.setDate(d.getDate() + add);
    return d.toLocaleDateString("de-DE", { weekday: "short", day: "2-digit", month: "2-digit" });
  }
  async function getJson(path) {
    const res = await fetch(path, { cache: "no-cache" });
    if (!res.ok) throw new Error(path + ": " + res.status);
    return res.json();
  }

  // ---------- Datenbank ----------
  function renderRow(s) {
    const isNew = state.lastRun && (state.lastRun.new || []).includes(s.id);
    const website = safeUrl(s.website);
    const areas = (s.fit && s.fit.areas || []).map((a) => AREA_SHORT[a] || a).join(", ");
    const history = (s.history || []).slice().reverse()
      .map((h) => `<li><time>${fmtDate(h.date)}</time>${esc(h.change)}</li>`).join("");
    const sources = (s.sources || []).map((u) => `<li>${link(u, host(u))}</li>`).join("");

    return `
<details class="row">
  <summary class="row-summary">
    <span class="row-name">${esc(s.name)}${isNew ? ' <span class="tag-new">neu</span>' : ""}</span>
    <span class="cell-field"><span class="chip">${esc(FIELDS[s.field] || s.field)}</span></span>
    <span><span class="cell-label">Land</span>${esc(s.country && s.country.value || "–")}</span>
    <span><span class="cell-label">Phase</span>${esc(s.funding_stage && s.funding_stage.value || "–")}</span>
    <span><span class="cell-label">Reifegrad</span>${scoreHtml(s.maturity, "", MATURITY)}</span>
    <span><span class="cell-label">Fit</span>${scoreHtml(s.fit, "fit", FIT)}</span>
  </summary>
  <div class="row-body">
    <div>
      <h4>Beschreibung</h4>
      <p>${factValue(s.description)}</p>
      <h4>Fakten</h4>
      <dl class="facts">
        <dt>Website</dt><dd>${website ? link(website, host(website)) : '<span class="muted">–</span>'}</dd>
        <dt>Land</dt><dd>${factValue(s.country)}</dd>
        <dt>Gegründet</dt><dd>${factValue(s.founded)}</dd>
        <dt>Finanzierung</dt><dd>${factValue(s.funding_stage)}</dd>
        <dt>Beschäftigte</dt><dd>${factValue(s.employees)}</dd>
        <dt>Im Radar seit</dt><dd>${fmtDate(s.first_seen)}</dd>
      </dl>
      ${s.startup_check ? `<h4>Startup-Prüfung</h4>
      <p class="small check">Nach EU-Definition (Empfehlung 2026/720) ✓<br>
        Alter: ${esc(s.startup_check.age)} · Eigenständigkeit: ${esc(s.startup_check.independent)} · Größe: ${esc(s.startup_check.size)}</p>` : ""}
      <h4>Alle Quellen</h4>
      <ul class="sources">${sources}</ul>
    </div>
    <div>
      <h4>Bewertung <span class="kicker">KI-Einschätzung</span></h4>
      <div class="rating">
        <div class="rating-head"><span>Reifegrad ${s.maturity ? s.maturity.score : "–"}/5 · ${esc(MATURITY[s.maturity && s.maturity.score] || "")}</span></div>
        <p>${esc(s.maturity && s.maturity.reason)}</p>
      </div>
      <div class="rating">
        <div class="rating-head"><span>Fit ${s.fit ? s.fit.score : "–"}/5 · ${esc(FIT[s.fit && s.fit.score] || "")}</span></div>
        ${areas ? `<p class="small">Sparten: ${esc(areas)}</p>` : ""}
        <p>${esc(s.fit && s.fit.reason)}</p>
      </div>
      <h4>Historie</h4>
      <ul class="history">${history}</ul>
    </div>
  </div>
</details>`;
  }

  function applyFilters() {
    const q = $("q").value.trim().toLowerCase();
    const field = $("f-field").value;
    const minM = +$("f-maturity").value;
    const minF = +$("f-fit").value;
    const sort = $("sort").value;

    let list = state.startups.filter((s) => {
      if (field && s.field !== field) return false;
      if (minM && (!s.maturity || s.maturity.score < minM)) return false;
      if (minF && (!s.fit || s.fit.score < minF)) return false;
      if (q) {
        const hay = [s.name, s.description && s.description.value, FIELDS[s.field], s.country && s.country.value,
          s.funding_stage && s.funding_stage.value, s.fit && s.fit.reason].join(" ").toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });

    const byName = (a, b) => a.name.localeCompare(b.name, "de");
    const sorters = {
      fit: (a, b) => (b.fit.score - a.fit.score) || (b.maturity.score - a.maturity.score) || byName(a, b),
      maturity: (a, b) => (b.maturity.score - a.maturity.score) || (b.fit.score - a.fit.score) || byName(a, b),
      recent: (a, b) => (b.last_updated || "").localeCompare(a.last_updated || "") || byName(a, b),
      name: byName,
    };
    list.sort(sorters[sort]);

    $("list").innerHTML = list.length ? list.map(renderRow).join("")
      : '<p class="empty">Keine Startups für diese Filter. <button class="btn-link" type="button" data-reset>Filter zurücksetzen</button></p>';
    $("count").textContent = `${list.length} von ${state.startups.length} Startups`;
  }

  function resetFilters() {
    $("q").value = ""; $("f-field").value = ""; $("f-maturity").value = "0"; $("f-fit").value = "0"; $("sort").value = "fit";
    applyFilters();
  }

  function setupControls() {
    $("f-field").insertAdjacentHTML("beforeend",
      Object.entries(FIELDS).map(([k, v]) => `<option value="${k}">${esc(v)}</option>`).join(""));
    ["q", "f-field", "f-maturity", "f-fit", "sort"].forEach((id) =>
      $(id).addEventListener(id === "q" ? "input" : "change", applyFilters));
    $("reset").addEventListener("click", resetFilters);
    $("list").addEventListener("click", (e) => { if (e.target.matches("[data-reset]")) resetFilters(); });
    $("legend-maturity").innerHTML = MATURITY_LONG.map((t, i) => `<li><strong>${i + 1} · ${esc(MATURITY[i + 1])}:</strong> ${esc(t)}</li>`).join("");
    $("legend-fit").innerHTML = FIT_LONG.map((t, i) => `<li><strong>${i + 1} · ${esc(FIT[i + 1])}:</strong> ${esc(t)}</li>`).join("");
  }

  // ---------- Briefing ----------
  // Mehrere Quellen derselben Website durchnummerieren: "eu-startups.com (1)", "(2)" …
  function sourceLinks(urls) {
    const count = {};
    urls.forEach((u) => { const h = host(u); count[h] = (count[h] || 0) + 1; });
    const seen = {};
    return urls.map((u) => {
      const h = host(u);
      seen[h] = (seen[h] || 0) + 1;
      return link(u, count[h] > 1 ? `${h} (${seen[h]})` : h);
    }).join(" · ");
  }
  function renderBriefing(b, open) {
    const top = b.top5.map((t) => {
      const s = state.byId[t.id];
      if (!s) return "";
      return `<li>
        <div class="top5-head"><strong>${esc(s.name)}</strong><span class="chip">${esc(FIELDS[s.field] || "")}</span>
        <span class="top5-scores">Fit ${s.fit.score}/5 · Reifegrad ${s.maturity.score}/5</span></div>
        <p>${esc(t.why)}</p></li>`;
    }).join("");
    const trends = b.trends.map((t) => `<div class="trend"><h4>${esc(t.title)}</h4><p>${esc(t.text)}</p>
      <div class="src-list">Quellen: ${sourceLinks(t.sources)}</div></div>`).join("");
    const st = b.stats || {};
    const body = `
      <p class="brief-meta">${esc(b.week)} · erstellt am ${fmtDate(b.date)} · ${st.new ?? 0} neu, ${st.updated ?? 0} mit neuer Finanzierungsphase · ${st.total ?? "–"} Startups gesamt</p>
      <div class="brief-grid">
        <div><h3>Top ${b.top5.length} der Woche</h3><ol class="top5">${top}</ol>
          <p class="small">Rangfolge per fester Regel: höchster Fit, dann Reifegrad, dann Anzahl der Quellen.</p></div>
        <div><h3>Beobachtete Trends</h3>${trends || '<p class="muted">Diese Woche keine belegten Trends.</p>'}</div>
      </div>`;
    return open ? body : `<details><summary>${esc(b.week)} · ${fmtDate(b.date)}</summary>${body}</details>`;
  }

  function setupBriefings(data) {
    const list = data.briefings || [];
    if (!list.length) { $("briefing-current").innerHTML = '<p class="muted">Noch kein Briefing vorhanden.</p>'; return; }
    $("briefing-current").innerHTML = renderBriefing(list[0], true);
    if (list.length > 1) {
      $("briefing-archive").innerHTML = `<div class="archive"><h3>Archiv</h3>${list.slice(1).map((b) => renderBriefing(b, false)).join("")}</div>`;
    }
  }

  // ---------- Start ----------
  async function init() {
    setupControls();
    $("stat-next").textContent = nextMonday();
    try {
      const [db, briefings] = await Promise.all([getJson("data/startups.json"), getJson("data/briefings.json")]);
      state.startups = (db.startups || []).filter((s) => s.fit && s.maturity);
      state.lastRun = db.last_run || null;
      state.startups.forEach((s) => {
        state.byId[s.id] = s;
        (s.aliases || []).forEach((a) => { state.byId[a] = s; });
      });
      $("stat-total").textContent = state.startups.length;
      $("stat-updated").textContent = fmtDate(db.updated);
      $("footer-stand").textContent = "Datenstand: " + fmtDate(db.updated);
      applyFilters();
      setupBriefings(briefings);
    } catch (e) {
      $("list").innerHTML = '<p class="empty">Die Daten konnten nicht geladen werden. Bitte später erneut versuchen.</p>';
      console.error(e);
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
