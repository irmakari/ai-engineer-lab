from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

QUESTION = "Bir kedi kafesi için tek kelimelik yaratıcı bir isim öner. Sadece ismi yaz."

for temp in [0, 1]:
    print(f"\n🌡️ temperature = {temp}")
    for i in range(3):
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1000,
            extra_body={"temperature": temp},
            messages=[{"role": "user", "content": QUESTION}],
        )
        reply = "".join(b.text for b in response.content if b.type == "text")
        print(f"   {i + 1}. {reply.strip()}")