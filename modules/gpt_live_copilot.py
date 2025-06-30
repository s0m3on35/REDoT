import os
import openai
import pyttsx3
import asyncio
import websockets
import threading
import readline
import re

CONFIG_FILE = "config/openai_key.txt"
LOG_FILE = "logs/gpt_live_copilot.log"
WS_URI = "ws://localhost:8765"

os.makedirs("config", exist_ok=True)
os.makedirs("logs", exist_ok=True)

if not os.path.exists(CONFIG_FILE):
    print("Missing OpenAI key at config/openai_key.txt")
    exit(1)

with open(CONFIG_FILE, "r") as f:
    openai.api_key = f.read().strip()

tts = pyttsx3.init()
ws_queue = []

def is_prompt_injection(query):
    if re.search(r"(?i)ignore.*instructions|pretend.*assistant|you are not", query):
        return True
    return False

def suggest_repair(query):
    if "error" in query.lower() or "fail" in query.lower():
        return "Try restarting the module or check logs under /logs."
    return ""

async def ws_stream():
    async with websockets.connect(WS_URI) as ws:
        while True:
            if ws_queue:
                msg = ws_queue.pop(0)
                await ws.send(msg)
            await asyncio.sleep(0.1)

def start_ws_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(ws_stream())

threading.Thread(target=start_ws_thread, daemon=True).start()

print(" RedOT Live Copilot – GPT Interface (type 'exit' to quit)")
chat = [{"role": "system", "content": "You are a secure red team copilot for embedded and robotic systems. Provide concise, professional advice only."}]

while True:
    try:
        query = input("You> ").strip()
    except (EOFError, KeyboardInterrupt):
        break

    if query.lower() == "exit":
        break

    if is_prompt_injection(query):
        print("Copilot> Input rejected due to potential prompt injection.")
        ws_queue.append("Copilot> Prompt blocked.")
        continue

    chat.append({"role": "user", "content": query})
    try:
        response = openai.ChatCompletion.create(model="gpt-4", messages=chat)
        reply = response['choices'][0]['message']['content'].strip()
        chat.append({"role": "assistant", "content": reply})
        print("Copilot>", reply)
        ws_queue.append(f"Copilot> {reply}")
        tts.say(reply)
        tts.runAndWait()
        repair = suggest_repair(reply)
        if repair:
            print("Fix>", repair)
            ws_queue.append(f"Fix> {repair}")
        with open(LOG_FILE, "a") as log:
            log.write(f"You> {query}\nCopilot> {reply}\n\n")
    except Exception as e:
        print("Error:", e)
