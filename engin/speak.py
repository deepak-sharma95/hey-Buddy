import pyttsx3

engine = pyttsx3.init('sapi5')
engine.setProperty('rate', 170)

def speak(text):
    engine.say(text)
    engine.runAndWait()
