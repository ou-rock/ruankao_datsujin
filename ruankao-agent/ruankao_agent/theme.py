from __future__ import annotations


THEME_HEAD_SCRIPT = r"""<script>
(() => {
  const key = "ruankao-theme";
  let stored = null;
  try {
    stored = localStorage.getItem(key);
  } catch (_error) {
    stored = null;
  }
  const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  document.documentElement.dataset.theme =
    stored === "dark" || stored === "light" ? stored : (prefersDark ? "dark" : "light");
})();
</script>"""


THEME_TOGGLE = """<button class="theme-toggle" type="button" data-theme-toggle aria-label="切换黑夜模式" title="切换黑夜模式" aria-pressed="false">夜</button>"""


THEME_SCRIPT = r"""<script>
(() => {
  const key = "ruankao-theme";
  const root = document.documentElement;
  const toggles = () => Array.from(document.querySelectorAll("[data-theme-toggle]"));
  const readStored = () => {
    try {
      return localStorage.getItem(key);
    } catch (_error) {
      return null;
    }
  };
  const writeStored = (theme) => {
    try {
      localStorage.setItem(key, theme);
    } catch (_error) {
      return;
    }
  };
  const preferred = () => {
    const stored = readStored();
    if (stored === "dark" || stored === "light") return stored;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  };
  const apply = (theme) => {
    root.dataset.theme = theme;
    toggles().forEach((toggle) => {
      const dark = theme === "dark";
      toggle.setAttribute("aria-pressed", dark ? "true" : "false");
      toggle.setAttribute("aria-label", dark ? "切换日间模式" : "切换黑夜模式");
      toggle.setAttribute("title", dark ? "切换日间模式" : "切换黑夜模式");
      toggle.textContent = dark ? "日" : "夜";
    });
  };
  document.addEventListener("DOMContentLoaded", () => {
    apply(preferred());
    toggles().forEach((toggle) => {
      toggle.addEventListener("click", () => {
        const next = root.dataset.theme === "dark" ? "light" : "dark";
        writeStored(next);
        apply(next);
      });
    });
  });
})();
</script>"""


THEME_STYLE = r""":root {
  color-scheme: light;
  --canvas: #fbfcfb;
  --input: #ffffff;
  --chip: #ffffff;
  --accent-ink: #0f766e;
  --message-bg: #ecfdf5;
  --message-ink: #065f46;
  --shadow: rgba(15, 23, 42, 0.10);
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --ink: #e8eef0;
  --muted: #a7b7be;
  --line: #33464d;
  --paper: #10191d;
  --panel: #162126;
  --band: #17242a;
  --canvas: #0a0f12;
  --input: #0d1519;
  --chip: #142026;
  --accent: #2dd4bf;
  --accent-ink: #a7f3d0;
  --warn: #fbbf24;
  --danger: #fb7185;
  --amber: #fbbf24;
  --message-bg: #0b3128;
  --message-ink: #bbf7d0;
  --shadow: rgba(0, 0, 0, 0.35);
}
body {
  background: var(--canvas);
  color: var(--ink);
}
.theme-toggle {
  position: fixed;
  top: 12px;
  right: 12px;
  z-index: 50;
  width: 40px;
  height: 40px;
  min-height: 40px;
  padding: 0;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: var(--paper);
  color: var(--accent-ink);
  box-shadow: 0 8px 22px var(--shadow);
  font: 700 16px/1 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
.theme-toggle:hover,
.theme-toggle:focus {
  border-color: var(--accent);
  outline: none;
}
input, textarea, select {
  background: var(--input);
  color: var(--ink);
}
.button.secondary,
button.secondary,
.source-guide span,
.segmented label,
.grade-button,
.meta-row span,
.status-row span,
.metric,
.panel,
.item,
.priority,
.action-strip,
.front-card,
.route,
section,
aside,
header {
  border-color: var(--line);
}
:root[data-theme="dark"] .button.secondary,
:root[data-theme="dark"] button.secondary,
:root[data-theme="dark"] .source-guide span,
:root[data-theme="dark"] .segmented label,
:root[data-theme="dark"] .grade-button,
:root[data-theme="dark"] .meta-row span,
:root[data-theme="dark"] .status-row span {
  background: var(--chip);
  color: var(--accent-ink);
}
:root[data-theme="dark"] .message {
  background: var(--message-bg);
  border-color: #166534;
  color: var(--message-ink);
}
:root[data-theme="dark"] header,
:root[data-theme="dark"] section,
:root[data-theme="dark"] aside,
:root[data-theme="dark"] .hero,
:root[data-theme="dark"] .action-strip,
:root[data-theme="dark"] .front-card,
:root[data-theme="dark"] .route,
:root[data-theme="dark"] .priority {
  background: var(--paper);
}
:root[data-theme="dark"] .metric,
:root[data-theme="dark"] .panel,
:root[data-theme="dark"] .item,
:root[data-theme="dark"] .front-mini,
:root[data-theme="dark"] .operation-form,
:root[data-theme="dark"] .route-step,
:root[data-theme="dark"] .day,
:root[data-theme="dark"] .form-note,
:root[data-theme="dark"] .empty,
:root[data-theme="dark"] .route-state,
:root[data-theme="dark"] .front-state {
  background: var(--band);
}
:root[data-theme="dark"] input,
:root[data-theme="dark"] textarea,
:root[data-theme="dark"] select {
  background: var(--input);
  border-color: var(--line);
  color: var(--ink);
}
:root[data-theme="dark"] .front-state.red,
:root[data-theme="dark"] .route-state.red {
  color: #fecdd3;
  border-color: #7f1d1d;
  background: #3f1118;
}
:root[data-theme="dark"] .front-state.yellow,
:root[data-theme="dark"] .route-state.yellow {
  color: #fde68a;
  border-color: #854d0e;
  background: #3a2606;
}
:root[data-theme="dark"] .front-state.green,
:root[data-theme="dark"] .route-state.green {
  color: #bbf7d0;
  border-color: #166534;
  background: #0d2d1c;
}
@media (max-width: 720px) {
  .theme-toggle {
    top: 10px;
    right: 10px;
  }
}"""
