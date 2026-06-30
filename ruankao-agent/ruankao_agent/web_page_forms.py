from __future__ import annotations

from html import escape

from .web_controls import (
    _front_checks,
    _promotion_status_radios,
    _relation_radios,
)
from .web_card_lists import _card_list
from .web_page_view import HomePageView


def render_capture_section() -> str:
    return f"""
  <section id="capture">
    <h2>三源录入</h2>
    <form method="post" action="/records">
      <div class="grid">
        <div class="field">
          <div class="field-label">来源</div>
          <div class="segmented" aria-label="三源来源">
            <label><input type="radio" name="source" value="mein" checked>Mein</label>
            <label><input type="radio" name="source" value="du">Du</label>
            <label><input type="radio" name="source" value="uns">Uns</label>
          </div>
          <div class="source-guide" aria-label="三源边界">
            <span><strong>Mein：</strong>我的原话和卡点</span>
            <span><strong>Du：</strong>Codex 的整理和纠偏</span>
            <span><strong>Uns：</strong>外界资料和证据</span>
          </div>
        </div>
        <div class="field">
          <div class="field-label">状态</div>
          <div class="segmented flow" aria-label="三源状态">
            {_promotion_status_radios()}
          </div>
        </div>
      </div>
      <label>原文 / 灵感 / 对话摘录
        <textarea name="text" required placeholder="保留原话、文章摘录、对话片段或个人经验"></textarea>
      </label>
      <label>一句话摘要
        <textarea name="summary" required placeholder="一句话写清它为什么值得留下"></textarea>
      </label>
      <label>主题，每行一个
        <textarea name="topics" placeholder="质量属性&#10;架构评估"></textarea>
      </label>
      {_front_checks()}
      <button type="submit">沉淀到三源库</button>
    </form>
  </section>"""


def render_cards_section(view: HomePageView) -> str:
    return f"""
  <section id="cards">
    <h2>记忆卡</h2>
    <div class="split">
      <form method="post" action="/cards">
        <div class="form-note">一张合格记忆卡要能触发回忆、能自评、能映射到选择/案例/论文；如果只是摘抄，先回三源库沉淀。</div>
        <div class="grid">
          <label>类型
            <select name="card_type">
              <option value="concept">概念卡</option>
              <option value="principle">原则卡</option>
              <option value="comparison">对比卡</option>
              <option value="scenario">场景卡</option>
              <option value="expression">表达卡</option>
            </select>
          </label>
          <label>下次复习
            <input type="date" name="next_due" value="{escape(view.today.isoformat())}">
          </label>
        </div>
        <label>标题
          <input name="title" required>
        </label>
        <label>问题 / 适用场景
          <textarea name="prompt" required placeholder="看到什么场景时要想起这张卡？"></textarea>
        </label>
        <label>答案 / 核心表述
          <textarea name="answer" required placeholder="可直接检索的答案、原则或表达"></textarea>
        </label>
        <label>关联原始材料 ID
          <input type="number" name="source_record_id" min="1" step="1" inputmode="numeric">
        </label>
        <label>冲突原则，每行一个。仅原则卡使用
          <textarea name="conflicts" placeholder="技术先行&#10;性能优先"></textarea>
        </label>
        {_front_checks(default_all=True)}
        <button type="submit">创建记忆卡</button>
      </form>
      <div>
        <h3>最近卡片</h3>
        {_card_list(view.cards[-8:], with_review=False, today=view.today)}
      </div>
    </div>
  </section>"""


def render_principles_section(view: HomePageView) -> str:
    return f"""
  <section id="principles">
    <h2>原则网络</h2>
    <div class="split">
      <form method="post" action="/relations">
        <div class="form-note">只连接有真实逻辑张力的原则：能说明支撑、制约、冲突或派生，才值得进入网络。</div>
        <div class="grid">
          <label>From 原则 ID
            <input type="number" name="from_card_id" min="1" step="1" inputmode="numeric" required>
          </label>
          <label>To 原则 ID
            <input type="number" name="to_card_id" min="1" step="1" inputmode="numeric" required>
          </label>
        </div>
        <div class="field">
          <div class="field-label">关系</div>
          <div class="segmented flow" aria-label="原则关系">
            {_relation_radios()}
          </div>
        </div>
        <label>为什么这样连接
          <textarea name="rationale" required placeholder="说明这两个原则如何支撑、制约、冲突或派生"></textarea>
        </label>
        <button type="submit">连接原则</button>
      </form>
      <div>
        <h3>原则卡 ID</h3>
        {_card_list(view.principle_cards, with_review=False, today=view.today)}
      </div>
    </div>
  </section>"""


def render_vault_section(view: HomePageView) -> str:
    return f"""
  <section id="vault">
    <h2>Obsidian 与总图</h2>
    <div class="list">
      <div class="item">
        <div class="item-title">Vault 路径</div>
        <div class="meta">{escape(str(view.vault_path))}</div>
      </div>
      <div class="item">
        <div class="item-title">原则网络</div>
        <div class="meta"><a href="/vault/00-map/原则网络.md">vault/00-map/原则网络.md</a></div>
      </div>
      <div class="item">
        <div class="item-title">战役总图</div>
        <div class="meta"><a href="/vault/00-map/战役总图.md">vault/00-map/战役总图.md</a></div>
      </div>
    </div>
    <div class="footer-actions">
      <a class="button secondary" href="/learning/">打开学习台</a>
      <a class="button secondary" href="/dashboard.html">打开静态 HTML 总图</a>
      <a class="button secondary" href="/api/status">查看状态 JSON</a>
      {view.export_link}
    </div>
    <form method="post" action="/vault/sync" style="margin-top:10px;">
      <button type="submit">同步记忆卡到 Obsidian</button>
    </form>
    <form method="post" action="/vault/sync-raw" style="margin-top:10px;">
      <button type="submit">同步三源材料到 Obsidian</button>
    </form>
  </section>"""
