const KB = {
  repeater: {
    es: {
      title: "Repetidores (routers)",
      what: "Aparatos enchufados a la corriente (enchufes, bombillas, relés) que reenvían la señal de otros. Amplían el alcance de la red.",
      why: "Son la columna vertebral de tu red. Si uno se cae, los aparatos que dependían de él pueden fallar aunque estén bien. Cuantos más repetidores bien repartidos, más estable la red."
    },
    en: {
      title: "Repeaters (routers)",
      what: "Mains-powered devices (plugs, bulbs, relays) that relay other devices' signals. They extend your network's range.",
      why: "They are the backbone of your network. If one goes down, the devices relying on it can fail even if they are fine. More well-spread repeaters mean a more stable network."
    }
  },
  availability: {
    es: {
      title: "Disponibilidad («sin conexión»)",
      what: "Zigbee2MQTT marca un aparato como «sin conexión» cuando lleva un tiempo sin dar señales de vida.",
      why: "En aparatos enchufados es señal clara de problema. En aparatos de pila a veces solo estaba dormido: comprueba pila y distancia antes de actuar."
    },
    en: {
      title: "Availability (“offline”)",
      what: "Zigbee2MQTT marks a device as offline when it hasn't reported for a while.",
      why: "For mains devices it's a clear problem. For battery devices it may just have been asleep: check battery and distance before acting."
    }
  },
  battery: {
    es: {
      title: "Dispositivos de pila",
      what: "Sensores que duermen casi siempre para ahorrar batería (movimiento, puertas, temperatura). Solo «hablan» de vez en cuando.",
      why: "Es normal que tarden en reportar; no significa que estén caídos. No los re-emparejes a la primera. Una pila baja provoca fallos que parecen de cobertura: cámbiala antes de buscar otros problemas."
    },
    en: {
      title: "Battery devices",
      what: "Sensors that sleep most of the time to save power (motion, doors, temperature). They only talk now and then.",
      why: "It's normal for them to be slow to report; it doesn't mean they're down. Don't re-pair right away. A low battery causes failures that look like coverage problems: replace it first."
    }
  },
  lqi: {
    es: {
      title: "LQI (calidad del enlace)",
      what: "Una nota de 0 a 255 de cómo de bien «oye» el coordinador a un aparato. Más alto, mejor enlace.",
      why: "Sirve de orientación, pero no como prueba: varía mucho entre marcas y momentos. No te obsesiones con un valor puntual; preocúpate solo si es constantemente muy bajo (por debajo de ~20-30)."
    },
    en: {
      title: "LQI (link quality)",
      what: "A 0-255 score of how well the coordinator hears a device. Higher is better.",
      why: "It's a hint, not proof: it varies a lot between brands and moments. Don't obsess over a single value; only worry if it's consistently very low (below ~20-30)."
    }
  },
  rssi: {
    es: {
      title: "RSSI (potencia de señal)",
      what: "La fuerza de la señal recibida, en dBm (números negativos: -50 es fuerte, -90 es débil).",
      why: "Más fiable que el LQI para ver cobertura real, aunque no todos los aparatos lo reportan. Señal débil constante = acerca un repetidor."
    },
    en: {
      title: "RSSI (signal strength)",
      what: "The received signal strength in dBm (negative numbers: -50 is strong, -90 is weak).",
      why: "More reliable than LQI for real coverage, though not every device reports it. Consistently weak signal means you should add a repeater nearby."
    }
  },
  coordinator: {
    es: {
      title: "Coordinador",
      what: "El «cerebro» de la red Zigbee: el adaptador (USB o de red) que gestiona todos los aparatos. Solo hay uno.",
      why: "Si el coordinador o el puente fallan, toda la red Zigbee deja de funcionar. Colócalo lejos de routers wifi y puertos USB 3.0, que causan interferencias."
    },
    en: {
      title: "Coordinator",
      what: "The brain of the Zigbee network: the adapter (USB or network) that manages every device. There is only one.",
      why: "If the coordinator or bridge fails, the whole Zigbee network stops. Keep it away from wifi routers and USB 3.0 ports, which cause interference."
    }
  },
  chatty: {
    es: {
      title: "Dispositivos «habladores»",
      what: "Aparatos que envían muchísimos mensajes por segundo, a veces por un ajuste agresivo o un firmware con fallos.",
      why: "Saturan la red y la hacen parecer inestable para todos. Si detectas uno, revisa sus ajustes de reporte o actualiza su firmware."
    },
    en: {
      title: "Chatty devices",
      what: "Devices that send a huge number of messages per second, sometimes due to aggressive settings or buggy firmware.",
      why: "They flood the network and make it feel unstable for everyone. If you spot one, review its reporting settings or update its firmware."
    }
  },
  channel: {
    es: {
      title: "Canal e interferencias",
      what: "Zigbee y el wifi de 2,4 GHz comparten espacio. Si usan canales que se solapan, se molestan entre sí.",
      why: "Es una causa típica de red inestable. Elegir un canal Zigbee alejado del de tu wifi arregla caídas raras (cambiar el canal obliga a re-emparejar todo, hazlo con cabeza)."
    },
    en: {
      title: "Channel and interference",
      what: "Zigbee and 2.4 GHz wifi share the same space. If they use overlapping channels, they interfere with each other.",
      why: "It's a classic cause of an unstable network. Picking a Zigbee channel far from your wifi channel can fix odd dropouts (changing the channel forces re-pairing everything, so plan it)."
    }
  },
  last_seen: {
    es: {
      title: "Última vez visto",
      what: "Cuándo fue la última vez que un aparato dio señales de vida.",
      why: "En aparatos de pila es normal que pasen horas. En enchufados, mucho tiempo sin reportar suele indicar un problema."
    },
    en: {
      title: "Last seen",
      what: "When a device last reported.",
      why: "For battery devices, hours are normal. For mains devices, a long silence usually means a problem."
    }
  },
  ota: {
    es: {
      title: "Actualizaciones (OTA)",
      what: "Actualizar el firmware de los aparatos Zigbee por aire, sin cables.",
      why: "Pueden arreglar fallos de estabilidad y de batería, pero también introducir problemas nuevos. Actualiza cuando tengas un motivo, no por defecto."
    },
    en: {
      title: "Updates (OTA)",
      what: "Updating the firmware of Zigbee devices over the air, without cables.",
      why: "They can fix stability and battery issues, but can also introduce new ones. Update when you have a reason, not by default."
    }
  }
};

const KB_ORDER = ["repeater", "availability", "battery", "lqi", "rssi", "coordinator", "chatty", "channel", "last_seen", "ota"];

class ZigbeeDoctorPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._entityMap = null;
    this._entityMapPromise = null;
    this._tab = "resumen";
    this._sort = { key: "status", dir: 1 };
    this._focusConcept = null;
    this._sig = null;
  }

  set hass(hass) {
    this._hass = hass;
    this._ensureEntityMap();
    this._render();
  }

  connectedCallback() {
    this._render(true);
  }

  _isSpanish() {
    const lang = this._hass?.locale?.language || this._hass?.language || "en";
    return String(lang).toLowerCase().startsWith("es");
  }

  _t(key) {
    const es = {
      title: "Zigbee Doctor",
      subtitle: "Diagnóstico claro de tu red Zigbee",
      tabResumen: "Resumen",
      tabDispositivos: "Dispositivos",
      tabAprende: "Aprende",
      functioning: "Funcionando",
      offline: "Sin conexión",
      batteries: "Batería baja",
      routers: "Repetidores",
      analyze: "Analizar ahora",
      report: "Generar informe",
      whatToDo: "Qué hacer ahora",
      viewDevices: "Ver dispositivos",
      learnLink: "¿Qué es esto?",
      noData: "Todavía no hay datos. Revisa que MQTT y Zigbee2MQTT estén publicando estado y disponibilidad.",
      noDevices: "Aún no hay dispositivos. Espera a que Zigbee2MQTT publique la lista.",
      waiting: "Esperando datos de tu red",
      bridge: "Puente",
      lastUpdate: "Actualizado",
      thName: "Nombre",
      thStatus: "Estado",
      thBattery: "Pila",
      thSignal: "Señal",
      thType: "Tipo",
      thLastSeen: "Última vez",
      mains: "Enchufado",
      doffline: "Sin conexión",
      dok: "Bien",
      dlow_battery: "Pila baja",
      dstale: "Sin reportar",
      dunknown: "Desconocido",
      rrouter: "Repetidor",
      rend_device: "De pila",
      rcoordinator: "Coordinador",
      runknown: "—",
      kbWhat: "¿Qué es?",
      kbWhy: "¿Por qué fijarte?"
    };
    const en = {
      title: "Zigbee Doctor",
      subtitle: "Clear diagnostics for your Zigbee network",
      tabResumen: "Summary",
      tabDispositivos: "Devices",
      tabAprende: "Learn",
      functioning: "Working",
      offline: "Offline",
      batteries: "Low battery",
      routers: "Repeaters",
      analyze: "Analyze now",
      report: "Generate report",
      whatToDo: "What to do now",
      viewDevices: "View devices",
      learnLink: "What is this?",
      noData: "No data yet. Check that MQTT and Zigbee2MQTT are publishing state and availability.",
      noDevices: "No devices yet. Wait for Zigbee2MQTT to publish the list.",
      waiting: "Waiting for network data",
      bridge: "Bridge",
      lastUpdate: "Updated",
      thName: "Name",
      thStatus: "Status",
      thBattery: "Battery",
      thSignal: "Signal",
      thType: "Type",
      thLastSeen: "Last seen",
      mains: "Mains",
      doffline: "Offline",
      dok: "OK",
      dlow_battery: "Low battery",
      dstale: "Not reporting",
      dunknown: "Unknown",
      rrouter: "Repeater",
      rend_device: "Battery",
      rcoordinator: "Coordinator",
      runknown: "—",
      kbWhat: "What is it?",
      kbWhy: "Why it matters"
    };
    return (this._isSpanish() ? es : en)[key] || key;
  }

  _ensureEntityMap() {
    if (this._entityMapPromise || !this._hass?.callWS) return;
    const keys = ["network_status", "device_count"];
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
        this._render(true);
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
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
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

  _render(force = false) {
    if (!this._hass) return;
    const statusEntity = this._state("network_status");
    const attrs = statusEntity?.attributes || {};

    const sig = [
      this._tab, this._sort.key, this._sort.dir, this._focusConcept || "",
      statusEntity?.state || "", attrs.updated_at || "", !!this._entityMap, this._isSpanish()
    ].join("|");
    if (!force && sig === this._sig) return;
    this._sig = sig;

    const tabs = [
      ["resumen", this._t("tabResumen")],
      ["dispositivos", this._t("tabDispositivos")],
      ["aprende", this._t("tabAprende")]
    ];

    let content;
    if (this._tab === "dispositivos") content = this._renderDispositivos();
    else if (this._tab === "aprende") content = this._renderAprende();
    else content = this._renderResumen(statusEntity, attrs);

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; padding: 24px; box-sizing: border-box; --zd-text: var(--primary-text-color, #111); --zd-muted: var(--secondary-text-color, #667085); --zd-border: var(--divider-color, rgba(0,0,0,.12)); --zd-card-bg: var(--card-background-color, #fff); --zd-radius: 16px; --zd-ok: #12a150; --zd-warning: #df8d00; --zd-critical: #d92d20; --zd-unknown: #667085; --zd-primary: var(--primary-color, #03a9f4); }
        .wrap { max-width: 1120px; margin: 0 auto; }
        .title { font-size: clamp(28px, 4vw, 46px); font-weight: 800; letter-spacing: -0.03em; line-height: 1; color: var(--zd-text); }
        .subtitle { color: var(--zd-muted); font-size: 15px; margin: 6px 0 16px; }
        .tabbar { display: flex; gap: 4px; border-bottom: 1px solid var(--zd-border); margin-bottom: 18px; flex-wrap: wrap; }
        .tab { padding: 9px 14px; font-size: 14px; font-weight: 600; color: var(--zd-muted); cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -1px; }
        .tab.active { color: var(--zd-text); border-bottom-color: var(--zd-primary); }
        .banner { border-radius: var(--zd-radius); padding: 20px 22px; margin-bottom: 18px; display: flex; gap: 16px; align-items: flex-start; border: 1px solid var(--zd-border); }
        .banner.ok { background: rgba(18,161,80,.10); border-color: rgba(18,161,80,.30); }
        .banner.warning { background: rgba(223,141,0,.10); border-color: rgba(223,141,0,.30); }
        .banner.critical { background: rgba(217,45,32,.10); border-color: rgba(217,45,32,.30); }
        .banner.unknown { background: rgba(102,112,133,.08); }
        .banner .ic { font-size: 26px; font-weight: 800; line-height: 1; }
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
        button { border: 0; border-radius: 999px; padding: 11px 18px; font-weight: 700; cursor: pointer; background: var(--zd-primary); color: var(--text-primary-color, white); font-size: 14px; }
        button.secondary { background: transparent; border: 1px solid var(--zd-border); color: var(--zd-text); }
        .section-title { font-size: 17px; font-weight: 800; color: var(--zd-text); margin: 0 0 10px; }
        .todo { border: 1px solid var(--zd-border); border-radius: var(--zd-radius); overflow: hidden; background: var(--zd-card-bg); }
        .action { display: flex; gap: 12px; padding: 15px 18px; border-top: 1px solid var(--zd-border); align-items: flex-start; }
        .action:first-child { border-top: 0; }
        .dot { flex-shrink: 0; width: 9px; height: 9px; border-radius: 50%; margin-top: 6px; background: var(--zd-warning); }
        .dot.critical { background: var(--zd-critical); } .dot.warning { background: var(--zd-warning); } .dot.info { background: var(--zd-ok); }
        .action-title { font-size: 15px; font-weight: 700; color: var(--zd-text); }
        .action-detail { font-size: 13.5px; color: var(--zd-muted); line-height: 1.55; margin-top: 4px; }
        .learn-link { font-size: 13px; color: var(--zd-primary); cursor: pointer; margin-top: 7px; display: inline-block; }
        details.devs { margin-top: 8px; }
        details.devs summary { font-size: 13px; color: var(--zd-primary); cursor: pointer; list-style: none; }
        details.devs summary::-webkit-details-marker { display: none; }
        .dev-list { font-size: 13px; color: var(--zd-text); margin-top: 8px; line-height: 1.7; }
        .empty { padding: 18px; color: var(--zd-muted); line-height: 1.5; font-size: 14px; border: 1px solid var(--zd-border); border-radius: var(--zd-radius); background: var(--zd-card-bg); }
        .tablewrap { border: 1px solid var(--zd-border); border-radius: var(--zd-radius); overflow: auto; background: var(--zd-card-bg); }
        table.dev-table { width: 100%; border-collapse: collapse; font-size: 14px; }
        table.dev-table th { text-align: left; padding: 12px 14px; color: var(--zd-muted); font-weight: 700; font-size: 12.5px; text-transform: uppercase; letter-spacing: .03em; cursor: pointer; white-space: nowrap; border-bottom: 1px solid var(--zd-border); }
        table.dev-table td { padding: 11px 14px; border-top: 1px solid var(--zd-border); color: var(--zd-text); }
        table.dev-table td.muted { color: var(--zd-muted); font-size: 13px; white-space: nowrap; }
        table.dev-table td.dn { font-weight: 600; }
        .badge { font-size: 12px; font-weight: 700; padding: 3px 9px; border-radius: 999px; white-space: nowrap; }
        .badge.offline { background: rgba(217,45,32,.14); color: var(--zd-critical); }
        .badge.low_battery { background: rgba(223,141,0,.16); color: var(--zd-warning); }
        .badge.stale { background: rgba(223,141,0,.12); color: var(--zd-warning); }
        .badge.ok { background: rgba(18,161,80,.14); color: var(--zd-ok); }
        .badge.unknown { background: rgba(102,112,133,.14); color: var(--zd-unknown); }
        .bat-low { color: var(--zd-critical); font-weight: 700; }
        .kb-card { border: 1px solid var(--zd-border); border-radius: var(--zd-radius); background: var(--zd-card-bg); padding: 16px 18px; margin-bottom: 12px; }
        .kb-card.focus { border-color: var(--zd-primary); box-shadow: 0 0 0 2px rgba(3,169,244,.25); }
        .kb-title { font-size: 16px; font-weight: 800; color: var(--zd-text); }
        .kb-h { font-size: 12.5px; font-weight: 700; color: var(--zd-muted); text-transform: uppercase; letter-spacing: .03em; margin-top: 12px; }
        .kb-p { font-size: 14px; color: var(--zd-text); line-height: 1.55; margin-top: 4px; opacity: .9; }
        @media (max-width: 900px) { :host { padding: 16px; } .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
        @media (max-width: 520px) { .grid { grid-template-columns: 1fr; } }
      </style>

      <div class="wrap">
        <div class="title">${this._t("title")}</div>
        <div class="subtitle">${this._t("subtitle")}</div>
        <div class="tabbar">
          ${tabs.map(([id, label]) => `<div class="tab ${this._tab === id ? "active" : ""}" data-tab="${id}">${label}</div>`).join("")}
        </div>
        <div class="content">${content}</div>
      </div>
    `;

    this._attachEvents();
  }

  _attachEvents() {
    const root = this.shadowRoot;
    root.querySelectorAll(".tab[data-tab]").forEach((el) =>
      el.addEventListener("click", () => {
        this._tab = el.getAttribute("data-tab");
        this._focusConcept = null;
        this._render(true);
      })
    );
    root.querySelector('[data-action="analyze"]')?.addEventListener("click", () => this._callService("analyze_now"));
    root.querySelector('[data-action="report"]')?.addEventListener("click", () => this._callService("generate_report"));
    root.querySelectorAll("[data-learn]").forEach((el) =>
      el.addEventListener("click", () => {
        this._focusConcept = el.getAttribute("data-learn");
        this._tab = "aprende";
        this._render(true);
      })
    );
    root.querySelectorAll("th[data-sort]").forEach((el) =>
      el.addEventListener("click", () => {
        const key = el.getAttribute("data-sort");
        if (this._sort.key === key) this._sort.dir *= -1;
        else this._sort = { key, dir: 1 };
        this._render(true);
      })
    );

    if (this._tab === "aprende" && this._focusConcept) {
      const target = root.getElementById(`concept-${this._focusConcept}`);
      if (target) requestAnimationFrame(() => target.scrollIntoView({ behavior: "smooth", block: "center" }));
    }
  }

  _renderResumen(statusEntity, attrs) {
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

    return `
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
    `;
  }

  _bannerIcon(cls) {
    if (cls === "ok") return "✓";
    if (cls === "unknown") return "…";
    return "!";
  }

  _metric(label, value, valueClass) {
    return `<div class="metric"><div class="label">${label}</div><div class="value ${valueClass}">${this._esc(value)}</div></div>`;
  }

  _renderActions(actions) {
    const items = (Array.isArray(actions) ? actions : []).filter((a) => a.code !== "network_ok");
    if (items.length === 0) {
      const ok = (actions || []).find((a) => a.code === "network_ok");
      if (ok) return `<div class="empty" style="border:0"><strong>${this._esc(ok.title)}</strong><br>${this._esc(ok.detail || "")}</div>`;
      return `<div class="empty" style="border:0">${this._t("noData")}</div>`;
    }
    return items.slice(0, 10).map((action) => {
      const devices = Array.isArray(action.devices) ? action.devices : [];
      const expandable = devices.length > 1
        ? `<details class="devs"><summary>${this._t("viewDevices")} (${devices.length})</summary><div class="dev-list">${devices.map((d) => this._esc(d)).join(" · ")}</div></details>`
        : "";
      const learn = action.learn && KB[action.learn]
        ? `<span class="learn-link" data-learn="${this._esc(action.learn)}">${this._t("learnLink")}</span>`
        : "";
      return `
        <div class="action">
          <span class="dot ${action.severity || "warning"}"></span>
          <div style="flex:1">
            <div class="action-title">${this._esc(action.title)}</div>
            <div class="action-detail">${this._esc(action.detail || "")}</div>
            ${expandable}${learn ? `<div>${learn}</div>` : ""}
          </div>
        </div>`;
    }).join("");
  }

  _renderDispositivos() {
    const dc = this._state("device_count");
    let devices = dc?.attributes?.devices || [];
    if (!devices.length) return `<div class="empty">${this._t("noDevices")}</div>`;
    devices = this._sortDevices(devices.slice());
    const ind = (k) => (this._sort.key === k ? (this._sort.dir > 0 ? " ↑" : " ↓") : "");
    const head = [
      ["name", this._t("thName")], ["status", this._t("thStatus")], ["battery", this._t("thBattery")],
      ["lqi", this._t("thSignal")], ["role", this._t("thType")], ["last_seen", this._t("thLastSeen")]
    ].map(([k, l]) => `<th data-sort="${k}">${l}${ind(k)}</th>`).join("");
    const rows = devices.map((d) => `
      <tr>
        <td class="dn">${this._esc(d.name)}</td>
        <td><span class="badge ${d.status}">${this._t("d" + d.status)}</span></td>
        <td>${this._batteryCell(d)}</td>
        <td>${d.lqi == null ? "—" : this._esc(d.lqi)}</td>
        <td>${this._t("r" + d.role)}</td>
        <td class="muted">${d.last_seen ? this._esc(new Date(d.last_seen).toLocaleString()) : "—"}</td>
      </tr>`).join("");
    return `<div class="tablewrap"><table class="dev-table"><thead><tr>${head}</tr></thead><tbody>${rows}</tbody></table></div>`;
  }

  _batteryCell(d) {
    if (d.battery_powered === false) return `<span class="muted">${this._t("mains")}</span>`;
    if (d.battery == null) return "—";
    const low = d.status === "low_battery";
    return `<span class="${low ? "bat-low" : ""}">${this._esc(d.battery)}%</span>`;
  }

  _sortDevices(devices) {
    const { key, dir } = this._sort;
    const order = { offline: 0, low_battery: 1, stale: 2, unknown: 3, ok: 4 };
    return devices.sort((a, b) => {
      let va;
      let vb;
      if (key === "status") { va = order[a.status] ?? 9; vb = order[b.status] ?? 9; }
      else if (key === "battery") { va = a.battery == null ? Infinity : a.battery; vb = b.battery == null ? Infinity : b.battery; }
      else if (key === "lqi") { va = a.lqi == null ? -Infinity : a.lqi; vb = b.lqi == null ? -Infinity : b.lqi; }
      else if (key === "last_seen") { va = a.last_seen ? Date.parse(a.last_seen) : -Infinity; vb = b.last_seen ? Date.parse(b.last_seen) : -Infinity; }
      else { va = String(a[key] || "").toLowerCase(); vb = String(b[key] || "").toLowerCase(); }
      if (va < vb) return -dir;
      if (va > vb) return dir;
      return 0;
    });
  }

  _renderAprende() {
    const lang = this._isSpanish() ? "es" : "en";
    return KB_ORDER.filter((id) => KB[id]).map((id) => {
      const c = KB[id][lang] || KB[id].en;
      const focus = this._focusConcept === id ? " focus" : "";
      return `
        <div class="kb-card${focus}" id="concept-${id}">
          <div class="kb-title">${this._esc(c.title)}</div>
          <div class="kb-h">${this._t("kbWhat")}</div>
          <div class="kb-p">${this._esc(c.what)}</div>
          <div class="kb-h">${this._t("kbWhy")}</div>
          <div class="kb-p">${this._esc(c.why)}</div>
        </div>`;
    }).join("");
  }
}

customElements.define("zigbee-doctor-panel", ZigbeeDoctorPanel);
