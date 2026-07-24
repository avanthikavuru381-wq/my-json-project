import speech_recognition as sr

r = sr.Recognizer()

with sr.Microphone() as source:
    print("Speak now...")
    audio = r.listen(source, timeout=5)

print("Recorded successfully")