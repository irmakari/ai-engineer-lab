from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

MODEL = "claude-sonnet-5-5"

REVIEWS = [
    # net olumlu
    ("Kargo ertesi gün geldi, ürün tam anlatıldığı gibi. Bayıldım!", "olumlu"),
    ("Kalitesi çok iyi, fiyatına göre beklentimin üstünde.", "olumlu"),
    # net olumsuz
    ("İki gün kullandım, şarj girişi bozuldu. Param çöpe gitti.", "olumsuz"),
    ("Satıcı mesajlarıma hiç dönmedi, iade de alamadım.", "olumsuz"),
    # ironi
    ("Harika, üçüncü kez bozuk geldi. Tebrikler gerçekten 👏", "olumsuz"),
    ("Ne diyeyim, tam 'kaliteli' ürün... bir haftada parçalandı.", "olumsuz"),
    # karışık duygu
    ("Ürün güzel ama kargo 2 hafta sürdü.", "nötr"),
    ("Tasarımı şık ama pil ancak yarım gün gidiyor.", "nötr"),
    # düz bilgi
    ("Ürün dün teslim edildi.", "nötr"),
    ("Siparişi 3 adet olarak verdim.", "nötr"),
]

HARD_REVIEWS = [
    ("Eh işte.", "nötr"),
    ("Ürün güzel ama kargo felaketti, bir daha asla bu satıcıdan almam.", "olumsuz"),
    ("Fiyatı biraz yüksek ama değer, herkese tavsiye ederim.", "olumlu"),
    ("Çok hızlı geldi, sadece 3 hafta 🐢👏", "olumsuz"),
    ("Honestly not bad, ama beklediğim gibi de değil.", "nötr"),
]


def classify_v1(review):
    message = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        output_config={"effort": "low"},
        messages=[
            {"role": "user", "content": f"Bu yorum olumlu mu, olumsuz mu, nötr mü? {review}"},
        ],
    )
    for block in message.content:
        if block.type == "text":
            return block.text.strip()


PROMPT_V2 = """Bir e-ticaret sitesindeki müşteri yorumlarını duygu durumuna göre sınıflandırıyorsun.

Etiketler:
- olumlu: müşteri memnun
- olumsuz: müşteri memnun değil (övüyor gibi görünüp ironi yapsa bile)
- nötr: duygu yok ya da övgü ile şikâyet dengede

Yorum <yorum> etiketlerinin içinde. Cevap olarak sadece etiketi yaz: olumlu, olumsuz ya da nötr. Açıklama ekleme.

<yorum>
{review}
</yorum>"""


def classify_v2(review):
    message = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        output_config={"effort": "low"},
        messages=[
            {"role": "user", "content": PROMPT_V2.format(review=review)},
        ],
    )
    for block in message.content:
        if block.type == "text":
            return block.text.strip()

PROMPT_V3 = """Bir e-ticaret sitesindeki müşteri yorumlarını duygu durumuna göre sınıflandırıyorsun.

Etiketler:
- olumlu: müşteri memnun
- olumsuz: müşteri memnun değil (övüyor gibi görünüp ironi yapsa bile)
- nötr: duygu yok ya da övgü ile şikâyet dengede

Örnekler:
<ornek>
<yorum>Paketleme çok özenliydi, satıcıya teşekkürler.</yorum>
<etiket>olumlu</etiket>
</ornek>
<ornek>
<yorum>Süper, kutuyu açtım içi boş çıktı. Eline sağlık kargo 🙃</yorum>
<etiket>olumsuz</etiket>
</ornek>
<ornek>
<yorum>Kumaşı kaliteli ama bedeni küçük geldi.</yorum>
<etiket>nötr</etiket>
</ornek>

Yorum <yorum> etiketlerinin içinde. Cevap olarak sadece etiketi yaz: olumlu, olumsuz ya da nötr. Açıklama ekleme.

<yorum>
{review}
</yorum>"""


def classify_v3(review):
    message = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        output_config={"effort": "low"},
        messages=[
            {"role": "user", "content": PROMPT_V3.format(review=review)},
        ],
    )
    for block in message.content:
        if block.type == "text":
            return block.text.strip()

def score(classify, reviews):
    correct = 0
    for review, expected in reviews:
        answer = classify(review)
        is_correct = answer.lower() == expected
        if is_correct:
            correct += 1
        print(f"{'✅' if is_correct else '❌'} beklenen: {expected:8} | model: {answer[:40]!r}")
    return correct


print("=== V2 · zor set ===")
v2 = score(classify_v2, HARD_REVIEWS)
print("\n=== V3 · zor set ===")
v3 = score(classify_v3, HARD_REVIEWS)

total = len(HARD_REVIEWS)
print(f"\nZor set → V2: {v2}/{total} · V3: {v3}/{total}")