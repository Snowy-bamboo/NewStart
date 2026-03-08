import win32api
import win32gui
from win32con import WM_INPUTLANGCHANGEREQUEST


def change_language(lang="EN")->bool: 
	LANG = {
		"ZH": 0x0804,
		"EN": 0x0409
	}
	hwnd = win32gui.GetForegroundWindow()
	language = LANG[lang]
	result = win32api.SendMessage(
		hwnd,
		WM_INPUTLANGCHANGEREQUEST,
		0,
		language
	)
	if not result:
		return True