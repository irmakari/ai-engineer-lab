from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

MODEL = "claude-sonnet-5-5"

TEXTS = {
    "🇹🇷 Türkçe": (
        "Yapay zekâ asistanları konuşmaları hatırlamaz. Uygulama, her mesajda "
        "bütün geçmişi modele yeniden gönderir. Bu yüzden sohbet uzadıkça "
        "her istek biraz daha pahalı hale gelir."
    ),
    "🇬🇧 English": (
        "AI assistants do not remember conversations. The application resends "
        "the entire history to the model with every message. That is why each "
        "request becomes a bit more expensive as the chat grows longer."
    ),
}

for label, text in TEXTS.items():
    result = client.messages.count_tokens(
        model=MODEL,
        messages=[{"role": "user", "content": text}],
    )
    print(f"{label}: {len(text)} karakter · {result.input_tokens} token")