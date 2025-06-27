# gpt_live_copilot.py
import openai

openai.api_key = "YOUR_OPENAI_KEY"

print("🤖 RedOT Live Copilot (type 'exit' to quit)")
while True:
    query = input("You> ")
    if query.strip().lower() == "exit":
        break
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a red team assistant for embedded OT systems."},
                {"role": "user", "content": query}
            ]
        )
        print("Copilot>", response['choices'][0]['message']['content'].strip(), "\n")
    except Exception as e:
        print("❌ Error:", e)
