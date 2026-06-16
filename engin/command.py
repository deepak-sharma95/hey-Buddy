import pyttsx3
import speech_recognition as sr
import eel
import sqlite3
from g4f.client import Client

# Initialize Chat DB table if not exists
def init_chat_db():
    con = sqlite3.connect("heybuddy.db")
    cursor = con.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT,
        response TEXT
    )
    """)
    con.commit()
    con.close()

init_chat_db()

@eel.expose
def GetChatHistory():
    con = sqlite3.connect("heybuddy.db")
    cursor = con.cursor()
    cursor.execute("SELECT id, query, response FROM chat_history ORDER BY id DESC")
    rows = cursor.fetchall()
    con.close()
    return [{"id": row[0], "query": row[1], "response": row[2]} for row in rows]

@eel.expose
def DeleteChat(chat_id):
    con = sqlite3.connect("heybuddy.db")
    cursor = con.cursor()
    cursor.execute("DELETE FROM chat_history WHERE id=?", (chat_id,))
    con.commit()
    con.close()

@eel.expose
def ClearAllChats():
    con = sqlite3.connect("heybuddy.db")
    cursor = con.cursor()
    cursor.execute("DELETE FROM chat_history")
    con.commit()
    con.close()

def save_chat(query, response):
    con = sqlite3.connect("heybuddy.db")
    cursor = con.cursor()
    cursor.execute("INSERT INTO chat_history (query, response) VALUES (?, ?)", (query, response))
    con.commit()
    con.close()

# Initialize G4F Client (Completely Free, No API Key needed)
client = Client()

# Global Voice Settings
VOICE_RATE = 170
VOICE_VOLUME = 1.0
IS_MUTED = False
VOICE_ID = 0 # 0 for Male, 1 for Female
ASSISTANT_PERSONALITY = "Professional"
ANSWER_DETAIL = "Detailed"
RESPONSE_LANGUAGE = "English"

@eel.expose
def UpdateCoreSettings(personality, detail, is_muted, voice_id, language):
    global ASSISTANT_PERSONALITY, ANSWER_DETAIL, IS_MUTED, VOICE_ID, RESPONSE_LANGUAGE
    ASSISTANT_PERSONALITY = personality
    ANSWER_DETAIL = detail
    IS_MUTED = is_muted
    VOICE_ID = int(voice_id)
    RESPONSE_LANGUAGE = language
    if not IS_MUTED:
        speak("Settings saved")

@eel.expose
def ExportChatHistory():
    con = sqlite3.connect("heybuddy.db")
    cursor = con.cursor()
    cursor.execute("SELECT query, response FROM chat_history ORDER BY id ASC")
    rows = cursor.fetchall()
    con.close()
    
    export_text = "HeyBuddy Chat History\n======================\n\n"
    for row in rows:
        # replace <br> with newlines for text export
        resp = row[1].replace("<br>", "\n")
        export_text += f"You: {row[0]}\nBuddy: {resp}\n\n"
    return export_text

def speak(text):
    if IS_MUTED:
        eel.DisplayMessage(text)
        return
        
    # 🔊 Text to Speech: Ye function computer ko bulwane ke kaam aata hai.
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    try:
        engine.setProperty('voice', voices[VOICE_ID].id)
    except:
        pass
    
    engine.setProperty('rate', int(VOICE_RATE))
    engine.setProperty('volume', float(VOICE_VOLUME))

    # UI pe jo bhi bol raha hai use display karna
    eel.DisplayMessage(text)
    engine.say(text)
    engine.runAndWait()


# 🎤 Speech to Text: Ye function humari awaz sunkar text mein badalta hai.
def takecommand():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        eel.DisplayMessage("Listening...") # UI Update

        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)

    try:
        print("Recognizing...")
        eel.DisplayMessage("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}")
        eel.DisplayMessage(query)
    except Exception as e:
        print("Error: Kuch samajh nahi aaya.")
        # Removed eel.ShowHood() so we stay on siri page
        return ""
    
    # Removed eel.ShowHood() so we stay on siri page
    return query.lower()


# Ye function JS se call hota hai, ya to Type karke ya Mic dabake
@eel.expose
def allCommands(textQuery=None):
    # Agar frontend se typed text bheja hai to wo use hoga
    if textQuery:
        query = textQuery.lower()
        eel.DisplayMessage(query)
        eel.ShowHood() # Wave hata dega 
    else:
        # Nahi to mike suneega
        query = takecommand()

    print("Mila hua command:", query)
    if not query:
        return

    # Priority 1: System Applications (App Launching)
    if ("open" in query or "start" in query or "kholo" in query) and len(query.split()) <= 4 and "and" not in query:
        from engin.feature import openCommand
        openCommand(query)
        eel.ShowHood() # Return to home after opening app

    # Priority 2: Youtube
    elif ("youtube" in query or "play" in query) and len(query.split()) <= 6 and "and" not in query:
        from engin.feature import PlayYoutube
        PlayYoutube(query)
        eel.ShowHood() # Return to home after playing

    # Priority 3: Google / Search / Browser intents
    elif ("google" in query or "search" in query or "news" in query) and len(query.split()) <= 6 and "and" not in query:
        from engin.feature import SearchGoogle
        SearchGoogle(query)
        eel.ShowHood() # Return to home after search

    else:
        print("Sending to G4F API...")
        eel.ShowChatSection()
        eel.AddChatMessage("sender", query)
        eel.ShowTypingIndicator()
        
        try:
            # Many free G4F providers ignore the 'system' role. 
            # We inject the settings directly into the user's prompt to force compliance.
            system_instruction = f"[System Context: You are HeyBuddy, an AI voice assistant. Personality: {ASSISTANT_PERSONALITY}. Detail level: {ANSWER_DETAIL}. ALWAYS reply in {RESPONSE_LANGUAGE} language.]\n\n"
            combined_query = system_instruction + "User Query: " + query
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": combined_query}
                ]
            )
            ans = response.choices[0].message.content
                
            eel.RemoveTypingIndicator()
            
            # Format markdown response roughly to HTML just for newlines
            formatted_ans = ans.replace("\n", "<br>")
            
            save_chat(query, formatted_ans) # Save to DB
            eel.RefreshChatHistory()() # Tell frontend to refresh sidebar
            
            eel.AddChatMessage("receiver", formatted_ans)
            
            # Stop speaking the full long answer, just say a small confirmation
            speak("Here is the information you asked for.")
        except Exception as e:
            eel.RemoveTypingIndicator()
            error_details = str(e)
            eel.AddChatMessage("receiver", f"I'm sorry, an error occurred with G4F API. Details: {error_details}")
            print("G4F Error:", e)
