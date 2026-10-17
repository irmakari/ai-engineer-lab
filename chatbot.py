from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

MODEL = "claude-sonnet-5-5"
SYSTEM_PROMPT = "Kısa ve samimi cevap veren bir Türkçe asistansın."

# 1M token başına USD
PRICING = {
    "claude-sonnet-5-5": {"input": 2.00, "output": 10.00},
    "claude-haiku-5-5": {"input": 0.10, "output": 0.50},
}


def calculate_cost(model, input_tokens, output_tokens):
    price = PRICING[model]
    return (input_tokens * price["input"] + output_tokens * price["output"]) / 1_000_000


messages = []

total_cost = 0.0

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

    print("Claude: ", end="", flush=True)
    with client.messages.stream(
        model=MODEL,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
        response = stream.get_final_message()
    print()

    messages.append({"role": "assistant", "content": response.content})

    cost = calculate_cost(MODEL, response.usage.input_tokens, response.usage.output_tokens)
    total_cost += cost
    print(f"   📊 input: {response.usage.input_tokens} · output: {response.usage.output_tokens} · 💸 ${cost:.6f} · toplam: ${total_cost:.6f}\n")