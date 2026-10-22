import json
from typing import Literal

from dotenv import load_dotenv
import anthropic
from pydantic import BaseModel, Field, ValidationError

load_dotenv()
client = anthropic.Anthropic()

MODEL = "claude-sonnet-5-5"


class ReviewAnalysis(BaseModel):
    duygu: Literal["olumlu", "olumsuz", "nötr"] = Field(
        description=(
            "olumlu: müşteri memnun. "
            "olumsuz: müşteri memnun değil (övüyor gibi görünüp ironi yapsa bile). "
            "nötr: duygu yok ya da övgü ile şikâyet dengede."
        )
    )
    konu: Literal["kargo", "kalite", "fiyat", "satıcı", "diğer"] = Field(
        description="Yorumun ana konusu"
    )
    puan_1_5: int = Field(
        ge=1, le=5, description="Müşterinin muhtemelen vereceği yıldız puanı"
    )
    ozet: str = Field(description="Yorumun en fazla 10 kelimelik özeti")


PROMPT = """Bir e-ticaret müşteri yorumunu analiz ediyorsun.

Şu alanlarla bir JSON nesnesi döndür:
- duygu: "olumlu", "olumsuz" ya da "nötr"
- konu: yorumun ana konusu (ör. kargo, kalite, fiyat, satıcı)
- puan_1_5: müşterinin muhtemel puanı, 1 ile 5 arası tam sayı
- ozet: yorumun tek cümlelik özeti

Sadece JSON döndür.

<yorum>
{review}
</yorum>"""


def analyze(review, max_retries=1):
    messages = [{"role": "user", "content": PROMPT.format(review=review)}]

    for attempt in range(max_retries + 1):
        message = client.messages.create(
            model=MODEL,
            max_tokens=1000,
            output_config={"effort": "low"},
            messages=messages,
        )
        raw = next(b.text for b in message.content if b.type == "text")

        try:
            return ReviewAnalysis.model_validate_json(raw)
        except ValidationError as e:
            print(f"⚠️ Deneme {attempt + 1} geçersiz:\n{e}\n")
            messages.append({"role": "assistant", "content": raw})
            messages.append({
                "role": "user",
                "content": f"Bu JSON şemaya uymuyor. Hata:\n{e}\n\nDüzeltip sadece JSON döndür.",
            })

    raise ValueError(f"{max_retries + 1} denemede geçerli JSON alınamadı: {review}")

def analyze_native(review):
    message = client.messages.parse(
        model=MODEL,
        max_tokens=1000,
        output_config={"effort": "low"},
        output_format=ReviewAnalysis,
        messages=[{"role": "user", "content": f"Bu müşteri yorumunu analiz et:\n<yorum>\n{review}\n</yorum>"}],
    )
    return message.parsed_output

REVIEWS = [
    "Kargo ertesi gün geldi, ürün tam anlatıldığı gibi. Bayıldım!",
    "Kalitesi çok iyi, fiyatına göre beklentimin üstünde.",
    "İki gün kullandım, şarj girişi bozuldu. Param çöpe gitti.",
    "Satıcı mesajlarıma hiç dönmedi, iade de alamadım.",
    "Harika, üçüncü kez bozuk geldi. Tebrikler gerçekten 👏",
    "Ne diyeyim, tam 'kaliteli' ürün... bir haftada parçalandı.",
    "Ürün güzel ama kargo 2 hafta sürdü.",
    "Tasarımı şık ama pil ancak yarım gün gidiyor.",
    "Ürün dün teslim edildi.",
    "Siparişi 3 adet olarak verdim.",
]

valid = 0
for review in REVIEWS:
    try:
        r = analyze_native(review)
        valid += 1
        print(f"✅ {r.duygu:8} | {r.konu:10} | {r.puan_1_5} | {r.ozet}")
    except ValueError as e:
        print(f"❌ {e}")

print(f"\nGeçerli JSON: {valid}/{len(REVIEWS)}")