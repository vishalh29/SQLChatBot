import streamlit as st
from sarvamai import SarvamAI
from sarvamai.play import play, save
import tempfile
import os

# Initialize client
client = SarvamAI(
    api_subscription_key="1ef57146-5fb4-4ad5-9f11-12c78f44aaca",
)

st.set_page_config(page_title="AI Chat Assistant", layout="centered")

st.title("🤖 AI Chat Assistant")

# Session state to store conversation history
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "You are a helpful assistant. Answer in detail."}
    ]

# Display chat history
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])

# Chat input box
if prompt := st.chat_input("Type your message..."):
    # Add user message
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # 🔑 Pass the FULL conversation history
    response = client.chat.completions(
        messages=st.session_state["messages"],
        temperature=0.5,
        top_p=1,
        max_tokens=20000,
    )

    ai_reply = response.choices[0].message.content

    # Add AI reply to history
    st.session_state["messages"].append({"role": "assistant", "content": ai_reply})
    st.chat_message("assistant").write(ai_reply)

# Text-to-Speech functionality
def get_last_assistant_response():
    """Get the last assistant response from chat history"""
    for msg in reversed(st.session_state["messages"]):
        if msg["role"] == "assistant":
            return msg["content"]
    return None

def text_to_speech(text):
    """Convert text to speech using SarvamAI TTS API"""
    try:
        # SarvamAI TTS API has a limit of 2500 characters
        MAX_CHARS = 2400  # Using 2400 to be safe
        
        if len(text) > MAX_CHARS:
            # Truncate text and add warning
            original_length = len(text)
            text = text[:MAX_CHARS].rsplit(' ', 1)[0] + "..."  # Truncate at word boundary
            st.warning(f"⚠️ Text was truncated from {original_length} to {len(text)} characters due to API limits.")
        
        response = client.text_to_speech.convert(
            text=text,
            target_language_code="en-IN",
            enable_preprocessing=True
        )
        return response
    except Exception as e:
        st.error(f"Error converting text to speech: {str(e)}")
        return None

# TTS Button and functionality
st.divider()

# Show text length info
last_response = get_last_assistant_response()
if last_response:
    text_length = len(last_response)
    if text_length > 2400:
        st.warning(f"⚠️ Last response: {text_length} characters (exceeds 2400 char limit)")
        st.info("💡 The text will be automatically truncated for TTS. Consider asking for a shorter response for better audio experience.")
    else:
        st.info(f"✅ Last response: {text_length} characters (perfect for TTS)")

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🔊 Read Last Response", type="primary"):
        if last_response:
            with st.spinner("Converting to speech..."):
                audio_response = text_to_speech(last_response)
                
            if audio_response:
                # Create a temporary file to save the audio
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                    save(audio_response, tmp_file.name)
                    
                    # Read the audio file and display it in Streamlit
                    with open(tmp_file.name, "rb") as audio_file:
                        audio_bytes = audio_file.read()
                        st.audio(audio_bytes, format="audio/wav")
                    
                    # Clean up temporary file
                    os.unlink(tmp_file.name)
                    
                    st.success("✅ Audio generated successfully!")
        else:
            st.warning("No assistant response found to convert to speech.")

with col2:
    if st.button("💾 Save Last Response Audio"):
        if last_response:
            with st.spinner("Converting to speech..."):
                audio_response = text_to_speech(last_response)
                
            if audio_response:
                # Save to downloads or current directory
                output_filename = "tts_output.wav"
                save(audio_response, output_filename)
                st.success(f"✅ Audio saved as '{output_filename}'")
                
                # Also provide download button
                with open(output_filename, "rb") as file:
                    st.download_button(
                        label="📥 Download Audio File",
                        data=file.read(),
                        file_name=output_filename,
                        mime="audio/wav"
                    )
        else:
            st.warning("No assistant response found to convert to speech.")

st.divider()

# Optional: Clear chat button
if st.button("🗑️ Clear Chat"):
    st.session_state["messages"] = [
        {"role": "system", "content": "You are a helpful assistant. Answer in detail."}
    ]
    st.experimental_rerun()
