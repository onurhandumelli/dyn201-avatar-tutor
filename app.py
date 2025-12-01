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

# Sticky avatar için basit CSS
st.markdown(
    """
    <style>
    .sticky-avatar {
        position: sticky;
        top: 80px;
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
            "content": "Merhaba, ben DYN201 avatar eğitmeninim. "
                       "Dersle ilgili sorularını sorabilir veya çözümünü anlatabilirsin."
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

    # Geçmiş mesajları göster
    for msg in st.session_state.chat_history:
        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
            st.markdown(msg["content"])

    # Kullanıcıdan yeni mesaj
    user_msg = st.chat_input(
        "DYN201 ile ilgili soru sor veya çözüm adımını yaz..."
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

        # Yeni cevabı hemen ekranda göster
        with st.chat_message("assistant"):
            st.markdown(bot_reply)

    # ----- FOTOĞRAF YÜKLEME -----
    st.markdown("### Soru / Çözüm Fotoğrafı Yükle")
    st.caption(
        "Dynamics ile ilgili bir **soru** veya **defterindeki çözümün fotoğrafını** buraya yükleyebilirsin."
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
# MİKROFON → CHAT GİRDİSİ (Web Speech API entegrasyonu)
# --------------------------------------------------
st.markdown(
    """
    <script>
    // Avatar iframe'inden gelen sesli giriş mesajını yakala
    window.addEventListener("message", (event) => {
      const data = event.data;
      if (data && data.type === "dyn201_voice_input") {
        const text = data.text;

        // Streamlit chat_input alanını bul (placeholder'a göre)
        const inputs = window.parent.document.querySelectorAll('input');
        for (const inp of inputs) {
          if (inp.getAttribute('placeholder') === 'DYN201 ile ilgili soru sor veya çözüm adımını yaz...') {
            inp.value = text;
            const enterEvent = new KeyboardEvent('keydown', {
              key: 'Enter',
              keyCode: 13,
              which: 13,
              bubbles: true
            });
            inp.dispatchEvent(enterEvent);
            break;
          }
        }
      }
    });
    </script>
    """,
    unsafe_allow_html=True,
)
