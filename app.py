import streamlit as st
import streamlit.components.v1 as components

from dyn201_bot import dyn201_chat, check_solution

st.set_page_config(page_title="DYN201 Avatar Tutor", page_icon="🎓")

st.title("DYN201 Avatar Tutor (FREEWARE)")

# Ek ders notları için başlangıç
if "extra_context" not in st.session_state:
    st.session_state.extra_context = ""

if "messages" not in st.session_state:
    st.session_state.messages = []  # {"role": "user"/"assistant", "content": "metin"}

if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""


# SIDEBAR
with st.sidebar:
    st.header("Ders Ayarları")

    st.markdown(
        "Buraya hocanın gönderdiği web sayfalarından veya kendi notlarından kısa "
        "özetler yapıştırabilirsin. Asistan cevap verirken bunları dikkate alır."
    )
    st.session_state.extra_context = st.text_area(
        "DYN201 notların (isteğe bağlı)",
        value=st.session_state.extra_context,
        height=200,
    )

    st.markdown("---")
    st.markdown(
        "**İpucu:** Çözümünü önce defterine yaz, fotoğrafını çek ve aşağıdaki bölümden yükle."
    )


# ÜSTTE İKİ KOLON: solda avatar, sağda çözüm kontrolü
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Konuşan Avatar")

    # avatar_widget.html dosyasını okuyup, en son cevabı içine yerleştireceğiz
    try:
        with open("avatar_widget.html", "r", encoding="utf-8") as f:
            template_html = f.read()
        # backtick karakteri JS'de sorun olmasın diye kaçırıyoruz
        safe_answer = st.session_state.last_answer.replace("`", "\\`")
        html_code = template_html.replace("{{ANSWER_PLACEHOLDER}}", safe_answer)
        components.html(html_code, height=430)
    except FileNotFoundError:
        st.warning(
            "avatar_widget.html henüz eklenmemiş. Bir sonraki adımda bu dosyayı oluşturacağız."
        )


with col2:
    st.subheader("Çözüm Fotoğrafını Kontrol Ettir")

    uploaded_img = st.file_uploader(
        "Defterinden / kağıdından çözüm fotoğrafı yükle",
        type=["png", "jpg", "jpeg"],
        help="Örneğin bir DYN201 sorusunun çözümünü defterine yazıp fotoğrafını yükle.",
    )

    if uploaded_img and st.button("Bu çözümü kontrol et"):
        with st.spinner("Çözüm inceleniyor..."):
            feedback = check_solution(uploaded_img)

        st.chat_message("assistant").markdown("**Çözüm değerlendirmesi:**\n\n" + feedback)


st.markdown("---")
st.subheader("Soru–Cevap (Chat)")

# Önce geçmişi göster
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

# Kullanıcıdan yeni mesaj al
user_input = st.chat_input("DYN201 ile ilgili soru sor veya çözüm adımını yaz...")

if user_input:
    # Kullanıcı mesajını ekle
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)

    # Asistan cevabı
    with st.chat_message("assistant"):
        with st.spinner("Düşünüyorum..."):
            answer = dyn201_chat(
                history=st.session_state.messages,
                user_message=user_input,
                extra_context=st.session_state.extra_context,
            )
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.last_answer = answer  # Avatarın okuyacağı metin
