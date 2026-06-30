from __future__ import annotations

from html import escape

from .web_controls import _front_checks
from .web_lists import _card_list, _practice_list
from .web_page_view import HomePageView


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
