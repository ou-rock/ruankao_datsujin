from __future__ import annotations

from html import escape

from .web_page_view import HomePageView


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
