// Welcome.js - Screen 1
// Features: Tagline, Big Mic Button, "or type instead" link, "Try demo" button, 3 Sample Personas

window.Welcome = function Welcome({ t, lang, onStartSpeak, onTypeInstead, onRunDemo }) {
  const personas = window.samplePersonas || {};

  const getPersonaName = (p) => {
    if (!p) return "";
    if (lang === "kn" && p.name_kn) return p.name_kn;
    if (lang === "hi" && p.name_hi) return p.name_hi;
    return p.name;
  };

  const getPersonaRole = (p) => {
    if (!p) return "";
    if (lang === "kn" && p.role_kn) return p.role_kn;
    if (lang === "hi" && p.role_hi) return p.role_hi;
    return p.role;
  };

  const demoPersonaLabel = lang === "kn"
    ? "ಸುನೀತಾ - ಟೈಲರ್"
    : (lang === "hi" ? "सुनीता - दर्जी" : "Sunita - Tailor");

  return (
    <div className="main-content">
      {/* Hero Welcome Box */}
      <div className="card text-center" style={{ marginBottom: "var(--space-lg)" }}>
        <h1 className="heading-hero" style={{ marginTop: "var(--space-xs)" }}>
          {t.appName}
        </h1>
        <p className="subheading" style={{ fontSize: "var(--font-size-md)", fontWeight: "600", color: "var(--text-charcoal)" }}>
          {t.tagline}
        </p>
        <p style={{ color: "var(--text-muted)", fontSize: "var(--font-size-sm)", margin: "-8px 0 var(--space-md) 0" }}>
          {t.micInstruction}
        </p>

        {/* Big Microphone Hero Button */}
        <div className="mic-hero-container" style={{ padding: "var(--space-md) 0 var(--space-sm) 0" }}>
          <div className="mic-pulse-wrapper">
            <div className="pulse-ring"></div>
            <div className="pulse-ring-outer"></div>
            <button
              className="btn-mic-large"
              onClick={onStartSpeak}
              title={lang === "kn" ? "ಮಾತನಾಡಲು ಒತ್ತಿರಿ" : (lang === "hi" ? "बोलने के लिए दबाएं" : "Tap to speak")}
              aria-label="Start voice input"
            >
              <svg viewBox="0 0 24 24">
                <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
              </svg>
            </button>
          </div>

          <button
            type="button"
            className="btn-link"
            onClick={onTypeInstead}
            style={{ marginTop: "var(--space-xs)" }}
          >
            {t.orTypeInstead}
          </button>
        </div>
      </div>

      {/* Demo Mode Section */}
      <div className="card" style={{ background: "var(--bg-subtle)" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "var(--space-xs)" }}>
          <span style={{ fontSize: "0.8rem", fontWeight: "700", textTransform: "uppercase", color: "var(--accent-terracotta)", letterSpacing: "0.5px" }}>
            {t.demoBadge}
          </span>
        </div>

        <h3 style={{ fontSize: "var(--font-size-md)", marginBottom: "var(--space-xs)" }}>
          {lang === "kn" ? "ಒಂದು ಕ್ಲಿಕ್‌ನಲ್ಲಿ ಡೆಮೊ ಚಲಾಯಿಸಿ" : (lang === "hi" ? "एक क्लिक में डेमो चलाएं" : "Instant 1-Click Demo")}
        </h3>
        <p style={{ fontSize: "var(--font-size-sm)", color: "var(--text-muted)", marginBottom: "var(--space-md)" }}>
          {t.tryDemoSubtitle}
        </p>

        {/* Primary Try Demo Button */}
        <button
          type="button"
          className="btn btn-terracotta"
          onClick={() => onRunDemo("tailor")}
          style={{ marginBottom: "var(--space-md)" }}
        >
          <span>✨</span>
          <span>{t.tryDemoBtn} ({demoPersonaLabel})</span>
        </button>

        <p style={{ fontSize: "var(--font-size-sm)", fontWeight: "600", color: "var(--text-charcoal)", marginBottom: "var(--space-xs)" }}>
          {t.choosePersona}
        </p>

        {/* 3 Sample Persona Cards */}
        <div className="persona-grid">
          {/* Tailor Persona */}
          <div
            className="persona-card"
            onClick={() => onRunDemo("tailor")}
            role="button"
            tabIndex={0}
          >
            <div className="persona-icon">🧵</div>
            <div className="persona-name">
              {getPersonaName(personas.tailor)}
            </div>
            <div className="persona-role">
              {getPersonaRole(personas.tailor)} • 8y exp
            </div>
          </div>

          {/* Cook Persona */}
          <div
            className="persona-card"
            onClick={() => onRunDemo("cook")}
            role="button"
            tabIndex={0}
          >
            <div className="persona-icon">🍳</div>
            <div className="persona-name">
              {getPersonaName(personas.cook)}
            </div>
            <div className="persona-role">
              {getPersonaRole(personas.cook)} • 5y exp
            </div>
          </div>

          {/* Electrician Persona */}
          <div
            className="persona-card"
            onClick={() => onRunDemo("electrician")}
            role="button"
            tabIndex={0}
          >
            <div className="persona-icon">⚡</div>
            <div className="persona-name">
              {getPersonaName(personas.electrician)}
            </div>
            <div className="persona-role">
              {getPersonaRole(personas.electrician)} • 6y exp
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
