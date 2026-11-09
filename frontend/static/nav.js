/* P2S — Shared Navigation, Language Switcher & Utilities */

const I18N = {
  en: {
    home: 'Home',
    triage: 'Triage',
    services: 'Services',
    dashboard: 'Dashboard',
    history: 'History',
    about: 'About',
    admin: 'Admin',
    prototype_badge: '● Live',
    footer_text: 'P2S — Problem to Service · MSc Thesis · Emergency: 112 · Medical On-Call: 116 117 · API Docs',
    triage_title: "What's your problem?",
    triage_subtitle: 'Describe what happened in plain German or English.',
    situation_label: 'Describe your situation',
    situation_placeholder: '',
    voice_btn: 'Voice Dictation',
    voice_listening: 'Listening... Speak now',
    analyse_btn: '🔍 Analyse & Route Problem',
    shortcut_hint: 'Ctrl+Enter to submit',
    quick_clarification: 'One quick clarification',
    clarification_sub: 'This ensures we route you to the exact responsible office or helpline.',
    or_type_details: 'Or type your specific details:',
    continue_btn: '→ Continue Triage',
    action_plan_title: '📋 Immediate Action Plan',
    recommended_services_title: '🔗 Verified Berlin Services & Helplines',
    new_triage_btn: '↩ New Triage',
    save_plan_btn: '💾 Save Action Plan',
    export_pdf_btn: '📄 Export Official PDF / Print',
    emergency_title: 'URGENT SAFETY HAZARD',
    chips: [
      '🏢 Hausmeister not responding, need electrical room for fuse',
      '🏠 Landlord kept my Kaution deposit 8 months after move-out',
      '🏛️ Student visa expires next week, no LEA appointment available',
      '⚡ Sudden power blackout across the whole street in Berlin',
      '🏥 Severe migraine on Sunday, need an on-call doctor',
      '🚨 I smell gas near my basement',
      '🛡️ Gym contract renewed automatically without my consent'
    ]
  },
  de: {
    home: 'Startseite',
    triage: 'Triage',
    services: 'Dienste',
    dashboard: 'Statistik',
    history: 'Verlauf',
    about: 'Über P2S',
    admin: 'Admin',
    prototype_badge: '● Online',
    footer_text: 'P2S — Problem to Service · Masterarbeit · Notruf: 112 · Ärztlicher Bereitschaftsdienst: 116 117 · API Docs',
    triage_title: 'Was ist Ihr Anliegen / Problem?',
    triage_subtitle: 'Beschreiben Sie Ihre Situation in einfachen Worten.',
    situation_label: 'Ihre Problemschilderung',
    situation_placeholder: '',
    voice_btn: 'Spracheingabe',
    voice_listening: 'Höre zu... Bitte sprechen',
    analyse_btn: '🔍 Problem analysieren & leiten',
    shortcut_hint: 'Strg+Enter zum Absenden',
    quick_clarification: 'Eine kurze Rückfrage',
    clarification_sub: 'Dies stellt sicher, dass wir Sie an die zuständige Stelle oder Notdienst leiten.',
    or_type_details: 'Oder eigene Details eingeben:',
    continue_btn: '→ Weiter zur Lösung',
    action_plan_title: '📋 Sofortiger Maßnahmenplan',
    recommended_services_title: '🔗 Verifizierte Berliner Behörden & Hilfsstellen',
    new_triage_btn: '↩ Neuer Vorgang',
    save_plan_btn: '💾 Plan speichern',
    export_pdf_btn: '📄 Offiziellen Maßnahmenplan drucken (PDF)',
    emergency_title: 'AKUTE GEFAHR / NOTFALL',
    chips: [
      '🏢 Hausmeister reagiert nicht, Stromraum für Sicherung verschlossen',
      '🏠 Vermieter zahlt Mietkaution nach 8 Monaten nicht zurück',
      '🏛️ Studentenvisum läuft bald ab, kein Termin beim LEA Berlin',
      '⚡ Plötzlicher Stromausfall im gesamten Straßenzug',
      '🏥 Starke Migräne am Sonntag, brauche Bereitschaftsarzt',
      '🚨 Gasgeruch im Kellerbereich bemerkt',
      '🛡️ Fitnessstudio-Vertrag ungewollt automatisch verlängert'
    ]
  }
};

let currentLang = localStorage.getItem('p2s_lang') || 'en';

function setLanguage(lang) {
  currentLang = lang;
  localStorage.setItem('p2s_lang', lang);
  buildNav();
  if (typeof updatePageLanguage === 'function') {
    updatePageLanguage(lang);
  }
}

const NAV_LINKS = [
  { href: '/',           icon: '🏠', key: 'home' },
  { href: '/triage',     icon: '🔍', key: 'triage' },
  { href: '/services',   icon: '📂', key: 'services' },
  { href: '/dashboard',  icon: '📊', key: 'dashboard' },
  { href: '/history',    icon: '📜', key: 'history' },
  { href: '/about',      icon: 'ℹ️',  key: 'about' },
  { href: '/admin',      icon: '⚙️',  key: 'admin' },
];

function buildNav() {
  const current = window.location.pathname.replace(/\/$/, '') || '/';
  const nav = document.getElementById('p2s-nav');
  if (!nav) return;

  const t = I18N[currentLang] || I18N.en;

  nav.innerHTML = `
    <a class="nav-logo" href="/">
      <div class="nav-logo-icon">P</div>
      P2S
    </a>
    <div class="nav-links">
      ${NAV_LINKS.map(l => {
        const href = l.href === '/' ? '/' : l.href;
        const isActive = (href === '/' ? current === '/' : current === href);
        return `<a class="nav-link ${isActive ? 'active' : ''}" href="${l.href}">
          <span>${l.icon}</span>
          <span class="nav-text">${t[l.key] || l.key}</span>
        </a>`;
      }).join('')}
    </div>

    <!-- Active Region Badge -->
    <div style="display:flex;align-items:center;gap:4px;background:var(--bg-2);border:1px solid var(--border);border-radius:99px;padding:3px 10px;font-size:0.75rem;font-weight:700;color:var(--text-2);margin-right:4px;">
      <span>📍</span>
      <span>Berlin, DE</span>
    </div>

    <!-- Language Switcher Pill -->
    <div style="display:flex;align-items:center;background:var(--bg-2);border:1px solid var(--border);border-radius:99px;padding:2px 4px;margin-right:8px;font-size:0.75rem;font-weight:700;">
      <button onclick="setLanguage('en')" style="border:none;background:${currentLang==='en'?'var(--brand)':'transparent'};color:${currentLang==='en'?'#fff':'var(--muted)'};padding:3px 8px;border-radius:99px;cursor:pointer;font-family:inherit;transition:all .15s;">EN</button>
      <button onclick="setLanguage('de')" style="border:none;background:${currentLang==='de'?'var(--brand)':'transparent'};color:${currentLang==='de'?'#fff':'var(--muted)'};padding:3px 8px;border-radius:99px;cursor:pointer;font-family:inherit;transition:all .15s;">DE</button>
    </div>

    <span class="nav-badge" style="background:var(--success-bg);color:#16A34A;">${t.prototype_badge}</span>
  `;
}

function buildFooter() {
  const footer = document.getElementById('p2s-footer');
  if (!footer) return;
  const t = I18N[currentLang] || I18N.en;
  footer.innerHTML = `
    ${t.footer_text}
  `;
}

/* Toast notifications */
function showToast(msg, duration = 3000) {
  let t = document.getElementById('toast');
  if (!t) {
    t = document.createElement('div');
    t.id = 'toast';
    document.body.appendChild(t);
  }
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), duration);
}

/* Format ISO timestamp nicely */
function fmtTime(iso) {
  const d = new Date(iso);
  const locale = currentLang === 'de' ? 'de-DE' : 'en-GB';
  return d.toLocaleDateString(locale, { day:'2-digit', month:'short', year:'numeric' })
       + ' · ' + d.toLocaleTimeString(locale, { hour:'2-digit', minute:'2-digit' });
}

/* Urgency tag HTML */
function urgencyTag(u) {
  const map = {
    Low:                 ['tag-success', '🟢', currentLang==='de'?'Niedrig':'Low'],
    Medium:              ['tag-warn',    '🟡', currentLang==='de'?'Mittel':'Medium'],
    High:                ['tag-danger',  '🔴', currentLang==='de'?'Hoch':'High'],
    CRITICAL_EMERGENCY:  ['tag-danger',  '🚨', currentLang==='de'?'AKUTER NOTFALL':'CRITICAL EMERGENCY']
  };
  const [cls, icon, label] = map[u] || ['tag-neutral', '⚪', u];
  return `<span class="tag ${cls}">${icon} ${label}</span>`;
}

/* Domain tag HTML */
function domainTag(d) {
  const icons = {
    'Facility & Building Emergencies': '🏢',
    'Tenancy & Housing Law':           '🏠',
    'Health & Medical Care':           '🏥',
    'Bureaucracy & Immigration':       '🏛️',
    'Utilities & Energy Crises':       '⚡',
    'Consumer Protection & Contracts': '🛡️',
    'IT, Telecom & Connectivity':      '💻',
    'Home Appliances & Craftspeople':  '🔧'
  };
  return `<span class="tag tag-brand">${icons[d] || '📂'} ${d}</span>`;
}

/* Run on load */
document.addEventListener('DOMContentLoaded', () => {
  buildNav();
  buildFooter();
  if (typeof updatePageLanguage === 'function') {
    updatePageLanguage(currentLang);
  }
});
