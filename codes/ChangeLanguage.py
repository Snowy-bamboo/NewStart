import win32api
import win32gui
from win32con import WM_INPUTLANGCHANGEREQUEST


def change_language(lang="EN")->bool: 
	"切换输入法，默认切换为英文输入法，参数可选'EN'或'ZH'"
	LANG = {
		"ZH": 0x0804,
		"EN": 0x0409
	}
	hwnd = win32gui.GetForegroundWindow()
	language = LANG[lang]
	result = win32api.SendMessage(
		hwnd,
		WM_INPUTLANGCHANGEREQUEST,
		0, # type: ignore  
		language # type: ignore
	)
	return not result
