def dyn201_chat(history, user_message, extra_context=None):
    """
    history: Streamlit'ten gelen mesaj listesi (role, content).
    user_message: Son yazılan mesaj.
    extra_context: Kullanıcının koyduğu ek ders notları (isteğe bağlı).
    """

    transcript_lines = []

    # --- 1) CTMS + DYN201 Knowledge File Yükle ---
    try:
        with open("dyn201_refs.txt", "r", encoding="utf-8") as f:
            dyn201_refs = f.read()
    except Exception:
        dyn201_refs = ""

    # --- 2) Kullanıcı ders notlarını ekle (varsa) ---
    if extra_context:
        transcript_lines.append(
            "Kullanıcı ders notları:\n" + extra_context + "\n---\n"
        )

    # --- 3) DYN201/CTMS resmi referans metnini ekle ---
    if dyn201_refs:
        transcript_lines.append(
            "=== DYN201 & CTMS RESMI REFERANS BASLANGICI ===\n"
            + dyn201_refs +
            "\n=== DYN201 & CTMS RESMI REFERANS BITISI ===\n"
        )

    # --- 4) Sohbet geçmişini modele aktar ---
    for msg in history:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            prefix = "Öğrenci"
        else:
            prefix = "Asistan"
        transcript_lines.append(f"{prefix}: {content}")

    # --- 5) Kullanıcının son mesajını ekle ---
    transcript_lines.append(f"Öğrenci: {user_message}")

    # --- 6) Final prompt ---
    full_prompt = (
        SYSTEM_PROMPT
        + "\n\n"
        + "\n".join(transcript_lines)
        + "\nAsistan:"
    )

    # --- 7) Model yanıtı ---
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=full_prompt
    )

    return response.text
