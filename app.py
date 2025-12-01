import streamlit as st
import streamlit.components.v1 as components

from dyn201_bot import dyn201_chat, check_solution

st.set_page_config(page_title="DYN201 Avatar Tutor", page_icon="🎓")

st.title("DYN201 Avatar Tutor (FREEWARE)")

if "extra_context" not in st.session_state:
    st.session_state.extra_context = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""


# ==== SIDEBAR ====
with st.sidebar:
    st.header("Ders Ayarları")

    st.markdown(
        "Bu uygulama DYN201 için sesli ve görsel bir asistan.\n\n"
        "- Soldaki avatar sesli anlatım yapar\n"
        "- Sağda çözüm fotoğrafı yükleyebilirsin\n"
        "- Altta chat ile soru sorabilirsin"
    )

    st.markdown("---")
    st.markdown(
        "**İpucu:** Çözümünü deftere yaz, fotoğrafını çek ve aşağıdaki bölümden yükle."
    )

    st.markdown("---")
    st.markdown("### Ek DYN201 Notların (isteğe bağlı)")
    st.session_state.extra_context = st.text_area(
        "Buraya CTMS'den veya kendi notlarından kısa özetler yapıştırabilirsin.",
        value=st.session_state.extra_context,
        height=160,
    )


# ==== ÜST SATIR: SOLDA AVATAR, SAĞDA ÇÖZÜM FOTOĞRAFI ====
col_avatar, col_solution = st.columns([1, 2])

with col_avatar:
    st.subheader("Konuşan Avatar")

    try:
        with open("avatar_widget.html", "r", encoding="utf-8") as f:
            template_html = f.read()
        safe_answer = st.session_state.last_answer.replace("`", "\\`")
        html_code = template_html.replace("{{ANSWER_PLACEHOLDER}}", safe_answer)
        components.html(html_code, height=420)
    except FileNotFoundError:
        st.warning("avatar_widget.html dosyası bulunamadı, GitHub'a eklediğinden emin ol.")

with col_solution:
    st.subheader("Çözüm Fotoğrafını Kontrol Ettir")

    uploaded_img = st.file_uploader(
        "Defterinden / kağıdından çözüm fotoğrafı yükle",
        type=["png", "jpg", "jpeg"],
        help="Örneğin bir DYN201 sorusunun çözümünü defterine yazıp fotoğrafını yükleyebilirsin.",
    )

    if uploaded_img and st.button("Bu çözümü kontrol et"):
        with st.spinner("Çözüm inceleniyor..."):
            feedback = check_solution(uploaded_img)

        st.chat_message("assistant").markdown("**Çözüm değerlendirmesi:**\n\n" + feedback)


st.markdown("---")

# ==== ALTTA CHAT BÖLÜMÜ ====
st.subheader("Soru–Cevap (Chat)")

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

user_input = st.chat_input("DYN201 ile ilgili soru sor veya çözüm adımını yaz...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Düşünüyorum..."):
            answer = dyn201_chat(
                history=st.session_state.messages,
                user_message=user_input,
                extra_context=st.session_state.extra_context,
            )
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.last_answer = answer
