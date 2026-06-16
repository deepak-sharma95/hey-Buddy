import os
import time
import re
import sqlite3
import pywhatkit as kit
from playsound import playsound
from engin.configration import ASSISTANT_NAME
from engin.speak import speak
try:
    from AppOpener import open as appopen
except ImportError:
    appopen = None


def playAssistantsound():
    # Ye sound effects chalata hai starting mein. Local website folder se read ho rahe hain
    sounds = [
        "www/assets/audio/sound.mp3",
        "www/assets/audio/music.mp3"
    ]
    try:
        for sound in sounds:
            playsound(sound)
            time.sleep(0.2)
    except Exception as e:
        pass # Ignore error silently


def openCommand(query):
    # 'query' string mein se faaltu words hatakr actual software ka naam dhoondhna
    query = query.lower()
    query = query.replace(ASSISTANT_NAME.lower(), "")
    
    # Faltu trigger words hata dein
    for word in ["open", "start", "kholo", "karo", "please", "bhai", "can you"]:
        query = query.replace(word, "")
        
    query = query.strip() # Aage peeche ke spaces hata deta hai

    if not query:
        speak("Konsa application open karna hai ye samajh nahi aaya")
        return

    # 1. Web URLs
    app_mappings = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com"
    }

    if query in app_mappings:
        speak(f"Opening {query}")
        os.system(f"start {app_mappings[query]}")
        return

    speak(f"Opening {query}")

    # 2. AppOpener Magic (Ye system ke sabhi apps jaise Spotify, Edge, Store sabko khol dega)
    if appopen is not None:
        try:
            # Ye closely matching app dhoondh lega aur open kar dega
            appopen(query, match_closest=True)
            return
        except Exception as e:
            pass

    # 3. Basic System Commands (Agar AppOpener install na ho ya fail ho jaye)
    basic_apps = {
        "cmd": "cmd",
        "c m d": "cmd",
        "command prompt": "cmd",
        "powershell": "powershell",
        "power shell": "powershell",
        "whatsapp": "whatsapp:",
        "camera": "microsoft.windows.camera:",
        "calculator": "calc",
        "notepad": "notepad",
        "settings": "ms-settings:"
    }
    
    if query in basic_apps:
        os.system(f"start {basic_apps[query]}")
        return

    # 4. Database Lookup
    try:
        con = sqlite3.connect("heybuddy.db")
        cursor = con.cursor()
        cursor.execute("SELECT path FROM sys_command WHERE name = ?", (query,))
        result = cursor.fetchall()
        con.close()
        
        if len(result) > 0:
            path = result[0][0]
            os.system(f'start "" "{path}"')
            return
    except Exception as e:
        print("DB Error:", e)

    # 5. Direct Start Fallback
    os.system(f"start {query}")


def PlayYoutube(query):
    # simple clean up for query
    search_term = query.replace("play", "").replace("on youtube", "").replace("youtube", "").strip()
    if not search_term:
        search_term = query

    speak("Playing " + search_term + " on YouTube")
    # kit (pywhatkit) web page open karke youtube song khud play kar dega browser me
    kit.playonyt(search_term)


def SearchGoogle(query):
    # 'search' or 'google me dhundo' keyword hata dete hain
    search_term = query.replace("search", "").replace("on google", "").replace("google", "").strip()
    if not search_term:
        search_term = query
        
    speak("Searching for " + search_term)
    # kit browser me direct query search kar deta hai
    kit.search(search_term)
