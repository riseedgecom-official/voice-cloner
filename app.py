"""
Voice Cloner: clone a voice from a short sample and speak new text with it.

Uses Coqui XTTS-v2 (multilingual, ~6-30 seconds of clean audio is enough).
Only clone voices you own or have explicit permission to use.

Run:
    pip install -r requirements.txt
    python app.py
Then open http://127.0.0.1:7860
"""

import os
import tempfile

import gradio as gr
import torch
from TTS.api import TTS

MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"

LANGUAGES = [
    ("English", "en"),
    ("Spanish", "es"),
    ("French", "fr"),
    ("German", "de"),
    ("Italian", "it"),
    ("Portuguese", "pt"),
    ("Polish", "pl"),
    ("Turkish", "tr"),
    ("Russian", "ru"),
    ("Dutch", "nl"),
    ("Czech", "cs"),
    ("Arabic", "ar"),
    ("Chinese", "zh-cn"),
    ("Japanese", "ja"),
    ("Hungarian", "hu"),
    ("Korean", "ko"),
    ("Hindi", "hi"),
]

device = "cuda" if torch.cuda.is_available() else "cpu"

# The first run downloads the model (~2 GB) and asks you to accept its
# license in this terminal. The XTTS model is for non-commercial use.
print(f"Loading XTTS-v2 on {device}...")
tts = TTS(MODEL_NAME).to(device)
print("Model ready.")


def clone_voice(sample_path, text, language, consent):
    if not consent:
        raise gr.Error("Please confirm you have permission to use this voice.")
    if not sample_path:
        raise gr.Error("Upload or record a voice sample first.")
    if not text or not text.strip():
        raise gr.Error("Enter the text you want spoken.")

    out_path = os.path.join(tempfile.mkdtemp(), "cloned_voice.wav")
    tts.tts_to_file(
        text=text.strip(),
        speaker_wav=sample_path,
        language=language,
        file_path=out_path,
    )
    return out_path


with gr.Blocks(title="Voice Cloner") as demo:
    gr.Markdown(
        "# Voice Cloner\n"
        "Upload or record **6-30 seconds** of clear speech (no music or "
        "background noise), type some text, and hear it in that voice."
    )

    with gr.Row():
        with gr.Column():
            sample = gr.Audio(
                label="Voice sample",
                sources=["upload", "microphone"],
                type="filepath",
            )
            language = gr.Dropdown(
                choices=LANGUAGES, value="en", label="Language of the text"
            )
            text = gr.Textbox(
                label="Text to speak",
                lines=5,
                placeholder="Type what you want the cloned voice to say...",
            )
            consent = gr.Checkbox(
                label="I own this voice or have the speaker's permission to clone it."
            )
            go = gr.Button("Generate", variant="primary")

        with gr.Column():
            output = gr.Audio(label="Cloned voice", type="filepath")

    go.click(clone_voice, [sample, text, language, consent], output)

if __name__ == "__main__":
    # On Cloud Run, PORT is set for you. Set APP_USER and APP_PASSWORD to
    # require a login (strongly recommended for anything public).
    user = os.environ.get("APP_USER")
    password = os.environ.get("APP_PASSWORD")
    demo.launch(
        server_port=int(os.environ.get("PORT", 7860)),
        auth=(user, password) if user and password else None,
    )
