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

# Transcript Storage
transcript = []

# Streamlit UI
st.title("🎙️ AI Cold Calling Assistant")

# Function to check microphone availability
def is_microphone_available():
    try:
        if not sr.Microphone.list_microphone_names():
            return False
        return True
    except:
        return False

mic_available = is_microphone_available()

# Show an error message immediately if no microphone is detected
if not mic_available:
    st.error("🚫 No microphone detected! Please connect a microphone and restart.")

# Function to recognize speech
def recognize_speech(timeout=5, language="en"):
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.info("🎤 Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=timeout)
            text = recognizer.recognize_google(audio, language=language)
            st.write(f"👤 **User:** {text}")
            transcript.append(f"User: {text}")  # Save user input
            return text.lower()
    except sr.WaitTimeoutError:
        return None
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        st.error("🔴 Speech recognition service error.")
        return None
    except:
        st.error("🚫 No microphone detected! Please connect a microphone and restart.")
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
        os.system(f"start {fp.name}" if os.name == "nt" else f"afplay {fp.name}")
    transcript.append(f"AI: {text}")  # Save AI response

# Function to classify intent
def classify_intent(user_input):
    if "clone" in user_input:
        return "clone_repo"
    elif "search" in user_input:
        return "search_query"
    elif "transcribe" in user_input:
        return "transcribe"
    else:
        return "unknown"

# Function to execute cloning
def clone_repo():
    repo_url = "https://github.com/your-repo.git"  # Change to actual repo
    st.info("🛠️ Cloning repository...")
    subprocess.run(["git", "clone", repo_url], check=True)
    st.success("✅ Repository cloned successfully!")

# Function to save transcript
def save_transcript():
    with open("call_transcript.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(transcript))
    st.success("📄 Call transcript saved!")

# AI Call with Voice Commands
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
