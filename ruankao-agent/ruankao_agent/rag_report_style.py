from __future__ import annotations


RAG_REPORT_STYLE = r""":root {
      color-scheme: light;
      --ink: #172026;
      --muted: #5e6b73;
      --line: #cfd8dc;
      --paper: #ffffff;
      --band: #f5f7f5;
      --accent: #0f766e;
      --danger: #b91c1c;
      --warn: #b45309;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: #fbfcfb;
      line-height: 1.55;
    }
    main {
      max-width: 1120px;
      margin: 0 auto;
      padding: 24px 20px 48px;
    }
    header {
      border-bottom: 1px solid var(--line);
      padding-bottom: 18px;
      margin-bottom: 16px;
    }
    h1 { margin: 0; font-size: 28px; line-height: 1.2; letter-spacing: 0; }
    h2 { margin: 0 0 12px; font-size: 19px; line-height: 1.3; }
    section {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--paper);
      padding: 16px;
      margin-top: 14px;
    }
    .lead { color: var(--muted); margin: 8px 0 0; }
    .item {
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--band);
      padding: 11px;
    }
    .list { display: grid; gap: 10px; }
    .meta-row { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
    .meta-row span {
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #fff;
      color: var(--muted);
      padding: 4px 7px;
      font-size: 12px;
    }
    .red { border-left: 4px solid var(--danger); }
    .yellow { border-left: 4px solid var(--warn); }
    .green { border-left: 4px solid var(--accent); }"""
