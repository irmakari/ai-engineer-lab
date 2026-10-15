from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=1000,
    messages=[
        {"role": "user", "content": "Selam Claude! Bana LLM'lerin nasıl çalıştığını anlatır mısın?"},
    ],
)

for block in message.content:
    if block.type == "thinking":
        print("💭 Düşünce:", block.thinking)
        print()
    elif block.type == "text":
        print(block.text)
        
if message.stop_reason == "max_tokens":
    print("\n⚠️ Cevap yarım kaldı! max_tokens'ı artır.")
        
print("---")
print("Durma sebebi:", message.stop_reason)
print("Token kullanımı:", message.usage)