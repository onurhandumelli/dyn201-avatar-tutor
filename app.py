import streamlit as st

from dyn201_bot import dyn201_chat, check_solution

# Sayfa başlığı
st.set_page_config(page_title="DYN201 Avatar Tutor", page_icon="🎓")

st.title("DYN201 Avatar Tutor")

# Ek ders notları için başlangıç değeri
extra_context = ""

# Sohbet geçmişi
if "messages" not in st.session_state:
    st.session_state.messages = []  # her eleman: {"role": "user"/"assistant", "content": "metin"}


# SIDEBAR: Ders ayarları
with st.sidebar:
    st.header("Ders Ayarları")

    st.markdown(
        "Buraya hocanın PDF'lerinden, notlarından, ödev açıklamalarından kısa parçalar "
        "yapıştırabilirsin. Asistan cevap verirken bunları da dikkate alır."
    )
    extra_context = st.text_area("DYN201 notların (isteğe bağlı)", height=200)

    show_avatar = st.checkbox("Avatar GIF göster", value=True)

    st.markdown("---")
    st.markdown("**İpucu:** Çözümünü önce defterine yaz, fotoğrafını çek, aşağıdaki alandan yükle.")


# İki kolon: solda avatar, sağda çözüm kontrolü
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Avatar")

    if show_avatar:
        # Repo'ya ekleyeceğin avatar.gif dosyası burada gösterilecek
        st.image("avatar.gif", caption="DYN201 Asistanın", use_column_width=True)
    else:
        st.write("Avatar kapalı.")


with col2:
    st.subheader("Çözüm Fotoğrafını Kontrol Ettir")

    uploaded_img = st.file_uploader(
        "Defterinden / kağıdından çözüm fotoğrafı yükle",
        type=["png", "jpg", "jpeg"],
        help="Örneğin DYN201 midterm sorusunun çözümünü defterine yazıp fotoğrafını yükleyebilirsin.",
    )

    if uploaded_img and st.button("Bu çözümü kontrol et"):
        with st.spinner("Çözüm inceleniyor..."):
            feedback = check_solution(uploaded_img)

        st.chat_message("assistant").markdown("**Çözüm değerlendirmesi:**\n\n" + feedback)


# Sohbet geçmişini ekrana bas
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])


# Kullanıcıdan yeni mesaj al
user_input = st.chat_input("Soru sor veya çözüm adımını yaz...")

if user_input:
    # Kullanıcı mesajını geçmişe ekle ve göster
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)

    # Asistan cevabı
    with st.chat_message("assistant"):
        with st.spinner("Düşünüyorum..."):
            answer = dyn201_chat(
                history=st.session_state.messages,
                user_message=user_input,
                extra_context=extra_context,
            )
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
