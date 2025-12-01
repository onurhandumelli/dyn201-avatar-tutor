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

# CSS: sticky avatar + kaydırılabilir chat kutusu
st.markdown(
    """
    <style>
    .sticky-avatar {
        position: sticky;
        top: 120px;
    }

    /* Chat kutusu: sabit yükseklik + içten scroll */
    .dyn201-chat-box {
        max-height: 380px;
        overflow-y: auto;
        padding-right: 8px;
        margin-bottom: 1.2rem;
        border-radius: 12px;
    }

    /* Streamlit'in chat mesaj kartlarının arası çok açılmasın */
    .dyn201-chat-box [data-testid="stChatMessage"] {
        margin-bottom: 0.4rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sohbet geçmişini tutmak için session_state
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
    # Avatar bileşeni (solda sabit dursun)
    st.markdown('<div class="sticky-avatar">', unsafe_allow_html=True)
    try:
        avatar_html = open("avatar_widget.html", "r", encoding="utf-8").read()
        components.html(avatar_html, height=420)
    except Exception:
        st.error("avatar_widget.html yüklenemedi.")
    st.markdown("</div>", unsafe_allow_html=True)

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

    # --- KAYDIRILABİLİR CHAT KUTUSU ---
    st.markdown('<div class="dyn201-chat-box">', unsafe_allow_html=True)

    # Geçmiş mesajları göster
    for msg in st.session_state.chat_history:
        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
            st.markdown(msg["content"])

    st.markdown("</div>", unsafe_allow_html=True)

    # Kullanıcıdan yeni mesaj
    user_msg = st.chat_input(
        "DYN201 ile ilgili soru sor veya çözüm adımını yaz...",
        key="dyn201_chat_input",
    )

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

        st.session_state.chat_history.append(
            {"role": "assistant", "content": bot_reply}
        )

        # Yeni cevabı hemen ekranda göster (scroll kutusuna yeni render'da eklenecek)
        with st.chat_message("assistant"):
            st.markdown(bot_reply)

        # --- Avatarın cevabı yüksek sesle okuması için iframe'e mesaj gönder ---
        tts_text_json = json.dumps(bot_reply)
        st.markdown(
            f"""
            <script>
            // avatar_widget iframe'ini bul ve içine mesaj gönder
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

    # ----- FOTOĞRAF / ÇÖZÜM YÜKLEME (CHAT KUTUSUNUN ALTINDA SABİT) -----
    st.markdown("### Soru / Çözüm Fotoğrafı Yükle")
    st.caption(
        "Dynamics ile ilgili bir **soru** veya **defterindeki çözümünün fotoğrafını** "
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
# MİKROFON → CHAT GİRDİSİ (avatar'dan gelen sesli giriş)
# --------------------------------------------------
st.markdown(
    """
    <script>
    // Avatar iframe'inden gelen sesli giriş mesajını yakala
    window.addEventListener("message", (event) => {
      const data = event.data;
      if (data && data.type === "dyn201_voice_input") {
        const text = data.text || "";

        // Streamlit chat_input alanını bul (textarea + placeholder)
        const areas = window.document.querySelectorAll('textarea');
        for (const ta of areas) {
          if (ta.placeholder === 'DYN201 ile ilgili soru sor veya çözüm adımını yaz...') {
            ta.value = text;
            const enterEvent = new KeyboardEvent('keydown', {
              key: 'Enter',
              keyCode: 13,
              which: 13,
              bubbles: true
            });
            ta.dispatchEvent(enterEvent);
            break;
          }
        }
      }
    });
    </script>
    """,
    unsafe_allow_html=True,
)
