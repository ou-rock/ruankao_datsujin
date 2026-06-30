from __future__ import annotations

from html import escape

from .web_page_view import HomePageView
from .web_render import (
    _card_list,
    _front_checks,
    _practice_list,
    _promotion_status_radios,
    _relation_radios,
)


def render_today_operations(view: HomePageView) -> str:
    return f"""
        <div class="operation-stack" aria-label="今日产物生成">
          <form class="operation-form" method="post" action="/daily/receipt">
            <input type="hidden" name="as_of" value="{escape(view.today.isoformat())}">
            <button type="submit">生成日结回执</button>
            <div class="operation-hint">收束完成、缺口和明日最低动作。</div>
          </form>
          <form class="operation-form" method="post" action="/night/evolve">
            <input type="hidden" name="as_of" value="{escape(view.today.isoformat())}">
            <button type="submit">生成夜间进化草案</button>
            <div class="operation-hint">让系统在晚上整理卡片、风险和下一步。</div>
          </form>
          <form class="operation-form" method="post" action="/routes/map">
            <input type="hidden" name="as_of" value="{escape(view.today.isoformat())}">
            <button type="submit">生成三题型覆盖图</button>
            <div class="operation-hint">检查选择、案例、论文是否失衡。</div>
          </form>
          <form class="operation-form" method="post" action="/rag/brief">
            <input type="hidden" name="as_of" value="{escape(view.today.isoformat())}">
            <input type="hidden" name="query" value="{escape(view.rag_query)}">
            <button type="submit">生成 RAG 控制简报</button>
            <div class="operation-hint">召回记忆证据，并指出进步闸门。</div>
          </form>
          <form class="operation-form" method="post" action="/state/export">
            <input type="hidden" name="as_of" value="{escape(view.today.isoformat())}">
            <button type="submit">导出本地状态 JSON</button>
            <div class="operation-hint">保存本地状态，方便迁移、审计和回滚。</div>
          </form>
        </div>
        <div class="footer-actions">{view.receipt_link}{view.evolution_link}{view.route_link}{view.rag_link}{view.export_link}</div>"""


def render_cheko_section(view: HomePageView) -> str:
    return f"""
  <section id="cheko">
    <h2>学习信号</h2>
    <div class="split">
      <div>
        <h3>Cheko 入队</h3>
        <div class="metrics">
          <div class="metric"><span>Cheko 记忆卡</span><strong>{len(view.cheko_cards)}</strong></div>
          <div class="metric"><span>今日到期</span><strong>{len(view.cheko_due_cards)}</strong></div>
        </div>
        <form method="post" action="/cheko/cards" style="margin-top:10px;">
          <input type="hidden" name="next_due" value="{escape(view.today.isoformat())}">
          <button type="submit">把 Cheko 弱点入队</button>
        </form>
        <div class="footer-actions">
          <a class="button secondary" href="/learning/cheko-sync.html">同步信号</a>
          <a class="button secondary" href="/learning/today.html">今日三任务</a>
        </div>
      </div>
      <div>
        <h3>最近 Cheko 卡片</h3>
        {_card_list(view.cheko_cards[-4:], with_review=False, today=view.today)}
      </div>
    </div>
  </section>"""


def render_practice_section(view: HomePageView) -> str:
    return f"""
  <section id="practice">
    <h2>练习记录</h2>
    <div class="split">
      <form method="post" action="/practice">
        <div class="form-note">记录一次练习至少留下题型、得分或完成量、错因，以及下一步补救动作；这样三题型雷达和夜间进化才有材料可用。</div>
        <div class="grid">
          <div class="field">
            <div class="field-label">题型</div>
            <div class="segmented" aria-label="练习题型">
              <label><input type="radio" name="front" value="choice" checked>选择题</label>
              <label><input type="radio" name="front" value="case">案例题</label>
              <label><input type="radio" name="front" value="essay">论文题</label>
            </div>
          </div>
          <label>日期
            <input type="date" name="created_on" value="{escape(view.today.isoformat())}">
          </label>
        </div>
        <label>主题
          <input name="topic" required placeholder="系统架构设计错题 / 项目背景段">
        </label>
        <div class="grid">
          <label>得分
            <input type="number" name="score" min="0" step="0.5" inputmode="decimal">
          </label>
          <label>满分
            <input type="number" name="max_score" min="1" step="0.5" inputmode="decimal">
          </label>
          <label>耗时分钟
            <input type="number" name="duration_minutes" min="1" step="1" inputmode="numeric">
          </label>
        </div>
        <label>来源
          <input name="source" placeholder="Cheko / 真题 / 自写">
        </label>
        <label>练习摘要
          <textarea name="summary" required placeholder="得分点、卡点、暴露出的知识边界"></textarea>
        </label>
        <label>错因 / 卡点
          <textarea name="mistakes" placeholder="错因、混淆项、下一次避免方式"></textarea>
        </label>
        <button type="submit">记录练习</button>
      </form>
      <div>
        <h3>最近练习</h3>
        {_practice_list(view.practice_sessions[-8:])}
      </div>
    </div>
  </section>"""


def render_study_turn_section(view: HomePageView) -> str:
    return f"""
  <section id="study-turn">
    <h2>学习回合</h2>
    <form method="post" action="/study-turn">
      <div class="form-note">把一次苏格拉底式问答沉淀为一条 Mein 和一条 Du；外部证据仍走 Uns，原则链接交给夜间进化挖掘。</div>
      <label>主题
        <input name="topic" required placeholder="高可用场景 / ATAM / 缓存一致性">
      </label>
      <div class="grid">
        <label>我在哪
          <input name="learner_position" placeholder="知道概念名，但不会写可评分场景">
        </label>
        <label>你在哪
          <input name="codex_position" placeholder="ruankao-teach 追问者 / 案例教练">
        </label>
        <label>我们要去哪
          <input name="destination" placeholder="能写出刺激、响应和响应度量">
        </label>
      </div>
      <label>Mein：我的原话 / 我的答案
        <textarea name="user_text" required placeholder="先保留粗糙答案，不急着美化"></textarea>
      </label>
      <label>Du：Codex 的整理 / 纠偏 / 追问
        <textarea name="assistant_text" required placeholder="复述卡点、补结构，并只留下一个下一步追问"></textarea>
      </label>
      {_front_checks()}
      <button type="submit">记录学习回合</button>
    </form>
  </section>"""


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
