import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import requests
import spacy
import subprocess


# Load the English NLP model
nlp = spacy.load("en_core_web_sm")

# Get the OpenWeatherMap API key from an environment variable
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

# Initialize the text-to-speech engine once
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 150)
engine.setProperty('volume', 0.8)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
            print(f"You said: {said}")
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
        except sr.RequestError:
            print("Sorry, my speech service is down.")
        except Exception as e:
            print(f"Exception: {str(e)}")

    return said.lower()

def get_weather(city):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        temp = data['main']['temp']
        description = data['weather'][0]['description']
        return f"The weather in {city} is {description} with a temperature of {temp}°C."
    except requests.RequestException as e:
        return f"Sorry, I couldn't fetch the weather information: {str(e)}"

def open_vscode():
    try:
        subprocess.Popen(["code"])
        return "Opening Visual Studio Code."
    except FileNotFoundError:
        return "Sorry, I couldn't find Visual Studio Code on your system."

def shutdown_pc():
    speak("Are you sure you want to shut down your PC? Say 'yes' to confirm or 'no' to cancel.")
    confirmation = get_audio()
    if 'yes' in confirmation:
        speak("Shutting down your PC. Goodbye!")
        os.system("shutdown /s /t 1")
        return "Shutting down your PC."
    else:
        return "Shutdown cancelled."

def open_spotify():
    try:
        subprocess.Popen(["spotify"])
        return "Opening Spotify."
    except FileNotFoundError:
        return "Sorry, I couldn't find Spotify on your system."

def open_gmail():
    webbrowser.open("https://mail.google.com")
    return "Opening Gmail."

def open_whatsapp():
    try:
        subprocess.Popen(["whatsapp"])
        return "Opening WhatsApp."
    except FileNotFoundError:
        return "Sorry, I couldn't find WhatsApp on your system."
    
def open_instagram():
    webbrowser.open("https://instagram.com")
    return "Opening Instagram."

def open_chatgpt():
    webbrowser.open("https://chat.openai.com/")
    return "Opening ChatGPT."

def open_leetcode():
    webbrowser.open("https://leetcode.com/")
    return "Opening LeetCode."

def process_command(text):
    doc = nlp(text)
    
    if any(token.text in ["weather", "temperature", "forecast"] for token in doc):
        for ent in doc.ents:
            if ent.label_ == "GPE":
                return get_weather(ent.text)
        return "Please specify a city for the weather information."

    if any(token.text in ["time", "clock"] for token in doc):
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}"

    if any(token.text in ["browser", "internet", "web"] for token in doc):
        webbrowser.open("https://www.google.com")
        return "Opening your default web browser"

    if "notepad" in text:
        os.system("notepad.exe")
        return "Opening Notepad"

    if "files" in text:
        os.system("explorer")
        return "Opening File Explorer"

    if "visual studio code" in text or "vs code" in text:
        return open_vscode()

    if "shutdown" in text or "turn off" in text:
        return shutdown_pc()

    if "spotify" in text:
        return open_spotify()

    if "gmail" in text:
        return open_gmail()

    if "whatsapp" in text:
        return open_whatsapp()
    
    if "instagram" in text:
        return open_instagram()
    
    if "chatgpt" in text:
        return open_chatgpt()
    
    if "leetcode" in text:
        return open_leetcode()
    

    return "Sorry, I don't understand that command."

def main():
    speak("Hello, Osho. I'm jarvis. How can I help you?")
    
    while True:
        text = get_audio()

        if "exit" in text or "bye" in text:
            speak("Goodbye!")
            break

        response = process_command(text)
        if response:
            speak(response)
        else:
            speak("Sorry Osho. Can you try again?")

if __name__ == "__main__":
    main()
