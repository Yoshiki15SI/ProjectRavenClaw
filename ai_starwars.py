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
    os.system(f'say -v {voice} "{text}"')

def processing_sound():
    sounds = ["Beep boop", "Bzzzt", "Whirr"]
    def play_sound():
        speak(random.choice(sounds), voice="Zarvox")
    thread = threading.Thread(target=play_sound)
    thread.start()

def has_internet():
    socket.gethostbyname("www.google.com")
    return True

def load_cache():
    with open(CACHE_FILE, "r") as f:
        return json.load(f)

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

def internet_lookup(query):
    cache = load_cache()
    if query in cache:
        return cache[query]
    summary = wikipedia.summary(query, sentences=1)
    cache[query] = summary
    save_cache(cache)
    return summary

print("Hold tight, firing up the language model...")
generator = pipeline('text-generation', model='distilgpt2')

recognizer = sr.Recognizer()
mic = sr.Microphone()

def get_user_input():
    with mic as source:
        print("Alright, what’s on your mind?")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        audio = recognizer.listen(source, phrase_time_limit=10)
    processing_sound()
    if has_internet():
        text = recognizer.recognize_google(audio)
    else:
        text = recognizer.recognize_sphinx(audio)
    print("Heard you say:", text)
    return text

def main():
    print("Automated Kerney 45 is alive! Hit me with a question.")
    speak("Hey, Kerney 45 is online and ready to roll!")
    while True:
        user_query = get_user_input()
        if user_query.lower() in ["exit", "stop"]:
            speak("Kerney 45 out—later!")
            break
        processing_sound()
        if "joke" in user_query.lower():
            print("Cooking up a joke...")
            prompt = "As a witty droid, tell me a brief, humorous tech joke in one sentence."
            generated = generator(prompt, max_length=50, temperature=0.7, top_p=0.9, num_return_sequences=1)
            response = generated[0]['generated_text'].replace(prompt, "").strip()
            if not response:
                response = "Why’d the droid crash? Too many bugs!"
        else:
            print("Digging up an answer...")
            prompt = (
                f"As a smart droid with all the info, give a short, real answer to: '{user_query}'. "
                f"No guessing!"
            )
            processing_sound()
            generated = generator(prompt, max_length=100, temperature=0.3, top_p=0.95, num_return_sequences=1)
            response = generated[0]['generated_text'].replace(prompt, "").strip()
            if has_internet():
                print("Checking the web...")
                processing_sound()
                lookup_result = internet_lookup(user_query)
                if lookup_result.lower() not in response.lower():
                    response = lookup_result
            response = response.split(".")[0] + "."
        print("Here’s the deal:", response)
        speak(response)
        time.sleep(1)

if __name__ == "__main__":
    main()
