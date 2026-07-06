from __future__ import annotations

import json
from pathlib import Path
from string import Template

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
XLSX_PATH = Path(r"P:\Atualização\Mercado\Juros\didol - novo_ticker.xlsx")
OUT_HTML = BASE_DIR / "curva_di_3d.html"
OUT_HTML_PAGES = BASE_DIR / "index.html"
SHEET_NAME = "Historico"


TENOR_YEARS = {
    "1 DIA": 0.0,
    "1M": 1 / 12,
    "2M": 2 / 12,
    "3M": 3 / 12,
    "6M": 6 / 12,
    "9M": 9 / 12,
    "1Y": 1.0,
    "2Y": 2.0,
    "3Y": 3.0,
    "4Y": 4.0,
    "5Y": 5.0,
    "6Y": 6.0,
    "7Y": 7.0,
    "8Y": 8.0,
    "9Y": 9.0,
    "10Y": 10.0,
}


def read_history() -> pd.DataFrame:
    raw = pd.read_excel(XLSX_PATH, sheet_name=SHEET_NAME, header=None, engine="openpyxl")
    headers = raw.iloc[1].astype(str).str.strip().tolist()
    data = raw.iloc[2:].copy()
    data.columns = headers
    data["Data"] = pd.to_datetime(data["Data"], errors="coerce")

    cols = ["Data"] + [c for c in TENOR_YEARS if c in data.columns]
    data = data[cols].copy()
    for col in cols[1:]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.dropna(subset=["Data"]).drop_duplicates("Data").set_index("Data").sort_index()
    data = data.dropna(how="all")
    return data


def build_payload(df: pd.DataFrame) -> dict:
    tenors = [t for t in TENOR_YEARS if t in df.columns and df[t].notna().any()]
    clean = df[tenors].dropna(how="all")
    clean = clean.ffill().dropna(how="any")
    start = clean.index.min()
    z_days = [(d - start).days for d in clean.index]

    return {
        "generated_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": str(XLSX_PATH),
        "dates": [d.strftime("%Y-%m-%d") for d in clean.index],
        "z_days": z_days,
        "tenors": [{"label": t, "years": TENOR_YEARS[t]} for t in tenors],
        "values": clean.round(4).values.tolist(),
    }


HTML_TEMPLATE = Template(r"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Curva DI 3D</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root {
      --bg: #ffffff;
      --panel: #f5f6f7;
      --panel-2: #eceff1;
      --text: #202124;
      --muted: #6b7280;
      --border: #d3d7dc;
      --blue: #4a7fb5;
      --red: #cd6252;
      --green: #5c9478;
      --gold: #b29234;
      --purple: #796cb7;
      --dark: #515151;
    }
    * { box-sizing: border-box; }
    html, body { height: 100%; margin: 0; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: Arial, sans-serif;
      overflow: hidden;
    }
    .app {
      display: grid;
      grid-template-columns: 320px 1fr;
      height: 100vh;
      min-height: 680px;
    }
    aside {
      border-right: 1px solid var(--border);
      background: var(--panel);
      padding: 16px 14px;
      overflow: auto;
    }
    main {
      min-width: 0;
      display: grid;
      grid-template-rows: auto 1fr;
      height: 100vh;
    }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 14px 18px 10px;
      border-bottom: 1px solid var(--border);
    }
    h1 {
      margin: 0;
      font-family: "Segoe UI", Arial, sans-serif;
      font-weight: 700;
      color: var(--dark);
      font-size: 26px;
      line-height: 1.1;
      letter-spacing: 0;
    }
    .meta {
      color: var(--muted);
      font-size: 12px;
      white-space: nowrap;
    }
    .section {
      border: 1px solid var(--border);
      background: #fff;
      padding: 12px;
      margin-bottom: 12px;
    }
    .section-title {
      font-family: "Segoe UI", Arial, sans-serif;
      font-weight: 700;
      color: var(--dark);
      font-size: 13px;
      margin-bottom: 10px;
      text-transform: uppercase;
      letter-spacing: .02em;
    }
    .row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      align-items: center;
      margin-bottom: 8px;
    }
    label {
      font-size: 12px;
      color: #30343a;
    }
    input[type="date"], select {
      width: 100%;
      height: 30px;
      border: 1px solid var(--border);
      background: #fff;
      color: var(--text);
      padding: 4px 6px;
      font: 12px Arial, sans-serif;
    }
    input[type="range"] { width: 100%; }
    button {
      height: 30px;
      border: 1px solid var(--border);
      background: var(--panel-2);
      color: var(--text);
      font: 12px Arial, sans-serif;
      cursor: pointer;
    }
    button:hover { border-color: #aeb5bd; background: #e4e8eb; }
    .button-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 6px;
      margin-bottom: 8px;
    }
    .button-grid.two { grid-template-columns: repeat(2, 1fr); }
    .tenors {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 6px;
    }
    .check {
      display: flex;
      align-items: center;
      gap: 7px;
      min-height: 26px;
      font-size: 12px;
      border: 1px solid var(--border);
      background: #fff;
      padding: 4px 6px;
    }
    .swatch {
      width: 18px;
      height: 3px;
      display: inline-block;
      background: var(--blue);
      flex: 0 0 auto;
    }
    .status {
      font-size: 12px;
      line-height: 1.45;
      color: var(--muted);
      margin-top: 8px;
    }
    #chart {
      width: 100%;
      height: 100%;
      min-height: 0;
    }
    .chart-wrap { min-height: 0; }
    @media (max-width: 980px) {
      body { overflow: auto; }
      .app { grid-template-columns: 1fr; height: auto; }
      aside { border-right: 0; border-bottom: 1px solid var(--border); }
      main { height: 78vh; min-height: 620px; }
      header { align-items: flex-start; flex-direction: column; }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside>
      <div class="section">
        <div class="section-title">Visualização</div>
        <div class="row">
          <label for="mode">Modo</label>
          <select id="mode">
            <option value="curves">Curvas por data</option>
            <option value="surface">Superfície</option>
            <option value="tenors">Séries por vértice</option>
            <option value="all">Tudo</option>
          </select>
        </div>
        <div class="row">
          <label for="density">Densidade</label>
          <input id="density" type="range" min="1" max="30" value="7">
        </div>
        <div class="row">
          <label for="opacity">Opacidade</label>
          <input id="opacity" type="range" min="20" max="100" value="86">
        </div>
        <div class="status" id="densityLabel"></div>
      </div>

      <div class="section">
        <div class="section-title">Corte no tempo</div>
        <div class="row">
          <label for="startDate">Início</label>
          <input id="startDate" type="date">
        </div>
        <div class="row">
          <label for="endDate">Fim</label>
          <input id="endDate" type="date">
        </div>
        <div class="button-grid">
          <button data-window="180">6M</button>
          <button data-window="365">1Y</button>
          <button data-window="730">2Y</button>
          <button data-window="1095">3Y</button>
          <button data-window="1825">5Y</button>
          <button data-window="all">Tudo</button>
        </div>
      </div>

      <div class="section">
        <div class="section-title">Vértices</div>
        <div class="button-grid two">
          <button id="selectAll">Selecionar todos</button>
          <button id="clearAll">Limpar</button>
          <button id="coreTenors">Principais</button>
          <button id="frontTenors">Curto prazo</button>
        </div>
        <div class="tenors" id="tenorChecks"></div>
      </div>

      <div class="section">
        <div class="section-title">Câmera</div>
        <div class="button-grid">
          <button data-camera="persp">Persp.</button>
          <button data-camera="front">Frente</button>
          <button data-camera="side">Lado</button>
          <button data-camera="top">Topo</button>
          <button data-camera="rate">Taxa</button>
          <button id="resetView">Reset</button>
        </div>
        <div class="button-grid">
          <button id="zoomIn">Zoom +</button>
          <button id="zoomOut">Zoom -</button>
          <button id="rotate">Girar</button>
          <button data-nudge="left">←</button>
          <button data-nudge="up">↑</button>
          <button data-nudge="right">→</button>
        </div>
      </div>

      <div class="section">
        <div class="section-title">Leitura</div>
        <div class="status" id="status"></div>
      </div>
    </aside>

    <main>
      <header>
        <h1>Curva DI 3D</h1>
        <div class="meta">Fonte: didol - novo_ticker.xlsx | X = tempo | Y = prazo | Z = % a.a. | Gerado em $generated_at</div>
      </header>
      <div class="chart-wrap">
        <div id="chart"></div>
      </div>
    </main>
  </div>

  <script>
    const DATA = $payload_json;
    const COLORWAY = ['#4a7fb5', '#cd6252', '#5c9478', '#b29234', '#796cb7', '#515151', '#65a356', '#dc7878', '#c285a3', '#808080'];
    const chart = document.getElementById('chart');
    const state = {
      selected: new Set(DATA.tenors.map(t => t.label)),
      rotating: false,
      angle: 0,
      camera: { eye: { x: 1.65, y: 1.25, z: 0.9 }, up: { x: 0, y: 0, z: 1 } },
    };

    const controls = {
      mode: document.getElementById('mode'),
      density: document.getElementById('density'),
      opacity: document.getElementById('opacity'),
      startDate: document.getElementById('startDate'),
      endDate: document.getElementById('endDate'),
      status: document.getElementById('status'),
      densityLabel: document.getElementById('densityLabel'),
      tenorChecks: document.getElementById('tenorChecks'),
    };

    function dateIndex(dateStr) {
      return DATA.dates.findIndex(d => d === dateStr);
    }

    function clampDateInputs() {
      controls.startDate.min = DATA.dates[0];
      controls.startDate.max = DATA.dates[DATA.dates.length - 1];
      controls.endDate.min = DATA.dates[0];
      controls.endDate.max = DATA.dates[DATA.dates.length - 1];
      controls.startDate.value = DATA.dates[Math.max(0, DATA.dates.length - 730)];
      controls.endDate.value = DATA.dates[DATA.dates.length - 1];
    }

    function tenorColor(label) {
      const idx = DATA.tenors.findIndex(t => t.label === label);
      return COLORWAY[idx % COLORWAY.length];
    }

    function renderTenorChecks() {
      controls.tenorChecks.innerHTML = '';
      DATA.tenors.forEach(t => {
        const item = document.createElement('label');
        item.className = 'check';
        const input = document.createElement('input');
        input.type = 'checkbox';
        input.checked = state.selected.has(t.label);
        input.dataset.tenor = t.label;
        const swatch = document.createElement('span');
        swatch.className = 'swatch';
        swatch.style.background = tenorColor(t.label);
        const text = document.createElement('span');
        text.textContent = t.label === '1 DIA' ? 'DI' : t.label;
        item.append(input, swatch, text);
        controls.tenorChecks.appendChild(item);
      });
    }

    function currentSlices() {
      let a = dateIndex(controls.startDate.value);
      let b = dateIndex(controls.endDate.value);
      if (a < 0) a = 0;
      if (b < 0) b = DATA.dates.length - 1;
      if (a > b) [a, b] = [b, a];
      const step = Number(controls.density.value);
      const tenorIdx = DATA.tenors.map((t, i) => state.selected.has(t.label) ? i : -1).filter(i => i >= 0);
      const dateIdx = [];
      for (let i = a; i <= b; i += step) dateIdx.push(i);
      if (!dateIdx.includes(b)) dateIdx.push(b);
      return { a, b, step, tenorIdx, dateIdx };
    }

    function ticksForZ(a, b) {
      const ticks = [];
      const labels = [];
      let lastYear = '';
      for (let i = a; i <= b; i++) {
        const y = DATA.dates[i].slice(0, 4);
        if (y !== lastYear) {
          ticks.push(DATA.z_days[i]);
          labels.push(y);
          lastYear = y;
        }
      }
      return { tickvals: ticks, ticktext: labels };
    }

    function traces() {
      const { a, b, step, tenorIdx, dateIdx } = currentSlices();
      const opacity = Number(controls.opacity.value) / 100;
      const mode = controls.mode.value;
      const out = [];

      if (mode === 'surface' || mode === 'all') {
        const xTime = dateIdx.map(i => tenorIdx.map(() => DATA.z_days[i]));
        const yTenor = dateIdx.map(i => tenorIdx.map(j => DATA.tenors[j].years));
        const zRate = dateIdx.map(i => tenorIdx.map(j => DATA.values[i][j]));
        out.push({
          type: 'surface',
          name: 'Superfície',
          x: xTime,
          y: yTenor,
          z: zRate,
          surfacecolor: zRate,
          colorscale: 'Viridis',
          opacity: Math.max(0.25, opacity - 0.12),
          showscale: true,
          colorbar: { title: '% a.a.', thickness: 10, len: 0.65 },
          hovertemplate: 'Tempo: %{x:.0f} dias<br>Prazo: %{y:.2f} anos<br>Taxa: %{z:.2f}%<extra></extra>'
        });
      }

      if (mode === 'curves' || mode === 'all') {
        dateIdx.forEach((i, k) => {
          const alpha = mode === 'all' ? 0.28 : opacity;
          out.push({
            type: 'scatter3d',
            mode: 'lines',
            name: DATA.dates[i],
            showlegend: k % Math.max(1, Math.ceil(dateIdx.length / 8)) === 0,
            x: tenorIdx.map(() => DATA.z_days[i]),
            y: tenorIdx.map(j => DATA.tenors[j].years),
            z: tenorIdx.map(j => DATA.values[i][j]),
            line: { color: DATA.z_days[i], colorscale: 'Bluered', width: mode === 'all' ? 2 : 3 },
            opacity: alpha,
            hovertemplate: 'Data: ' + DATA.dates[i] + '<br>Prazo: %{y:.2f} anos<br>Taxa: %{z:.2f}%<extra></extra>'
          });
        });
      }

      if (mode === 'tenors' || mode === 'all') {
        tenorIdx.forEach(j => {
          const label = DATA.tenors[j].label;
          const display = label === '1 DIA' ? 'DI' : label;
          out.push({
            type: 'scatter3d',
            mode: 'lines',
            name: display,
            x: dateIdx.map(i => DATA.z_days[i]),
            y: dateIdx.map(() => DATA.tenors[j].years),
            z: dateIdx.map(i => DATA.values[i][j]),
            line: { color: tenorColor(label), width: 5 },
            opacity,
            hovertemplate: 'Vértice: ' + display + '<br>Data: %{text}<br>Taxa: %{z:.2f}%<extra></extra>',
            text: dateIdx.map(i => DATA.dates[i]),
          });
        });
      }

      controls.densityLabel.textContent = `1 linha a cada $${step} dia(s); $${dateIdx.length} datas no corte.`;
      controls.status.textContent = `$${DATA.dates[a]} a $${DATA.dates[b]} | $${tenorIdx.length} vértice(s) | X = tempo, Y = prazo, Z = % a.a.`;
      return out;
    }

    function layout() {
      const { a, b } = currentSlices();
      const zticks = ticksForZ(a, b);
      return {
        margin: { l: 0, r: 0, t: 0, b: 0 },
        paper_bgcolor: '#ffffff',
        plot_bgcolor: '#ffffff',
        font: { family: 'Arial, sans-serif', size: 11, color: '#202124' },
        showlegend: true,
        legend: { orientation: 'h', x: 0.01, y: 0.99, bgcolor: 'rgba(255,255,255,0.78)' },
        scene: {
          xaxis: { title: 'Tempo', tickvals: zticks.tickvals, ticktext: zticks.ticktext, gridcolor: '#e5e7eb', zeroline: false },
          yaxis: { title: 'Prazo', tickvals: DATA.tenors.map(t => t.years), ticktext: DATA.tenors.map(t => t.label === '1 DIA' ? 'DI' : t.label), gridcolor: '#e5e7eb', zeroline: false },
          zaxis: { title: '% a.a.', gridcolor: '#e5e7eb', zeroline: false },
          camera: state.camera,
          aspectmode: 'manual',
          aspectratio: { x: 1.65, y: 0.95, z: 0.85 },
          bgcolor: '#ffffff',
        },
      };
    }

    function draw() {
      Plotly.react(chart, traces(), layout(), {
        responsive: true,
        displaylogo: false,
        scrollZoom: true,
        modeBarButtonsToAdd: ['drawline', 'eraseshape'],
      });
    }

    function setCamera(name) {
      const cams = {
        persp: { eye: { x: 1.65, y: 1.25, z: 0.9 }, up: { x: 0, y: 0, z: 1 } },
        front: { eye: { x: 0, y: 2.25, z: 0.25 }, up: { x: 0, y: 0, z: 1 } },
        side: { eye: { x: 2.35, y: 0.05, z: 0.35 }, up: { x: 0, y: 0, z: 1 } },
        top: { eye: { x: 0, y: 0, z: 2.55 }, up: { x: 0, y: 1, z: 0 } },
        rate: { eye: { x: 1.45, y: 0.55, z: 1.75 }, up: { x: 0, y: 0, z: 1 } },
      };
      state.camera = cams[name] || cams.persp;
      draw();
    }

    function scaleCamera(factor) {
      const eye = state.camera.eye;
      state.camera.eye = { x: eye.x * factor, y: eye.y * factor, z: eye.z * factor };
      draw();
    }

    function nudgeCamera(dir) {
      const eye = { ...state.camera.eye };
      if (dir === 'left') eye.x -= 0.15;
      if (dir === 'right') eye.x += 0.15;
      if (dir === 'up') eye.z += 0.15;
      state.camera.eye = eye;
      draw();
    }

    function rotateLoop() {
      if (!state.rotating) return;
      state.angle += 0.025;
      const r = 2.0;
      state.camera.eye = { x: Math.cos(state.angle) * r, y: Math.sin(state.angle) * r, z: 0.9 };
      Plotly.relayout(chart, { 'scene.camera': state.camera });
      requestAnimationFrame(rotateLoop);
    }

    function initEvents() {
      ['mode', 'density', 'opacity', 'startDate', 'endDate'].forEach(id => {
        document.getElementById(id).addEventListener('input', draw);
      });

      controls.tenorChecks.addEventListener('change', ev => {
        const t = ev.target.dataset.tenor;
        if (!t) return;
        ev.target.checked ? state.selected.add(t) : state.selected.delete(t);
        draw();
      });

      document.getElementById('selectAll').onclick = () => { state.selected = new Set(DATA.tenors.map(t => t.label)); renderTenorChecks(); draw(); };
      document.getElementById('clearAll').onclick = () => { state.selected = new Set(); renderTenorChecks(); draw(); };
      document.getElementById('coreTenors').onclick = () => { state.selected = new Set(['1 DIA', '3M', '9M', '2Y', '5Y', '10Y']); renderTenorChecks(); draw(); };
      document.getElementById('frontTenors').onclick = () => { state.selected = new Set(['1 DIA', '1M', '2M', '3M', '6M', '9M', '1Y']); renderTenorChecks(); draw(); };

      document.querySelectorAll('[data-window]').forEach(btn => {
        btn.onclick = () => {
          const val = btn.dataset.window;
          const end = DATA.dates[DATA.dates.length - 1];
          controls.endDate.value = end;
          if (val === 'all') controls.startDate.value = DATA.dates[0];
          else controls.startDate.value = DATA.dates[Math.max(0, DATA.dates.length - Number(val))];
          draw();
        };
      });

      document.querySelectorAll('[data-camera]').forEach(btn => btn.onclick = () => setCamera(btn.dataset.camera));
      document.querySelectorAll('[data-nudge]').forEach(btn => btn.onclick = () => nudgeCamera(btn.dataset.nudge));
      document.getElementById('resetView').onclick = () => setCamera('persp');
      document.getElementById('zoomIn').onclick = () => scaleCamera(0.82);
      document.getElementById('zoomOut').onclick = () => scaleCamera(1.22);
      document.getElementById('rotate').onclick = () => {
        state.rotating = !state.rotating;
        if (state.rotating) rotateLoop();
      };
    }

    clampDateInputs();
    renderTenorChecks();
    initEvents();
    draw();
  </script>
</body>
</html>
""")


def main() -> None:
    df = read_history()
    payload = build_payload(df)
    html = HTML_TEMPLATE.substitute(
        generated_at=payload["generated_at"],
        payload_json=json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
    )
    OUT_HTML.write_text(html, encoding="utf-8")
    OUT_HTML_PAGES.write_text(html, encoding="utf-8")
    print(f"Gerado: {OUT_HTML}")
    print(f"Gerado: {OUT_HTML_PAGES}")


if __name__ == "__main__":
    main()

