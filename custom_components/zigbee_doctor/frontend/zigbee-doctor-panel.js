class ZigbeeDoctorPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._entityMap = null;
    this._entityMapPromise = null;
  }

  set hass(hass) {
    this._hass = hass;
    this._ensureEntityMap();
    this._render();
  }

  connectedCallback() {
    this._render();
  }

  _isSpanish() {
    const lang = this._hass?.locale?.language || this._hass?.language || "en";
    return String(lang).toLowerCase().startsWith("es");
  }

  _t(key) {
    const es = {
      title: "Zigbee Doctor",
      subtitle: "Diagnóstico claro de tu red Zigbee",
      functioning: "Funcionando",
      offline: "Sin conexión",
      batteries: "Batería baja",
      routers: "Repetidores",
      analyze: "Analizar ahora",
      report: "Generar informe",
      whatToDo: "Qué hacer ahora",
      viewDevices: "Ver dispositivos",
      noData: "Todavía no hay datos. Revisa que MQTT y Zigbee2MQTT estén publicando estado y disponibilidad.",
      waiting: "Esperando datos de tu red",
      bridge: "Puente",
      lastUpdate: "Actualizado",
      sok: "Bien",
      swarning: "Atención",
      scritical: "Crítico",
      sunknown: "Esperando"
    };
    const en = {
      title: "Zigbee Doctor",
      subtitle: "Clear diagnostics for your Zigbee network",
      functioning: "Working",
      offline: "Offline",
      batteries: "Low battery",
      routers: "Repeaters",
      analyze: "Analyze now",
      report: "Generate report",
      whatToDo: "What to do now",
      viewDevices: "View devices",
      noData: "No data yet. Check that MQTT and Zigbee2MQTT are publishing state and availability.",
      waiting: "Waiting for network data",
      bridge: "Bridge",
      lastUpdate: "Updated",
      sok: "Healthy",
      swarning: "Attention",
      scritical: "Critical",
      sunknown: "Waiting"
    };
    return (this._isSpanish() ? es : en)[key] || key;
  }

  _ensureEntityMap() {
    if (this._entityMapPromise || !this._hass?.callWS) return;
    const keys = [
      "network_status",
      "health_score",
      "device_count",
      "offline_devices",
      "problem_count",
      "low_battery_devices",
      "stale_devices"
    ];
    this._entityMapPromise = this._hass
      .callWS({ type: "config/entity_registry/list" })
      .then((entries) => {
        const map = {};
        for (const entry of entries || []) {
          if (entry.platform !== "zigbee_doctor") continue;
          if (entry.translation_key && keys.includes(entry.translation_key)) {
            map[entry.translation_key] = entry.entity_id;
          }
        }
        this._entityMap = map;
        this._render();
      })
      .catch(() => {
        this._entityMap = {};
      });
  }

  _entityId(key) {
    if (this._entityMap && this._entityMap[key]) return this._entityMap[key];
    return `sensor.zigbee_doctor_${key}`;
  }

  _state(key) {
    return this._hass?.states?.[this._entityId(key)];
  }

  _esc(value) {
    return String(value ?? "").replace(/[&<>"']/g, (c) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;"
    }[c]));
  }

  _num(value, fallback = 0) {
    return value === undefined || value === null ? fallback : value;
  }

  _callService(service) {
    if (!this._hass) return;
    const data = service === "generate_report" ? { language: this._isSpanish() ? "es" : "en" } : {};
    this._hass.callService("zigbee_doctor", service, data);
  }

  _render() {
    if (!this._hass) return;

    const statusEntity = this._state("network_status");
    const attrs = statusEntity?.attributes || {};
    const summary = attrs.summary || {};
    const actions = attrs.actions || [];

    const status = statusEntity?.state || "unknown";
    const headline = attrs.headline || this._t("waiting");
    const subline = attrs.subline || "";
    const bridge = attrs.bridge_state || "unknown";
    const updatedAt = attrs.updated_at ? new Date(attrs.updated_at).toLocaleString() : "-";

    const functioning = this._num(summary.functioning_count);
    const total = this._num(summary.device_count);
    const offline = this._num(summary.offline_count);
    const lowBattery = this._num(summary.low_battery_count);
    const routers = this._num(summary.router_count);

    const cls = ["ok", "warning", "critical"].includes(status) ? status : "unknown";

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; padding: 24px; box-sizing: border-box; --zd-card-bg: var(--card-background-color, #fff); --zd-text: var(--primary-text-color, #111); --zd-muted: var(--secondary-text-color, #667085); --zd-border: var(--divider-color, rgba(0,0,0,.12)); --zd-radius: 16px; --zd-ok: #12a150; --zd-warning: #df8d00; --zd-critical: #d92d20; --zd-unknown: #667085; }
        .wrap { max-width: 1120px; margin: 0 auto; }
        .hero { margin-bottom: 18px; }
        .title { font-size: clamp(28px, 4vw, 46px); font-weight: 800; letter-spacing: -0.03em; line-height: 1; color: var(--zd-text); }
        .subtitle { color: var(--zd-muted); font-size: 15px; margin-top: 6px; }
        .banner { border-radius: var(--zd-radius); padding: 20px 22px; margin-bottom: 18px; display: flex; gap: 16px; align-items: flex-start; border: 1px solid var(--zd-border); }
        .banner.ok { background: rgba(18,161,80,.10); border-color: rgba(18,161,80,.30); }
        .banner.warning { background: rgba(223,141,0,.10); border-color: rgba(223,141,0,.30); }
        .banner.critical { background: rgba(217,45,32,.10); border-color: rgba(217,45,32,.30); }
        .banner.unknown { background: rgba(102,112,133,.08); }
        .banner .ic { font-size: 26px; line-height: 1; }
        .banner.ok .ic, .banner.ok .headline { color: var(--zd-ok); }
        .banner.warning .ic, .banner.warning .headline { color: var(--zd-warning); }
        .banner.critical .ic, .banner.critical .headline { color: var(--zd-critical); }
        .banner.unknown .ic, .banner.unknown .headline { color: var(--zd-unknown); }
        .headline { font-size: 20px; font-weight: 800; }
        .subline { font-size: 14px; color: var(--zd-text); opacity: .85; margin-top: 5px; line-height: 1.5; }
        .meta { color: var(--zd-muted); font-size: 12px; margin-top: 8px; }
        .grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-bottom: 20px; }
        .metric { background: var(--zd-card-bg); border: 1px solid var(--zd-border); border-radius: var(--zd-radius); padding: 16px; }
        .metric .label { color: var(--zd-muted); font-size: 13px; font-weight: 600; }
        .metric .value { color: var(--zd-text); font-size: 30px; font-weight: 800; line-height: 1.1; margin-top: 6px; }
        .metric .value.bad { color: var(--zd-critical); }
        .metric .value.warn { color: var(--zd-warning); }
        .metric .value.good { color: var(--zd-ok); }
        .actions-bar { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 18px; }
        button { border: 0; border-radius: 999px; padding: 11px 18px; font-weight: 700; cursor: pointer; background: var(--primary-color, #03a9f4); color: var(--text-primary-color, white); font-size: 14px; }
        button.secondary { background: transparent; border: 1px solid var(--zd-border); color: var(--zd-text); }
        .section-title { font-size: 17px; font-weight: 800; color: var(--zd-text); margin: 0 0 10px; }
        .todo { border: 1px solid var(--zd-border); border-radius: var(--zd-radius); overflow: hidden; background: var(--zd-card-bg); }
        .action { display: flex; gap: 12px; padding: 15px 18px; border-top: 1px solid var(--zd-border); align-items: flex-start; }
        .action:first-child { border-top: 0; }
        .dot { flex-shrink: 0; width: 9px; height: 9px; border-radius: 50%; margin-top: 6px; background: var(--zd-warning); }
        .dot.critical { background: var(--zd-critical); }
        .dot.warning { background: var(--zd-warning); }
        .dot.info { background: var(--zd-ok); }
        .action-title { font-size: 15px; font-weight: 700; color: var(--zd-text); }
        .action-detail { font-size: 13.5px; color: var(--zd-muted); line-height: 1.55; margin-top: 4px; }
        details.devs { margin-top: 8px; }
        details.devs summary { font-size: 13px; color: var(--primary-color, #03a9f4); cursor: pointer; list-style: none; }
        details.devs summary::-webkit-details-marker { display: none; }
        .dev-list { font-size: 13px; color: var(--zd-text); margin-top: 8px; line-height: 1.7; }
        .empty { padding: 18px; color: var(--zd-muted); line-height: 1.5; font-size: 14px; }
        @media (max-width: 900px) { :host { padding: 16px; } .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
        @media (max-width: 520px) { .grid { grid-template-columns: 1fr; } }
      </style>

      <div class="wrap">
        <div class="hero">
          <div class="title">${this._t("title")}</div>
          <div class="subtitle">${this._t("subtitle")}</div>
        </div>

        <div class="banner ${cls}">
          <div class="ic">${this._bannerIcon(cls)}</div>
          <div style="flex:1">
            <div class="headline">${this._esc(headline)}</div>
            <div class="subline">${this._esc(subline)}</div>
            <div class="meta">${this._t("bridge")}: ${this._esc(bridge)} · ${this._t("lastUpdate")}: ${this._esc(updatedAt)}</div>
          </div>
        </div>

        <div class="grid">
          ${this._metric(this._t("functioning"), `${functioning} / ${total}`, total && functioning === total ? "good" : "")}
          ${this._metric(this._t("offline"), offline, offline > 0 ? "bad" : "")}
          ${this._metric(this._t("batteries"), lowBattery, lowBattery > 0 ? "warn" : "")}
          ${this._metric(this._t("routers"), routers, "")}
        </div>

        <div class="actions-bar">
          <button data-action="analyze">${this._t("analyze")}</button>
          <button class="secondary" data-action="report">${this._t("report")}</button>
        </div>

        <div class="section-title">${this._t("whatToDo")}</div>
        <div class="todo">${this._renderActions(actions)}</div>
      </div>
    `;

    this.shadowRoot.querySelector('[data-action="analyze"]')?.addEventListener("click", () => this._callService("analyze_now"));
    this.shadowRoot.querySelector('[data-action="report"]')?.addEventListener("click", () => this._callService("generate_report"));
  }

  _bannerIcon(cls) {
    if (cls === "ok") return "✓";
    if (cls === "critical") return "!";
    if (cls === "warning") return "!";
    return "…";
  }

  _metric(label, value, valueClass) {
    return `<div class="metric"><div class="label">${label}</div><div class="value ${valueClass}">${this._esc(value)}</div></div>`;
  }

  _renderActions(actions) {
    const items = (Array.isArray(actions) ? actions : []).filter((a) => a.code !== "network_ok");

    if (items.length === 0) {
      const ok = (actions || []).find((a) => a.code === "network_ok");
      if (ok) {
        return `<div class="empty"><strong>${this._esc(ok.title)}</strong><br>${this._esc(ok.detail || "")}</div>`;
      }
      return `<div class="empty">${this._t("noData")}</div>`;
    }

    return items.slice(0, 10).map((action) => {
      const devices = Array.isArray(action.devices) ? action.devices : [];
      const expandable = devices.length > 1
        ? `<details class="devs"><summary>${this._t("viewDevices")} (${devices.length})</summary><div class="dev-list">${devices.map((d) => this._esc(d)).join(" · ")}</div></details>`
        : "";
      return `
        <div class="action">
          <span class="dot ${action.severity || "warning"}"></span>
          <div style="flex:1">
            <div class="action-title">${this._esc(action.title)}</div>
            <div class="action-detail">${this._esc(action.detail || "")}</div>
            ${expandable}
          </div>
        </div>`;
    }).join("");
  }
}

customElements.define("zigbee-doctor-panel", ZigbeeDoctorPanel);
