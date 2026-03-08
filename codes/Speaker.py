import subprocess
import win32com.client

speaker = win32com.client.Dispatch("SAPI.SpVoice")
speaker.Volume = 100
speaker.Rate = 1.5


def Speak(text: str) -> None:
    "鏈楄缁欏畾鐨勫瓧绗︿覆"
    speaker.Speak(text, 3)


def Volume(level=100):
    "level: 0 鍒?100"
    intlevel = "%d" % (655.35 * level)
    try:
        subprocess.run(["nircmd.exe", "setsysvolume", str(intlevel)], check=False)
    except FileNotFoundError:
        # nircmd is optional; keep app running if it is not installed.
        pass
