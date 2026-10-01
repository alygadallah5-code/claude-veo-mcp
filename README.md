# Claude → Veo 3.1 MCP

هذا المشروع يجعل Claude قادرًا على استدعاء Google Veo 3.1 عبر Gemini API باستخدام Remote MCP.

## الأدوات

- `generate_video`: يولّد فيديو وينتظر حتى يكتمل.
- `start_video_generation`: يبدأ التوليد ويعيد رقم العملية.
- `check_generation`: يفحص العملية ويعيد رابط الفيديو عند اكتمالها.
- `create_ad_video`: يحوّل فكرة إعلان بسيطة إلى prompt إعلاني احترافي ثم يولّد الفيديو.

## 1) احصل على Gemini API key

أنشئ مفتاحًا من Google AI Studio، ثم ضعه في متغير البيئة:

`GEMINI_API_KEY`

لا تضع المفتاح داخل `server.py` ولا ترسله إلى Claude.

## 2) شغّل السيرفر

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python server.py
```

للاستخدام المحلي سيكون endpoint عادة:

`http://localhost:8000/mcp`

لكن Claude على السحابة لا يستطيع الوصول إلى localhost مباشرة.

## 3) للنشر مع Claude

ارفع المشروع إلى GitHub ثم انشره على Render/Railway/Fly.io أو أي استضافة Python عامة.
يجب أن يكون السيرفر متاحًا عبر HTTPS على الإنترنت.

بعد النشر، استخدم:

`https://YOUR-DOMAIN/mcp`

داخل Claude:
Customize → Connectors → + → Add custom connector

ثم ضع رابط `/mcp`.

## 4) اختبار سريع داخل Claude

بعد تفعيل الـ connector، جرّب:

"استخدم create_ad_video واعمل إعلان 8 ثواني لبودي كيك، لقطة ماكرو للكريمة والشوكولاتة، حركة كاميرا دائرية، إضاءة فاخرة، مناسب Reels."

## ملاحظات

- Veo 3.1 يولّد فيديوهات قصيرة، وواجهة Gemini API الحالية تدعم 8 ثوانٍ مع 720p/1080p/4K حسب الإعدادات.
- روابط الفيديو الناتجة من Google مؤقتة، لذلك احفظ الفيديو فورًا.
- هذا الإصدار يبدأ بـ Text-to-Video. يمكن إضافة Image-to-Video وreference images في إصدار لاحق.
