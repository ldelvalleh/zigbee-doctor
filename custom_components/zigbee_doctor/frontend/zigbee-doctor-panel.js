class ZigbeeDoctorPanel extends HTMLElement {
  set hass(hass) {
    this._hass = hass;
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
      subtitle: "Diagnóstico claro de tu red Zigbee2MQTT",
      status: "Estado",
      score: "Salud",
      devices: "Dispositivos",
      offline: "Sin conexión",
      problems: "Problemas",
      batteries: "Batería baja",
      stale: "Sin reportar",
      analyze: "Analizar ahora",
      report: "Generar informe",
      findings: "Hallazgos principales",
      noData: "Todavía no hay datos. Revisa MQTT, el topic base y que Zigbee2MQTT esté publicando disponibilidad y health.",
      ok: "Todo parece estable",
      warning: "Hay avisos que revisar",
      critical: "Atención: hay problemas críticos",
      unknown: "Esperando datos",
      bridge: "Bridge",
      lastUpdate: "Última actualización",
      action: "Acción sugerida"
    };
    const en = {
      title: "Zigbee Doctor",
      subtitle: "Clear diagnostics for your Zigbee2MQTT network",
      status: "Status",
      score: "Health",
      devices: "Devices",
      offline: "Offline",
      problems: "Problems",
      batteries: "Low battery",
      stale: "Stale",
      analyze: "Analyze now",
      report: "Generate report",
      findings: "Main findings",
      noData: "No data yet. Check MQTT, base topic and make sure Zigbee2MQTT publishes availability and health.",
      ok: "Everything looks stable",
      warning: "There are warnings to review",
      critical: "Attention: critical problems found",
      unknown: "Waiting for data",
      bridge: "Bridge",
      lastUpdate: "Last update",
      action: "Suggested action"
    };
    return (this._isSpanish() ? es : en)[key] || key;
  }

  _state(entityId) {
    return this._hass?.states?.[entityId];
  }

  _statusInfo(status) {
    if (status === "ok") return { label: this._t("ok"), cls: "ok" };
    if (status === "warning") return { label: this._t("warning"), cls: "warning" };
    if (status === "critical") return { label: this._t("critical"), cls: "critical" };
    return { label: this._t("unknown"), cls: "unknown" };
  }

  _callService(service) {
    if (!this._hass) return;
    const data = service === "generate_report" ? { language: this._isSpanish() ? "es" : "en" } : {};
    this._hass.callService("zigbee_doctor", service, data);
  }

  _render() {
    if (!this._hass) return;

    const statusEntity = this._state("sensor.zigbee_doctor_network_status");
    const scoreEntity = this._state("sensor.zigbee_doctor_health_score");
    const deviceEntity = this._state("sensor.zigbee_doctor_device_count");
    const offlineEntity = this._state("sensor.zigbee_doctor_offline_devices");
    const problemEntity = this._state("sensor.zigbee_doctor_problem_count");
    const lowBatteryEntity = this._state("sensor.zigbee_doctor_low_battery_devices");
    const staleEntity = this._state("sensor.zigbee_doctor_stale_devices");

    const status = statusEntity?.state || "unknown";
    const info = this._statusInfo(status);
    const problems = statusEntity?.attributes?.problems || problemEntity?.attributes?.problems || [];
    const updatedAt = statusEntity?.attributes?.updated_at || "-";
    const bridge = statusEntity?.attributes?.bridge_state || "unknown";

    this.innerHTML = `
      <style>
        :host {
          display: block;
          padding: 24px;
          box-sizing: border-box;
          --zd-card-bg: var(--card-background-color, #fff);
          --zd-text: var(--primary-text-color, #111);
          --zd-muted: var(--secondary-text-color, #667085);
          --zd-border: var(--divider-color, rgba(0,0,0,.12));
          --zd-radius: 22px;
        }
        .wrap {
          max-width: 1120px;
          margin: 0 auto;
        }
        .hero {
          display: grid;
          gap: 12px;
          margin-bottom: 22px;
        }
        .title {
          font-size: clamp(32px, 5vw, 56px);
          font-weight: 800;
          letter-spacing: -0.04em;
          line-height: 0.95;
          color: var(--zd-text);
        }
        .subtitle {
          color: var(--zd-muted);
          font-size: 17px;
        }
        .status-card {
          border: 1px solid var(--zd-border);
          border-radius: var(--zd-radius);
          background: var(--zd-card-bg);
          padding: 22px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 18px;
          box-shadow: 0 10px 30px rgba(0,0,0,.05);
          margin-bottom: 18px;
        }
        .status-left {
          display: grid;
          gap: 6px;
        }
        .status-label {
          color: var(--zd-muted);
          font-size: 14px;
          text-transform: uppercase;
          letter-spacing: .08em;
          font-weight: 700;
        }
        .status-value {
          font-size: 24px;
          font-weight: 800;
          color: var(--zd-text);
        }
        .pill {
          border-radius: 999px;
          padding: 8px 13px;
          font-weight: 800;
          font-size: 13px;
          color: white;
          background: #7a7a7a;
        }
        .pill.ok { background: #12a150; }
        .pill.warning { background: #df8d00; }
        .pill.critical { background: #d92d20; }
        .pill.unknown { background: #667085; }
        .meta {
          color: var(--zd-muted);
          font-size: 13px;
        }
        .grid {
          display: grid;
          grid-template-columns: repeat(4, minmax(0, 1fr));
          gap: 14px;
          margin-bottom: 18px;
        }
        .metric {
          border: 1px solid var(--zd-border);
          border-radius: var(--zd-radius);
          background: var(--zd-card-bg);
          padding: 18px;
          min-height: 104px;
          display: grid;
          gap: 8px;
        }
        .metric .label {
          color: var(--zd-muted);
          font-size: 13px;
          font-weight: 700;
        }
        .metric .value {
          color: var(--zd-text);
          font-size: 34px;
          font-weight: 850;
          line-height: 1;
        }
        .actions {
          display: flex;
          gap: 10px;
          flex-wrap: wrap;
          margin-bottom: 18px;
        }
        button {
          border: 0;
          border-radius: 999px;
          padding: 12px 17px;
          font-weight: 800;
          cursor: pointer;
          background: var(--primary-color, #03a9f4);
          color: var(--text-primary-color, white);
        }
        button.secondary {
          background: color-mix(in srgb, var(--primary-color, #03a9f4) 12%, transparent);
          color: var(--primary-color, #03a9f4);
        }
        .findings {
          border: 1px solid var(--zd-border);
          border-radius: var(--zd-radius);
          background: var(--zd-card-bg);
          padding: 20px;
        }
        .findings h2 {
          margin: 0 0 12px;
          font-size: 20px;
          color: var(--zd-text);
        }
        .problem {
          border-top: 1px solid var(--zd-border);
          padding: 14px 0;
        }
        .problem:first-of-type { border-top: 0; }
        .problem-title {
          font-weight: 850;
          color: var(--zd-text);
          margin-bottom: 5px;
        }
        .problem-message, .problem-action {
          color: var(--zd-muted);
          line-height: 1.45;
          font-size: 14px;
        }
        .empty {
          color: var(--zd-muted);
          line-height: 1.5;
        }
        @media (max-width: 900px) {
          :host { padding: 16px; }
          .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
          .status-card { align-items: flex-start; flex-direction: column; }
        }
        @media (max-width: 560px) {
          .grid { grid-template-columns: 1fr; }
        }
      </style>

      <div class="wrap">
        <section class="hero">
          <div class="title">${this._t("title")}</div>
          <div class="subtitle">${this._t("subtitle")}</div>
        </section>

        <section class="status-card">
          <div class="status-left">
            <div class="status-label">${this._t("status")}</div>
            <div class="status-value">${info.label}</div>
            <div class="meta">${this._t("bridge")}: ${bridge} · ${this._t("lastUpdate")}: ${updatedAt}</div>
          </div>
          <div class="pill ${info.cls}">${status}</div>
        </section>

        <section class="grid">
          ${this._metric(this._t("score"), `${scoreEntity?.state ?? 0}%`)}
          ${this._metric(this._t("devices"), deviceEntity?.state ?? 0)}
          ${this._metric(this._t("offline"), offlineEntity?.state ?? 0)}
          ${this._metric(this._t("problems"), problemEntity?.state ?? 0)}
          ${this._metric(this._t("batteries"), lowBatteryEntity?.state ?? 0)}
          ${this._metric(this._t("stale"), staleEntity?.state ?? 0)}
        </section>

        <section class="actions">
          <button @click="analyze">${this._t("analyze")}</button>
          <button class="secondary" @click="report">${this._t("report")}</button>
        </section>

        <section class="findings">
          <h2>${this._t("findings")}</h2>
          ${this._renderProblems(problems)}
        </section>
      </div>
    `;

    this.querySelector('button[@click="analyze"]')?.addEventListener("click", () => this._callService("analyze_now"));
    this.querySelector('button[@click="report"]')?.addEventListener("click", () => this._callService("generate_report"));
  }

  _metric(label, value) {
    return `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`;
  }

  _renderProblems(problems) {
    if (!Array.isArray(problems) || problems.length === 0) {
      return `<div class="empty">${this._t("noData")}</div>`;
    }

    return problems.slice(0, 6).map(problem => `
      <div class="problem">
        <div class="problem-title">${problem.title || problem.code || "Finding"}</div>
        <div class="problem-message">${problem.message || ""}</div>
        ${problem.suggested_action ? `<div class="problem-action"><strong>${this._t("action")}:</strong> ${problem.suggested_action}</div>` : ""}
      </div>
    `).join("");
  }
}

customElements.define("zigbee-doctor-panel", ZigbeeDoctorPanel);
