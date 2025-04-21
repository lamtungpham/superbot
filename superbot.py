# superbot.py - Phiên bản SIÊU CẤP + Cập nhật Hugging Face Token theo yêu cầu

import streamlit as st
import requests
import time

# --- Giao diện Streamlit ---
st.set_page_config(page_title="🎉 Trợ Lý AI của Tùng Tinh Tấn ✨", page_icon="🕵️")

st.title("🕵️ Trợ Lý AI của Tùng Tinh Tấn vô cùng đẹp trai 🚀")

st.info("🌟 Đây là Chatbot phục vụ riêng cho anh Tùng Tinh Tấn đẹp trai và học viên của anh trong quá trình nghiên cứu, thực hành! Mọi thắc mắc vui lòng liên hệ anh Tùng theo số điện thoại 0833821008 hoặc email tung.edtech@gmail.com nhé! 🚀", icon="🤖")

# --- Nhập Prompt Base ---
prompt_base = st.text_area("📋 Nhập Prompt Base cho chatbot:", placeholder="Ví dụ: Bạn là chuyên gia marketing...")

# --- Lựa chọn nhà cung cấp AI ---
provider = st.selectbox("Chọn nhà cung cấp AI:", ["OpenAI ChatGPT", "Google AI Studio", "Hugging Face Free"])

# --- Chọn model và nhập Key ---
api_key = None
model = None

if provider == "OpenAI ChatGPT":
    model = st.selectbox("Chọn mô hình GPT:", ["gpt-4o-mini", "gpt-4o", "gpt-4.1-nano"])
    api_key = st.text_input("Nhập OpenAI API Key:", type="password")
elif provider == "Google AI Studio":
    model = st.selectbox("Chọn mô hình Gemini:", ["gemini-1.5-pro", "gemini-2.0-flash-001", "gemini-2.0-flash-exp", "gemini-2.5-flash-preview-04-17", "gemini-2.5-pro-exp-03-25"])
    api_key = st.text_input("Nhập Google Gemini API Key:", type="password")
else:
    model = st.selectbox("Chọn mô hình Hugging Face:", [
        "google/flan-t5-small", "HuggingFaceH4/zephyr-7b-beta", "mistralai/Mistral-7B-Instruct-v0.1"
    ])
    api_key = st.text_input("Nhập Hugging Face Token:", type="password")

# --- Xóa lịch sử chat ---
if st.button("❌ Xóa lịch sử chat"):
    st.session_state.messages = []

# --- Khởi tạo session ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Hiển thị lịch sử chat cũ ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=msg.get("avatar", "")):
        st.markdown(msg["content"])

# --- Nhập tin nhắn ---
user_input = st.chat_input("Nhập tin nhắn...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input, "avatar": "👤"})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # --- Loading giả ---
    with st.chat_message("assistant", avatar="🧙" if provider != "Hugging Face Free" else "🤖"):
        loading_placeholder = st.empty()
        loading_placeholder.markdown("...")
        time.sleep(1)

        try:
            # Ghép Prompt Base + User Input
            final_prompt = f"{prompt_base}\nUser: {user_input}" if prompt_base else user_input

            if provider == "OpenAI ChatGPT":
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": model,
                    "messages": [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    "temperature": 0.7
                }
                res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                res.raise_for_status()
                bot_reply = res.json()["choices"][0]["message"]["content"]

            elif provider == "Google AI Studio":
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                headers = {"Content-Type": "application/json"}
                payload = {
                    "contents": [{"parts": [{"text": final_prompt}]}]
                }
                res = requests.post(url, headers=headers, json=payload)
                res.raise_for_status()
                bot_reply = res.json()["candidates"][0]["content"]["parts"][0]["text"]

            else:  # Hugging Face
                url = f"https://api-inference.huggingface.co/models/{model}"
                headers = {"Authorization": f"Bearer {api_key}"}
                payload = {"inputs": final_prompt}
                res = requests.post(url, headers=headers, json=payload)
                res.raise_for_status()
                bot_reply = res.json()[0]["generated_text"]

        except Exception as e:
            bot_reply = f"🧙🏼‍♀️ Lỗi: {e}"

        loading_placeholder.markdown(bot_reply)

    # --- Lưu chat bot reply ---
    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_reply,
        "avatar": "🧙" if provider != "Hugging Face Free" else "🤖"
    })
