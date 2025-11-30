import os
import tempfile

from google import genai

# GEMINI_API_KEY, Streamlit Cloud "Secrets" içinden gelecek.
# Boş gelirse hata vermesin diye basit bir kontrol ekleyelim.
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY bulunamadı. "
        "Streamlit Cloud > Settings > Secrets kısmına GEMINI_API_KEY eklemelisin."
    )

# Google GenAI client
# Burası resmi dokümandaki kullanım şekline göre ayarlandı. 
client = genai.Client(api_key=API_KEY)

SYSTEM_PROMPT = """
You are a strict but kind teaching assistant for MEF University course DYN201 (Dynamics).

- Explain in Turkish unless the student explicitly asks for English.
- Always show the solution STEP BY STEP.
- After each step, briefly check for typical DYN201 mistakes
  (sign errors, wrong reference frame, wrong units, missing free-body diagram, etc.).
- If the student sends a photo of their notebook solution, carefully check it line by line.
- Keep answers focused on the current question, don't change the topic.
"""


def dyn201_chat(history, user_message, extra_context=None):
    """
    history: Streamlit'ten gelen mesaj listesi (role, content).
    user_message: Son yazdığın mesaj (string).
    extra_context: Hocanın notlarından senin koyduğun ek metin (string veya None).
    """

    transcript_lines = []

    # Ek ders notlarını başa ekleyelim (isteğe bağlı)
    if extra_context:
        transcript_lines.append(
            "Ders notları / PDF özetleri:\n" + extra_context + "\n---\n"
        )

    # Sohbet geçmişini plain text olarak modele veriyoruz
    for msg in history:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            prefix = "Öğrenci"
        else:
            prefix = "Asistan"
        transcript_lines.append(f"{prefix}: {content}")

    # Son kullanıcı mesajını da ekle
    transcript_lines.append(f"Öğrenci: {user_message}")

    full_prompt = SYSTEM_PROMPT + "\n\n" + "\n".join(transcript_lines) + "\nAsistan:"

    response = client.models.generate_content(
        model="gemini-2.0-flash",  # hızlı ve ucuz model 
        contents=full_prompt,
    )

    return response.text


def check_solution(image_file):
    """
    image_file: Streamlit'in file_uploader'dan verdiği UploadedFile objesi.

    Adımlar:
      1) Dosyayı geçici bir klasöre kaydediyoruz.
      2) Gemini'ye upload ediyoruz.
      3) Çözümü DYN201 bakış açısıyla değerlendir diyerek yorum istiyoruz.
    """

    # UploadedFile -> geçici dosya yolu
    with tempfile.NamedTemporaryFile(delete=False, suffix=image_file.name) as tmp:
        tmp.write(image_file.getbuffer())
        tmp_path = tmp.name

    grading_prompt = (
        "You are grading a DYN201 (Dynamics) exam solution written by a student "
        "on paper (photo). The image contains equations and steps.\n\n"
        "Tasks:\n"
        "1) First say briefly if the FINAL RESULT seems correct or not.\n"
        "2) Then list specific mistakes, line by line, with short explanations.\n"
        "3) Finally, explain to the student (in Turkish) which ONE OR TWO steps "
        "they should fix next, without giving the full final solution.\n"
    )

    # Multimodal kullanım örneği, resmi direkt contents içine ekliyoruz. 
    uploaded = client.files.upload(file=tmp_path)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[grading_prompt, uploaded],
    )

    return response.text
