import streamlit as st
import speech_recognition as sr
import os
import time
from gtts import gTTS
import tempfile
from groq import Groq
import subprocess

# Initialize API key
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# Transcript storage
transcript = []

# Streamlit UI
st.title("🎙️ AI Cold Calling Assistant")

# Function to check microphone availability and list devices
def is_microphone_available():
    try:
        mic_list = sr.Microphone.list_microphone_names()
        if not mic_list:
            return False, []
        return True, mic_list
    except Exception as e:
        st.error(f"Error detecting microphones: {e}")
        return False, []

mic_available, mic_names = is_microphone_available()

if mic_available:
    st.info("Available Microphones:")
    for i, name in enumerate(mic_names):
        st.write(f"{i}: {name}")
else:
    st.error("🚫 No microphone detected! Please connect a microphone and restart.")

# Optionally, let the user select a microphone by its index
device_index = None
if mic_available:
    default_index = 0  # default to first available microphone
    device_index = st.number_input("Select microphone index", min_value=0, max_value=len(mic_names)-1, value=default_index, step=1)

# Function to recognize speech
def recognize_speech(timeout=5, language="en"):
    recognizer = sr.Recognizer()
    try:
        # If device_index is set, use that microphone
        if device_index is not None:
            mic = sr.Microphone(device_index=int(device_index))
        else:
            mic = sr.Microphone()
        with mic as source:
            st.info("🎤 Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=timeout)
            text = recognizer.recognize_google(audio, language=language)
            st.write(f"👤 **User:** {text}")
            transcript.append(f"User: {text}")  # Save user input
            return text.lower()
    except sr.WaitTimeoutError:
        st.error("⏰ Listening timed out!")
        return None
    except sr.UnknownValueError:
        st.error("🤔 Could not understand audio!")
        return None
    except sr.RequestError:
        st.error("🔴 Speech recognition service error.")
        return None
    except Exception as e:
        st.error(f"🚫 Error: {e}")
        return None

# Function to generate AI response
def generate_ai_response(prompt):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=1,
        max_completion_tokens=512,
        top_p=1,
        stream=False,
    )
    return response.choices[0].message.content

# Function to convert text to speech and play it
def speak(text, language="en"):
    tts = gTTS(text=text, lang=language)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        # Use the appropriate command for your OS
        if os.name == "nt":
            os.system(f"start {fp.name}")
        else:
            os.system(f"afplay {fp.name}")
    transcript.append(f"AI: {text}")  # Save AI response

# Function to classify intent based on keywords in user input
def classify_intent(user_input):
    if "clone" in user_input:
        return "clone_repo"
    elif "search" in user_input:
        return "search_query"
    elif "transcribe" in user_input:
        return "transcribe"
    else:
        return "unknown"

# Function to execute repository cloning
def clone_repo():
    repo_url = "https://github.com/your-repo.git"  # Change to your actual repo URL
    st.info("🛠️ Cloning repository...")
    try:
        subprocess.run(["git", "clone", repo_url], check=True)
        st.success("✅ Repository cloned successfully!")
    except Exception as e:
        st.error(f"Error cloning repository: {e}")

# Function to save the transcript to a file
def save_transcript():
    try:
        with open("call_transcript.txt", "w", encoding="utf-8") as file:
            file.write("\n".join(transcript))
        st.success("📄 Call transcript saved!")
    except Exception as e:
        st.error(f"Error saving transcript: {e}")

# Main AI call flow triggered by button
if mic_available:
    if st.button("🎙️ Start AI Call"):
        intro = "Hello! How can I assist you today?"
        st.write(f"🤖 **AI:** {intro}")
        speak(intro)

        user_request = recognize_speech(timeout=10)
        if user_request:
            call_type = classify_intent(user_request)
            
            if call_type == "clone_repo":
                st.info("🛠️ Cloning a GitHub repository...")
                clone_repo()
            elif call_type == "search_query":
                ai_response = generate_ai_response(f"Search result for: {user_request}")
                st.write(f"🤖 **AI:** {ai_response}")
                speak(ai_response)
            elif call_type == "transcribe":
                save_transcript()
            else:
                ai_response = generate_ai_response(user_request)
                st.write(f"🤖 **AI:** {ai_response}")
                speak(ai_response)
else:
    st.warning("Please connect a microphone to start the AI call.")
