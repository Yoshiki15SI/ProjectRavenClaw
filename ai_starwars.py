import os
import socket
import speech_recognition as sr
from transformers import pipeline
import wikipedia
import json
import time
import threading
import random

CACHE_FILE = "wiki_cache.json"

def speak(text, voice="Daniel"):
    try:
        os.system(f'say -v {voice} "{text}"')
    except:
        print(text)

def processing_sound():
    sounds = ["Beep boop", "Bzzzt", "Whirr"]
    def run_sound():
        speak(random.choice(sounds), voice="Zarvox")
    thread = threading.Thread(target=run_sound)
    thread.start()

def has_internet():
    try:
        socket.gethostbyname("www.google.com")
        return True
    except:
        return False

def load_cache():
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

def internet_lookup(query):
    cache = load_cache()
    if query in cache:
        return cache[query]
    try:
        summary = wikipedia.summary(query, sentences=1)
        cache[query] = summary
        save_cache(cache)
        return summary
    except:
        return None

print("Loading language model...")
generator = pipeline('text-generation', model='distilgpt2')

recognizer = sr.Recognizer()
mic = sr.Microphone()

def get_user_input():
    with mic as source:
        print("Speak your question:")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        audio = recognizer.listen(source, phrase_time_limit=10)
    try:
        processing_sound()
        if has_internet():
            text = recognizer.recognize_google(audio)
        else:
            text = recognizer.recognize_sphinx(audio)
        print("You said:", text)
        if len(text.split()) < 2:
            speak("Please provide more details for a better answer.")
            return ""
        return text
    except:
        print("Could not understand audio.")
        return ""

def main():
    print("Automated Kerney 45 is online. Please ask your question.")
    speak("Automated Kerney 45 online. Ready for your queries.")
    while True:
        user_query = get_user_input()
        if not user_query:
            speak("I didn’t catch that. Please try again.")
            continue
        if user_query.lower() in ["exit", "stop"]:
            speak("Automated Kerney 45 shutting down. Farewell.")
            break
        processing_sound()
        if "joke" in user_query.lower():
            print("Generating joke...")
            prompt = "As a witty droid, tell me a brief, humorous tech joke in one sentence."
            generated = generator(prompt, max_length=50, temperature=0.7, top_p=0.9, num_return_sequences=1)
            response = generated[0]['generated_text'].replace(prompt, "").strip()
            if not response:
                response = "Why did the droid malfunction? It had too many bugs!"
        else:
            print("Generating answer...")
            prompt = (
                f"As an advanced knowledge droid with vast data access, provide a "
                f"concise, factual answer to: '{user_query}'. "
                f"Avoid speculation and ensure accuracy."
            )
            processing_sound()
            generated = generator(prompt, max_length=100, temperature=0.3, top_p=0.95, num_return_sequences=1)
            response = generated[0]['generated_text'].replace(prompt, "").strip()
            if not response or len(response.split()) < 3:
                response = "Insufficient data to respond."
            extra_info = ""
            if has_internet():
                print("Checking online data...")
                processing_sound()
                lookup_result = internet_lookup(user_query)
                if lookup_result:
                    if lookup_result.lower() not in response.lower():
                        response = lookup_result
                    extra_info = f" Online data: {lookup_result}"
            full_response = (response + extra_info).split(".")[0] + "."
            response = full_response
        print("Response:", response)
        speak(response)
        time.sleep(1)

if __name__ == "__main__":
    main()
