# import matplotlib
import speech_recognition as sr
import playsound
import simpleaudio as sa

r = sr.Recognizer()

bell = sr.AudioFile('bell.wav')

with bell as source:
    audio = r.record(source)
wave_obj = sa.WaveObject.from_wave_file("bell.wav")
play_obj = wave_obj.play()
play_obj.wait_done()

#print(r.recognize_google(audio))