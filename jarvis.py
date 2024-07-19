import pygame
import math
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import spacy
import subprocess
import threading

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Jarvis Assistant")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
BLUE = (0, 0, 255)

# Robot face properties
face_size = 300
eye_size = 50
mouth_width = 200
mouth_height = 20

# Initialize NLP
nlp = spacy.load("en_core_web_sm")

# API keys and configurations
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
SPOTIPY_CLIENT_ID = '926e78d263514d91ab86e86a0005573d'
SPOTIPY_CLIENT_SECRET = '52be511dbdbd4e3ca7370e311416b79f'
SPOTIPY_REDIRECT_URI = 'http://larvisassistant/callback/'

# Initialize speech recognition and text-to-speech
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()
voices = tts_engine.getProperty('voices')
tts_engine.setProperty('voice', voices[0].id)
tts_engine.setProperty('rate', 150)
tts_engine.setProperty('volume', 0.8)

# Spotify authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope="user-library-read,user-read-playback-state,user-modify-playback-state"))

speaking = False
mouth_open = 0

def speak(text):
    global speaking, mouth_open
    speaking = True
    tts_engine.say(text)
    tts_engine.runAndWait()
    speaking = False
    mouth_open = 0

def get_audio():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        said = ""

        try:
            said = recognizer.recognize_google(audio)
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
        subprocess.Popen(["WhatsApp"])
        return "Opening WhatsApp."
    except FileNotFoundError:
        return "Sorry, I couldn't find WhatsApp on your system."

def open_instagram():
    webbrowser.open("https://instagram.com")
    return "Opening Instagram."

def open_youtube():
    webbrowser.open("https://www.youtube.com")
    return "Opening YouTube."

def open_chatgpt():
    webbrowser.open("https://chat.openai.com/")
    return "Opening ChatGPT."

def open_leetcode():
    webbrowser.open("https://leetcode.com/")
    return "Opening LeetCode."

def play_music(song, artist):
    query = f"track:{song} artist:{artist}"
    results = sp.search(q=query, type='track', limit=1)
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        track_uri = track['uri']
        webbrowser.open(track['external_urls']['spotify'])
        speak(f"Playing {song} by {artist}")
    else:
        speak("Sorry, I couldn't find that song.")

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

    if "whatsapp" in text or "chat" in text:
        return open_whatsapp()
    
    if "instagram" in text:
        return open_instagram()
    
    if "youtube" in text:
        return open_youtube()
    
    if "chatgpt" in text or "AI" in text:
        return open_chatgpt()
    
    if "leetcode" in text or "DSA" in text or "coding" in text:
        return open_leetcode()
    
    if 'play' in text:
        try:
            text = text.replace('play', '').strip()
            song, artist = text.split('by')
            play_music(song.strip(), artist.strip())
        except ValueError:
            return "Please say the song name followed by the artist."

    return "Sorry, I don't understand that command."

def assistant_thread():
    speak("Hello, Osho. I'm Jarvis. How can I help you?")
    
    while True:
        text = get_audio()

        if "exit" in text or "bye" in text:
            speak("Goodbye!")
            pygame.quit()
            break

        response = process_command(text)
        if response:
            speak(response)
        else:
            speak("Sorry Osho. Can you try again?")

# Start the assistant in a separate thread
assistant = threading.Thread(target=assistant_thread)
assistant.start()

# Main Pygame loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill(WHITE)

    # Draw robot face
    pygame.draw.rect(screen, GRAY, (width//2 - face_size//2, height//2 - face_size//2, face_size, face_size))
    
    # Draw eyes
    pygame.draw.circle(screen, BLUE, (width//2 - face_size//4, height//2 - face_size//4), eye_size)
    pygame.draw.circle(screen, BLUE, (width//2 + face_size//4, height//2 - face_size//4), eye_size)
    
    # Draw mouth
    if speaking:
        mouth_open = math.sin(pygame.time.get_ticks() * 0.01) * 15 + 15
    pygame.draw.rect(screen, BLACK, (width//2 - mouth_width//2, height//2 + face_size//4, mouth_width, mouth_height + mouth_open))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
