import subprocess
import win32com.client

speaker = win32com.client.Dispatch("SAPI.SpVoice")
speaker.Volume = 100
speaker.Rate = 1.5


def Speak(text: str) -> None:
    "朗读给定的字符串"
    speaker.Speak(text, 3)


def Volume(level=100):
    "level: 0 到 100"
    intlevel = "%d" % (655.35 * level)

