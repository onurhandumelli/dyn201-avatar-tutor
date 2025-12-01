import json

import streamlit as st
import streamlit.components.v1 as components

from dyn201_bot import dyn201_chat, check_solution

# --------------------------------------------------
# SAYFA AYARLARI
# --------------------------------------------------
st.set_page_config(
    page_title="DYN201 Avatar Tutor (FREEWARE)",
    layout="wide",
)

# --------------------------------------------------
# SOHBET DURUMU
# --------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": (
                "Merhaba, ben DYN201 avatar eğitmeninim. "
                "Dersle ilgili sorularını sorabilir veya çözümünü anlatabilirsin."
            ),
        }
    ]

# --------------------------------------------------
# SAYFA DÜZENİ
# --------------------------------------------------
st.title("DYN201 Avatar Tutor (FREEWARE)")

left_col, right_col = st.columns([1, 2])

# ----------------- SOL SÜTUN (AVATAR + NOTLAR) -----------------
with left_col:
    # Avatar bileşeni (yüksekliği büyüttük ki ALTTKİ BUTONLAR KESİLMESİN)
    try:
        avatar_html = open("avatar_widget.html", "r", encoding="utf-8").read()
        # YÜKSEKLİĞİ ARTIRILAN TEK YER: height=600
        components.html(avatar_html, height=600, scrolling=False)
    except Exception:
        st.error("avatar_widget.html yüklenemedi.")

    # Ek not alanı
    st.markdown("### Ek DYN201 Notların (isteğe bağlı)")
    extra_notes = st.text_area(
        "Buraya CTMS'den veya kendi notlarından kısa özetler yapıştırabilirsin.",
        label_visibility="collapsed",
        height=200,
    )

# ----------------- SAĞ SÜTUN (CHAT + FOTOĞRAF) -----------------
with right_col:
    st.markdown("### Soru–Cevap (Chat)")

    # 1) Kullanıcıdan yeni mesajı al
    user_msg = st.chat_input(
        "DYN201 ile ilgili soru sor veya çözüm adımını yaz...",
        key="dyn201_chat_input",
    )

    # 2) Yeni mesaj geldiyse önce geçmişi güncelle
    if user_msg:
        # Kullanıcı mesajını geçmişe ekle
        st.session_state.chat_history.append(
            {"role": "user", "content": user_msg}
        )

        # Bottan cevap al
        bot_reply = dyn201_chat(
            history=st.session_state.chat_history,
            user_message=user_msg,
            extra_context=extra_notes,
        )

        # Cevabı geçmişe ekle
        st.session_state.chat_history.append(
            {"role": "assistant", "content": bot_reply}
        )

        # Avatarın cevabı sesli okuması için iframe'e mesaj gönder
        # (avatar_widget.html içinde window.addEventListener("message", type:"dyn201_tts") dinliyor)
        tts_text_json = json.dumps(bot_reply)
        st.markdown(
            f"""
            <script>
            const frame = window.document.querySelector("iframe[src*='avatar_widget.html']");
            if (frame && frame.contentWindow) {{
                frame.contentWindow.postMessage({{
                  type: "dyn201_tts",
                  text: {tts_text_json}
                }}, "*");
            }}
            </script>
            """,
            unsafe_allow_html=True,
        )

     # 3) Sohbet geçmişini YENİDEN ESKİYE doğru, ama her zaman
    #    "öğrenci mesajı + altında avatar cevabı" şeklinde göster.

    history = st.session_state.chat_history

    if not history:
        pass
    else:
        # İlk mesaj (karşılama) hep en tepede kalsın
        first = history[0]
        with st.chat_message("assistant"):
            st.markdown(first["content"])

        # Geri kalanları (1. elemandan itibaren) user/assistant çiftleri olarak grupla
        pairs = []
        i = 1
        while i < len(history):
            user_msg = history[i] if history[i]["role"] == "user" else None
            assistant_msg = (
                history[i + 1]
                if i + 1 < len(history) and history[i + 1]["role"] == "assistant"
                else None
            )
            pairs.append((user_msg, assistant_msg))
            i += 2  # her seferinde (user, assistant) çiftini atlıyoruz

        # En yeni çiftler en üstte görünsün diye ters çevir
        for user_msg, assistant_msg in reversed(pairs):
            if user_msg:
                with st.chat_message("user"):
                    st.markdown(user_msg["content"])
            if assistant_msg:
                with st.chat_message("assistant"):
                    st.markdown(assistant_msg["content"])


    # ----- FOTOĞRAF / ÇÖZÜM YÜKLEME -----
    st.markdown("### Soru / Çözüm Fotoğrafı Yükle")
    st.caption(
        "Dynamics ile ilgili bir *soru* veya *defterindeki çözümünün fotoğrafını* "
        "buraya yükleyebilirsin. Avatar çözümünü kontrol eder."
    )

    uploaded_file = st.file_uploader(
        "Dosyayı buraya bırak veya seç.",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=False,
    )

    if uploaded_file is not None:
        image_bytes = uploaded_file.read()
        feedback = check_solution(image_bytes)
        st.markdown("#### Avatarın değerlendirmesi:")
        st.write(feedback)

# --------------------------------------------------
# MİKROFON → CHAT GİRDİSİ (avatar'dan gelen sesli giriş)  — İSTERSEN KULLAN
# --------------------------------------------------
st.markdown(
    """
    <script>
    // Avatar iframe'inden gelen sesli giriş mesajını yakala
    window.addEventListener("message", (event) => {
      const data = event.data;
      if (data && data.type === "dyn201_voice_input") {
        const text = data.text || "";

        // Chat input'u (input veya textarea) placeholder'a göre bul
        const fields = window.document.querySelectorAll('input, textarea');
        for (const el of fields) {
          if (el.placeholder === 'DYN201 ile ilgili soru sor veya çözüm adımını yaz...') {
            el.value = text;
            const enterEvent = new KeyboardEvent('keydown', {
              key: 'Enter',
              keyCode: 13,
              which: 13,
              bubbles: true
            });
            el.dispatchEvent(enterEvent);
            break;
          }
        }
      }
    });
    </script>
    """,
    unsafe_allow_html=True,
)
