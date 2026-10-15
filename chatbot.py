from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

MODEL = "claude-sonnet-5-5"
SYSTEM_PROMPT = "Kısa ve samimi cevap veren bir Türkçe asistansın."

messages = []

print("🤖 Sohbet başladı! Çıkmak için 'exit' yaz.\n")

while True:
    try:
        user_input = input("Sen: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n👋 Görüşürüz!")
        break

    if user_input.lower() == "exit":
        print("👋 Görüşürüz!")
        break
    if not user_input:
        continue

    messages.append({"role": "user", "content": user_input})

    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    messages.append({"role": "assistant", "content": response.content})

    reply = "".join(block.text for block in response.content if block.type == "text")
    print(f"Claude: {reply}")
    print(f"   📊 input: {response.usage.input_tokens} · output: {response.usage.output_tokens}\n")