from __future__ import annotations


WORKBENCH_HOME_STYLE = r""":root {
  color-scheme: light;
  --ink: #172026;
  --muted: #5e6b73;
  --line: #cfd8dc;
  --paper: #ffffff;
  --band: #f4f7f5;
  --accent: #0f766e;
  --accent-ink: #063f3b;
  --warn: #b45309;
  --danger: #b91c1c;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: var(--ink);
  background: #fbfcfb;
}
.skip-link {
  position: absolute;
  left: 12px;
  top: 12px;
  transform: translateY(-160%);
  border: 1px solid var(--accent);
  border-radius: 6px;
  background: #fff;
  color: var(--accent-ink);
  padding: 8px 10px;
  font-weight: 750;
  text-decoration: none;
  z-index: 10;
}
.skip-link:focus {
  transform: translateY(0);
}
header {
  border-bottom: 1px solid var(--line);
  background: var(--paper);
}
.top {
  max-width: 1280px;
  margin: 0 auto;
  padding: 20px 24px;
  display: grid;
  gap: 14px;
}
.title-row {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}
h1 {
  margin: 0;
  font-size: 28px;
  line-height: 1.2;
  letter-spacing: 0;
}
.status {
  font-size: 14px;
  color: var(--muted);
}
.metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(148px, 1fr));
  gap: 10px;
}
.metric {
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 10px 12px;
  background: var(--band);
  min-height: 68px;
}
.metric span {
  display: block;
  color: var(--muted);
  font-size: 12px;
  margin-bottom: 5px;
}
.metric strong {
  display: block;
  font-size: 18px;
  line-height: 1.25;
}
.action-strip {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  border: 1px solid var(--line);
  border-left: 5px solid var(--accent);
  border-radius: 8px;
  background: #fff;
  padding: 12px 14px;
}
.action-strip.risk-red { border-left-color: var(--danger); }
.action-strip.risk-yellow { border-left-color: var(--warn); }
.action-kicker {
  color: var(--muted);
  font-size: 12px;
  font-weight: 750;
  margin-bottom: 4px;
}
.action-title {
  font-size: 18px;
  font-weight: 800;
  line-height: 1.35;
}
.action-reason {
  color: var(--muted);
  font-size: 13px;
  line-height: 1.45;
  margin-top: 4px;
}
.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-end;
}
.front-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}
.front-card {
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
  padding: 10px 12px;
  display: grid;
  gap: 8px;
  min-height: 116px;
}
.front-card.red { border-top: 4px solid var(--danger); }
.front-card.yellow { border-top: 4px solid var(--warn); }
.front-card.green { border-top: 4px solid var(--accent); }
.front-head {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  align-items: baseline;
  font-weight: 800;
}
.front-state {
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 2px 7px;
  font-size: 12px;
  font-weight: 750;
  white-space: nowrap;
  background: var(--band);
}
.front-state.red {
  color: #8a1f11;
  border-color: #f0b6ad;
  background: #fff1f0;
}
.front-state.yellow {
  color: #7a5600;
  border-color: #ead18a;
  background: #fff8db;
}
.front-state.green {
  color: #17623a;
  border-color: #a9d5b8;
  background: #eefaf1;
}
.front-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 6px;
}
.front-mini {
  background: var(--band);
  border-radius: 6px;
  padding: 6px;
  min-height: 46px;
}
.front-mini span {
  display: block;
  color: var(--muted);
  font-size: 10px;
  line-height: 1.1;
}
.front-mini strong {
  display: block;
  font-size: 15px;
  line-height: 1.35;
}
.front-action {
  color: var(--accent-ink);
  font-size: 12px;
  font-weight: 750;
  line-height: 1.35;
}
main {
  max-width: 1280px;
  margin: 0 auto;
  padding: 18px 24px 48px;
  display: grid;
  grid-template-columns: minmax(220px, 280px) minmax(0, 1fr);
  gap: 18px;
  align-items: start;
}
aside {
  position: sticky;
  top: 14px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--paper);
  padding: 12px;
}
aside a {
  display: block;
  padding: 9px 10px;
  border-radius: 6px;
  color: var(--accent-ink);
  text-decoration: none;
  font-weight: 600;
}
aside a:hover { background: var(--band); }
.content {
  display: grid;
  gap: 16px;
}
section {
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--paper);
  padding: 16px;
}
h2 {
  margin: 0 0 12px;
  font-size: 19px;
  line-height: 1.3;
}
h3 {
  margin: 0 0 8px;
  font-size: 15px;
  line-height: 1.3;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
}
form {
  display: grid;
  gap: 10px;
}
label {
  display: grid;
  gap: 5px;
  font-size: 13px;
  color: var(--muted);
  font-weight: 600;
}
.field {
  display: grid;
  gap: 5px;
}
.field-label {
  font-size: 13px;
  color: var(--muted);
  font-weight: 600;
}
.form-note {
  border: 1px solid var(--line);
  border-radius: 6px;
  background: var(--band);
  color: var(--muted);
  padding: 10px 12px;
  font-size: 13px;
  line-height: 1.45;
}
.source-guide {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(118px, 1fr));
  gap: 6px;
  margin-top: 6px;
}
.source-guide span {
  border: 1px solid var(--line);
  border-radius: 6px;
  background: #fff;
  color: var(--muted);
  padding: 7px 8px;
  font-size: 12px;
  line-height: 1.35;
}
.source-guide strong {
  color: var(--accent-ink);
}
input, textarea, select {
  width: 100%;
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 9px 10px;
  font: inherit;
  color: var(--ink);
  background: #fff;
}
textarea {
  min-height: 92px;
  resize: vertical;
  line-height: 1.45;
}
.checks {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.checks label {
  display: inline-flex;
  grid-template-columns: none;
  align-items: center;
  gap: 6px;
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 6px 9px;
  background: var(--band);
}
.checks input { width: auto; }
.segmented {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 6px;
}
.segmented.flow {
  grid-template-columns: repeat(auto-fit, minmax(96px, 1fr));
}
.segmented label {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-height: 40px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: #fff;
  color: var(--accent-ink);
  cursor: pointer;
  font-size: 13px;
  text-align: center;
}
.segmented input {
  width: auto;
  margin: 0;
  accent-color: var(--accent);
}
button, .button {
  appearance: none;
  border: 1px solid var(--accent);
  border-radius: 6px;
  background: var(--accent);
  color: #fff;
  font: inherit;
  font-weight: 700;
  padding: 9px 12px;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  justify-content: center;
  align-items: center;
  min-height: 40px;
}
.button.secondary, button.secondary {
  border-color: var(--line);
  color: var(--accent-ink);
  background: #fff;
}
.grade-row {
  display: grid;
  grid-template-columns: repeat(6, minmax(44px, 1fr));
  gap: 6px;
  margin-top: 8px;
}
.grade-button {
  border-color: var(--line);
  background: #fff;
  color: var(--accent-ink);
  min-height: 46px;
  padding: 6px 4px;
  display: grid;
  gap: 2px;
  justify-items: center;
  align-content: center;
}
.grade-button span {
  font-size: 15px;
  line-height: 1;
}
.grade-button small {
  color: var(--muted);
  font-size: 10px;
  line-height: 1;
}
.grade-button.low {
  color: var(--danger);
}
.grade-button:hover {
  border-color: var(--accent);
  background: var(--band);
}
.message {
  border: 1px solid #99f6e4;
  background: #ecfdf5;
  color: #065f46;
  border-radius: 6px;
  padding: 10px 12px;
  font-weight: 650;
}
.list {
  display: grid;
  gap: 10px;
}
.item {
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 10px;
  background: #fff;
}
.item-title {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  font-weight: 750;
}
.meta {
  color: var(--muted);
  font-size: 12px;
  line-height: 1.45;
  margin-top: 4px;
}
.meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 6px;
}
.meta-row span {
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--band);
  color: var(--muted);
  padding: 4px 7px;
  font-size: 12px;
  line-height: 1.2;
}
.empty {
  color: var(--muted);
  border: 1px dashed var(--line);
  border-radius: 6px;
  padding: 12px;
  background: var(--band);
}
.split {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 14px;
}
.footer-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}
.operation-stack {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 10px;
  margin-top: 10px;
}
.operation-form {
  border: 1px solid var(--line);
  border-radius: 6px;
  background: var(--band);
  padding: 10px;
  display: grid;
  gap: 8px;
}
.operation-form button {
  width: 100%;
}
.operation-hint {
  color: var(--muted);
  font-size: 12px;
  line-height: 1.4;
}
@media (max-width: 820px) {
  main { grid-template-columns: 1fr; padding: 14px 14px 40px; }
  aside { position: static; }
  .top { padding: 18px 14px; }
  h1 { font-size: 24px; }
  .action-strip { grid-template-columns: 1fr; }
  .action-buttons { justify-content: stretch; }
  .action-buttons .button { width: 100%; }
  .front-strip { grid-template-columns: 1fr; }
}
"""
