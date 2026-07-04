"""
IntelliQuery-RAG — Gradio application.

Provides a rich, dark-themed UI for:
  • Entering complex questions
  • Watching the agent graph execute step-by-step
  • Viewing the reasoning trace and final answer

Launch:
    python -m ui.app
"""

from __future__ import annotations

import gradio as gr

from ui.components import format_reasoning_trace, render_mermaid_graph

_CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

* { font-family: 'Outfit', sans-serif !important; }

body, .gradio-container {
    background-color: #0b0f19 !important;
    color: #e2e8f0 !important;
}

.gradio-container {
    max-width: 1200px !important;
    margin: auto !important;
    padding-top: 2rem !important;
}

.header-banner {
    background: rgba(30, 41, 59, 0.4);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 40px;
    margin-bottom: 30px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    position: relative;
    overflow: hidden;
}

.header-banner::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%; width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(129, 140, 248, 0.1) 0%, transparent 50%);
    z-index: 0;
    pointer-events: none;
}

.header-banner > * {
    position: relative;
    z-index: 1;
}

.header-banner h1 {
    background: linear-gradient(135deg, #38bdf8, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5rem;
    font-weight: 700;
    margin: 0 0 12px 0;
    letter-spacing: -0.02em;
}

.header-banner p {
    color: #94a3b8;
    font-size: 1.1rem;
    margin: 0;
    font-weight: 300;
}

/* Glassmorphism panels */
.gradio-container .form, .gradio-container .panel {
    background: rgba(30, 41, 59, 0.4) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 16px !important;
    box-shadow: 0 10px 30px -10px rgba(0,0,0,0.3) !important;
    backdrop-filter: blur(10px) !important;
}

/* Inputs */
textarea {
    background: rgba(15, 23, 42, 0.6) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: #fff !important;
    transition: all 0.3s ease !important;
}
textarea:focus {
    border-color: #818cf8 !important;
    box-shadow: 0 0 0 2px rgba(129, 140, 248, 0.2) !important;
}

/* Buttons */
button.primary {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 12px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4) !important;
}
button.primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(99, 102, 241, 0.6) !important;
}
button.secondary {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #e2e8f0 !important;
    border-radius: 12px !important;
    transition: all 0.3s ease !important;
}
button.secondary:hover {
    background: rgba(255,255,255,0.1) !important;
    transform: translateY(-2px) !important;
}

/* Badges */
.status-badge {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 30px;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    transition: all 0.3s ease;
}
.status-idle {
    background: rgba(30, 41, 59, 0.8);
    color: #94a3b8;
    border: 1px solid rgba(148, 163, 184, 0.2);
}
.status-running {
    background: rgba(59, 130, 246, 0.15);
    color: #60a5fa;
    border: 1px solid rgba(96, 165, 250, 0.3);
    animation: pulse 2s infinite;
}
.status-done {
    background: rgba(34, 197, 94, 0.15);
    color: #4ade80;
    border: 1px solid rgba(74, 222, 128, 0.3);
}

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(96, 165, 250, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(96, 165, 250, 0); }
    100% { box-shadow: 0 0 0 0 rgba(96, 165, 250, 0); }
}

/* Mermaid Graph Enlarge */
.mermaid, .mermaid svg {
    width: 100% !important;
    min-height: 400px !important;
    max-width: none !important;
}

/* Tabs */
.tabs {
    border: none !important;
    background: transparent !important;
    margin-top: 24px !important;
}
.tab-nav {
    border-bottom: 1px solid rgba(255,255,255,0.1) !important;
    margin-bottom: 16px !important;
}
.tab-nav button {
    border: none !important;
    color: #94a3b8 !important;
    font-weight: 500 !important;
    padding: 12px 24px !important;
    transition: all 0.3s ease !important;
}
.tab-nav button.selected {
    color: #fff !important;
    background: transparent !important;
    border-bottom: 2px solid #818cf8 !important;
}
.tab-nav button:hover {
    color: #e2e8f0 !important;
}
"""


def _build_ui() -> gr.Blocks:
    """Construct the full Gradio Blocks application."""

    with gr.Blocks(
        title="IntelliQuery-RAG",
    ) as app:

        # ── Header ──────────────────────────────────────────────────────
        gr.HTML("""
        <div class="header-banner">
            <h1>🧠 IntelliQuery-RAG</h1>
            <p>Intelligent Graph-Orchestrated RAG Agent &mdash;
               Ask complex multi-step questions over your documents.</p>
        </div>
        """)

        # ── State ───────────────────────────────────────────────────────
        state = gr.State(value={
            "current_node": None,
            "reasoning_trace": [],
            "final_response": None,
        })

        # ── Input & Controls ────────────────────────────────────────────
        with gr.Row():
            with gr.Column(scale=3):
                question_input = gr.Textbox(
                    label="Your Question",
                    placeholder=(
                        "e.g., Why did Duke Leto accept the posting to "
                        "Arrakis despite knowing it was a trap?"
                    ),
                    lines=2,
                    elem_id="question-input",
                )
            with gr.Column(scale=1):
                status_text = gr.Markdown(
                    value='<span class="status-badge status-idle">⏸ Idle</span>',
                    elem_id="status-display",
                )
                run_btn = gr.Button("🚀 Run Agent", variant="primary", size="lg")
                clear_btn = gr.Button("🗑️ Clear", variant="secondary")

        # ── Graph Workflow (Full Width) ─────────────────────────────────
        gr.Markdown("### ⚙️ Agent Execution Workflow")
        graph_display = gr.Markdown(
            value=f"```mermaid\n{render_mermaid_graph()}\n```",
            elem_id="graph-display",
        )

        # ── Output panels ────────────────────────────────────────────────
        with gr.Tabs():
            with gr.TabItem("💡 Final Answer", id="answer-tab"):
                answer_output = gr.Markdown(
                    value="_Submit a question to get started._",
                    elem_id="answer-output",
                )

            with gr.TabItem("🧠 Reasoning Trace", id="trace-tab"):
                trace_output = gr.Markdown(
                    value="_No reasoning steps yet._",
                    elem_id="trace-output",
                )

            with gr.TabItem("📊 Execution Plan", id="plan-tab"):
                plan_output = gr.Markdown(
                    value="_Plan will appear here after the agent starts._",
                    elem_id="plan-output",
                )

        # ── Event handlers ───────────────────────────────────────────────

        def run_agent(question: str, current_state: dict):
            """Execute the agent graph and yield progressive updates."""
            if not question.strip():
                yield (
                    current_state,
                    f"```mermaid\n{render_mermaid_graph()}\n```",
                    '<span class="status-badge status-idle">⚠️ Enter a question first</span>',
                    "_No answer yet._",
                    "_No reasoning steps yet._",
                    "_No plan yet._",
                )
                return

            # Attempt to load and run the agent graph
            try:
                from intelliquery.agents.graph import build_agent_graph
                from intelliquery.config import load_settings

                settings = load_settings()
                agent = build_agent_graph(settings)

                yield (
                    current_state,
                    f"```mermaid\n{render_mermaid_graph('anonymize_query')}\n```",
                    '<span class="status-badge status-running">🔄 Running…</span>',
                    "_Agent is working…_",
                    "_Reasoning in progress…_",
                    "_Generating plan…_",
                )

                result = agent.invoke({"query": question})

                # Format outputs
                final_answer = result.get("final_response", "_No answer generated._")
                trace = result.get("reasoning_trace", [])
                plan = result.get("execution_plan", [])

                plan_md = "### 📋 Execution Plan\n\n"
                for step in plan:
                    icon = "🔍" if step.get("action") == "RETRIEVE" else "💭"
                    action = step['action']
                    desc = step['description']
                    plan_md += (
                        f"{icon} **Step {step['step']}** "
                        f"[{action}]: {desc}\n\n"
                    )

                updated_state = {
                    "current_node": "synthesize_response",
                    "reasoning_trace": trace,
                    "final_response": final_answer,
                }

                yield (
                    updated_state,
                    f"```mermaid\n{render_mermaid_graph('synthesize_response')}\n```",
                    '<span class="status-badge status-done">✅ Complete</span>',
                    f"### 💡 Answer\n\n{final_answer}",
                    format_reasoning_trace(trace),
                    plan_md,
                )

            except FileNotFoundError as e:
                yield (
                    current_state,
                    f"```mermaid\n{render_mermaid_graph()}\n```",
                    '<span class="status-badge status-idle">⚠️ Setup needed</span>',
                    f"### ⚠️ Vector Stores Not Found\n\n{e}\n\n"
                    "Run the `notebooks/intelliquery_tutorial.ipynb` notebook first "
                    "to build the vector stores from your PDF.",
                    "_N/A_",
                    "_N/A_",
                )
            except Exception as e:
                yield (
                    current_state,
                    f"```mermaid\n{render_mermaid_graph()}\n```",
                    '<span class="status-badge status-idle">❌ Error</span>',
                    f"### ❌ Error\n\n```\n{e}\n```",
                    "_N/A_",
                    "_N/A_",
                )

        def clear_all():
            """Reset the UI to initial state."""
            empty_state = {
                "current_node": None,
                "reasoning_trace": [],
                "final_response": None,
            }
            return (
                "",
                empty_state,
                f"```mermaid\n{render_mermaid_graph()}\n```",
                '<span class="status-badge status-idle">⏸ Idle</span>',
                "_Submit a question to get started._",
                "_No reasoning steps yet._",
                "_Plan will appear here after the agent starts._",
            )

        run_btn.click(
            fn=run_agent,
            inputs=[question_input, state],
            outputs=[state, graph_display, status_text, answer_output, trace_output, plan_output],
        )

        clear_btn.click(
            fn=clear_all,
            outputs=[
                question_input, state, graph_display,
                status_text, answer_output,
                trace_output, plan_output,
            ],
        )

        # ── Footer ──────────────────────────────────────────────────────
        gr.HTML("""
        <div style="text-align:center; padding:24px 0 8px; color:#64748b; font-size:0.85rem;">
            IntelliQuery-RAG &middot; Built by jay14 &middot;
            <a href="https://github.com/jay14/IntelliQuery-RAG"
               style="color:#818cf8; text-decoration:none;">GitHub</a>
        </div>
        """)

    return app


def main():
    """Entry point for ``python -m ui.app``."""
    app = _build_ui()
    app.launch(
        server_port=7860,
        share=False,
        theme=gr.themes.Soft(
            primary_hue="indigo",
            secondary_hue="slate",
            neutral_hue="slate",
        ),
        css=_CUSTOM_CSS,
    )


if __name__ == "__main__":
    main()
