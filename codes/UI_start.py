import tkinter as tk
from PIL import Image, ImageTk
from main_alpha import mainalpha
from main_beta import mainbeta
from ConfigReader import Config
from ChangeLanguage import change_language


def Alpha():
	win.quit()
	win.destroy()
	mainalpha()
	

def Beta():
	win.quit()
	win.destroy()
	mainbeta()

print(
"""
===================================================
出车系统暂时保留此命令行窗口
用于调试及查看可能的报错信息
===================================================
"""
)

win = tk.Tk()
win.geometry("420x250+500+200")
win.iconphoto(False,tk.PhotoImage(file="./Resource/icon.png"))
win.title(f"器材管理系统v{Config.Version}")
Frametitle = tk.Frame(win)
Frametitle.pack(ipady=5)
tk.Label(Frametitle,text=f'器材管理系统v{Config.Version}',font=('华文魏碑',25,'bold'),justify='center',fg='blue4').pack(side=tk.RIGHT)
logo = ImageTk.PhotoImage(Image.open("./Resource/YAS.png").resize((45,45)))
Logo = tk.Label(Frametitle, image=logo,width=40,height=40)
Logo.pack(side=tk.LEFT)
tk.Label(win,text='Version 3.0 is Brilliant!',font=('华文魏碑',15,'bold'),justify='center',fg='green').pack()
tk.Button(win,text='出车系统',font=('华文魏碑',20),justify='center',command = Alpha,cursor="hand2").pack(pady=10)
tk.Button(win,text='收车系统',font=('华文魏碑',20),justify='center',command =Beta,cursor="hand2").pack()
Sign = tk.Label(win,text='by The Wolf-Rayet',font=('timesnewrom',12,'bold'),justify='center',fg='blue4')
Sign.place(relx=1,rely=1,anchor="se")
change_language("EN")
win.mainloop()