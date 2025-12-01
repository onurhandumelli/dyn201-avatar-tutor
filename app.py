import os
import tempfile

from google import genai

# GEMINI_API_KEY ortam değişkeninden gelecek.
# google-genai kütüphanesi, eğer GEMINI_API_KEY tanımlıysa
# client = genai.Client() çağrısında otomatik olarak kullanır.
# Burada yine de koruyucu bir kontrol ekleyelim.
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY bulunamadı. "
        "Streamlit Cloud > Settings > Secrets kısmına GEMINI_API_KEY eklemelisin."
    )

# Google GenAI client
client = genai.Client(api_key=API_KEY)

SYSTEM_PROMPT = """
Sen bir üniversite dersinde (Engineering Mechanics: Dynamics – DYN201)
öğrencilere yardım eden yapay zekâ asistanısın.

Amaç:
- Öğrenciye DYN201 konularında (kinematik, dinamik, serbest cisim diyagramı,
  Newton-Euler, enerji yöntemleri, simple control / PID / lead-lag vs.)
  adım adım yardımcı olmak.
- Öğrencinin çözüm sürecini desteklemek, fakat tam sınav çözümü vermemek.
- Her zaman önce öğrencinin düşünce sürecini anlamaya çalış, hatalarını
  nazikçe göster ve bir sonraki adımı nasıl düzelteceğini açıkla.

Kurallar:
- Cevaplarını TÜRKÇE ver; terimlerde İngilizce karşılığını parantez içinde
  verebilirsin (ör: damping ratio (sönüm oranı)).
- Eğer DYN201/CTMS referans dosyasında bir bilgi varsa, önce onu kullan;
  tamamen uydurma yapma.
- Emin olmadığın noktada “bu konuda emin değilim, ama genel prensip şu…”
  diyerek dürüst ol.
- Öğrencinin sorduğu soru dinamik veya kontrol dışına kayarsa kısaca cevapla,
  ama ana odağı DYN201 konularında tut.
"""


def dyn201_chat(history, user_message, extra_context=None):
    """
    history: Streamlit'ten gelen mesaj listesi (role, content).
    user_message: Son yazılan mesaj.
    extra_context: Kullanıcının eklediği ders notları (isteğe bağlı).
    """

    transcript_lines = []

    # 1) CTMS + DYN201 Knowledge File'i yükle
    try:
        with open("dyn201_refs.txt", "r", encoding="utf-8") as f:
            dyn201_refs = f.read()
    except Exception:
        dyn201_refs = ""

    # 2) Kullanıcı ders notlarını ekle (varsa)
    if extra_context:
        transcript_lines.append(
            "Kullanıcının kendi DYN201 ders notları:\n" + extra_context + "\n---\n"
        )

    # 3) Resmi CTMS/DYN201 referans metnini ekle
    if dyn201_refs:
        transcript_lines.append(
            "=== DYN201 & CTMS RESMI REFERANS BASLANGICI ===\n"
            + dyn201_refs +
            "\n=== DYN201 & CTMS RESMI REFERANS BITISI ===\n"
        )

    # 4) Sohbet geçmişini ekle
    for msg in history:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "user":
            prefix = "Öğrenci"
        else:
            prefix = "Asistan"
        transcript_lines.append(f"{prefix}: {content}")

    # 5) Öğrencinin son mesajını ekle
    transcript_lines.append(f"Öğrenci: {user_message}")

    # 6) Final prompt'u oluştur
    full_prompt = (
        SYSTEM_PROMPT
        + "\n\n"
        + "\n".join(transcript_lines)
        + "\nAsistan:"
    )

    # 7) Modelden yanıt iste
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=full_prompt,
    )

    # .text özelliği tüm adayları birleştirip tek bir metin verir
    return response.text


def check_solution(image_bytes, extra_instruction=None):
    """
    Öğrencinin defterinden çektiği çözüm fotoğrafını değerlendirir.

    image_bytes: Streamlit file_uploader'dan gelen binary içerik.
    extra_instruction: İsteğe bağlı ek açıklama / soru.
    """

    # Görseli geçici dosyaya yaz
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(image_bytes)
        tmp_path = tmp.name

      base_prompt = (
        "You are a teaching assistant for the course Engineering Mechanics: Dynamics (DYN201).\n"
        "The student uploaded an image that may contain one or more of the following:\n"
        " - a handwritten solution,\n"
        " - a dynamics problem statement / question,\n"
        " - a diagram or figure related to DYN201.\n"
        "Your job is to:\n"
        "1) First, understand what the image contains (solution, question, diagram or a mix).\n"
        "2) If it is mainly a question/problem statement, restate it briefly and explain how to start solving it.\n"
        "3) If it includes the student's solution steps, check them step by step and point out any mistakes.\n"
        "4) Always answer in TURKISH.\n"
        "5) Give kısa, yönlendirici ipuçları ver; fakat tam sınav çözümü yazma.\n"
    )


    if extra_instruction:
        base_prompt += "\nEk öğretmen notu / özel talimat:\n" + extra_instruction + "\n"

    # Dosyayı Gemini'ye yükle
    uploaded_file = client.files.upload(file=tmp_path)

    # Multimodal istek
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[base_prompt, uploaded_file],
    )

    return response.text
