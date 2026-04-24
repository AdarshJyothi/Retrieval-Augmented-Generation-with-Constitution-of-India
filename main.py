# main.py

import threading
import time

import gradio as gr
import requests
import uvicorn

from pipeline.app import app

import os
from huggingface_hub import login

login(token=os.environ["HF_TOKEN"])



# ─────────────────────────────────────────────
# FastAPI server — runs in a background thread
# ─────────────────────────────────────────────

def run_fastapi():
    """Start the FastAPI server on port 8000."""
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


# ─────────────────────────────────────────────
# Gradio UI — calls the FastAPI /ask endpoint
# ─────────────────────────────────────────────

def ask_question(query: str) -> tuple[str, str]:
    """
    Send the query to FastAPI /ask and return
    the answer and formatted sources.
    """
    if not query.strip():
        return "Please enter a question.", ""

    try:
        response = requests.post(
            "http://localhost:8000/ask",
            json={"query": query},
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()

        answer = data["answer"]

        # Format sources into a readable string
        sources_text = ""
        for i, src in enumerate(data["sources"], 1):
            sources_text += (
                f"[{i}] {src['section']}"
                + (f" — {src['chapter']}" if src.get("chapter") and str(src["chapter"]) not in ("0", "nan") else "")
                + f"\nScore: {src['score']}\n{src['text'][:300]}...\n\n"
            )

        return answer, sources_text.strip()

    except requests.exceptions.ConnectionError:
        return "Server not ready yet. Please wait a moment and try again.", ""
    except Exception as e:
        return f"Error: {str(e)}", ""


def build_ui() -> gr.Blocks:
    """Build and return the Gradio UI."""
    with gr.Blocks(title="Indian Constitution RAG") as demo:
        gr.Markdown("# 🇮🇳 Indian Constitution Q&A")
        gr.Markdown("Ask any question about the Indian Constitution.")

        with gr.Row():
            query_box = gr.Textbox(
                label="Your Question",
                placeholder="e.g. What is Article 21?",
                lines=2,
                scale=4,
            )
            submit_btn = gr.Button("Ask", variant="primary", scale=1)

        answer_box = gr.Textbox(label="Answer", lines=6, interactive=False)
        sources_box = gr.Textbox(label="Sources", lines=10, interactive=False)

        submit_btn.click(
            fn=ask_question,
            inputs=query_box,
            outputs=[answer_box, sources_box],
        )
        query_box.submit(
            fn=ask_question,
            inputs=query_box,
            outputs=[answer_box, sources_box],
        )

    return demo


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":

    # Start FastAPI in a background thread
    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()

    # Wait for FastAPI to be ready before launching Gradio
    print("Waiting for FastAPI to start...")
    while True:
        try:
            requests.get("http://localhost:8000/health", timeout=2)
            print("FastAPI is ready.")
            break
        except Exception:
            time.sleep(1)

    # Launch Gradio on port 7860
    demo = build_ui()
    demo.launch(server_name="0.0.0.0", server_port=7860)