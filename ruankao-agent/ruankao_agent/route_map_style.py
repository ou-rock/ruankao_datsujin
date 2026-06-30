from __future__ import annotations


ROUTE_MAP_STYLE = r""":root {
      color-scheme: light;
      --ink: #172026;
      --muted: #5e6b73;
      --line: #cfd8dc;
      --paper: #ffffff;
      --band: #f5f7f5;
      --accent: #0f766e;
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
    h1 {
      margin: 0;
      font-size: 28px;
      line-height: 1.2;
      letter-spacing: 0;
    }
    h2 {
      margin: 0 0 8px;
      font-size: 19px;
      line-height: 1.3;
    }
    .status {
      color: var(--muted);
      margin: 8px 0 0;
    }
    .priority {
      border: 1px solid var(--line);
      border-left: 4px solid var(--accent);
      border-radius: 8px;
      background: #ffffff;
      padding: 14px 16px;
      margin-bottom: 14px;
    }
    .priority span {
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 4px;
    }
    .priority strong {
      display: block;
      font-size: 18px;
      line-height: 1.25;
    }
    .priority p {
      margin: 6px 0 0;
      color: var(--muted);
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 12px;
    }
    .route {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--paper);
      padding: 16px;
    }
    .route-head {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
    }
    .route-head h2 {
      margin-bottom: 0;
    }
    .route-state {
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 3px 8px;
      font-size: 12px;
      font-weight: 700;
      white-space: nowrap;
      background: var(--band);
    }
    .route-state.red {
      color: #8a1f11;
      border-color: #f0b6ad;
      background: #fff1f0;
    }
    .route-state.yellow {
      color: #7a5600;
      border-color: #ead18a;
      background: #fff8db;
    }
    .route-state.green {
      color: #17623a;
      border-color: #a9d5b8;
      background: #eefaf1;
    }
    .metrics {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
      margin-top: 10px;
    }
    .metric {
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--band);
      padding: 10px;
    }
    .metric span {
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 4px;
    }
    .metric strong {
      display: block;
      font-size: 18px;
      line-height: 1.25;
    }
    .meta {
      color: var(--muted);
      font-size: 12px;
      margin-top: 8px;
    }
    .route-foot {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 10px;
    }
    .route-foot span {
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #fff;
      color: var(--muted);
      padding: 5px 8px;
      font-size: 12px;
    }"""
