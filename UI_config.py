import tkinter as tk
from ToolTip import FakeBalloon
from tkinter import messagebox
from PIL import Image, ImageTk

from ChangeLanguage import change_language

from ConfigReader import CONFIG
from typing import Union

"""
当前版本默认config
{
    "Version":"3.0",
	"Data Save Rule":"3.0",
    "Display Disable Equipment":0,
    "TJ Maxmess Rate":1.0,
    "Enable Old Logs":0,
	"ImportDataDisplaySoltDetail_Alpha":0,
	"ImportDataDisplaySoltDetail_Beta":0,
	"AutoCheckStepTwo":0,
	"ConfigNeedPassword":1,
	"Beta Password": "cmd-299792458",
	"Config Password": "ZHUKPW"
}
"""

def Quit(root:tk.Misc,ask=True):
	"询问是否退出后退出"
	if (not ask) or messagebox.askokcancel(title='警告',message='确认放弃更改?'):
		root.quit()
		root.destroy()
	else:
		root.focus_force()


def _quit(root:tk.Misc,Var:tk.BooleanVar,newvar:bool):
	"关闭窗口并储存结果"
	Var.set(newvar)
	Quit(root=root,ask=False)


def UpdateConfig(root:tk.Misc,config:CONFIG,Vars:dict[str,Union[tk.BooleanVar,tk.DoubleVar]],Updated:tk.BooleanVar):
	"更新"
	if not messagebox.askokcancel(title='提示 ',message='确认保存并退出?'):
		root.focus_force()
		return
	#更新配置文件
	NewConfig = config.GetConfig().copy()
	for cfg in Vars:
		NewConfig[cfg] = Vars[cfg].get()
	
	updated = NewConfig["TJ Maxmess Rate"] != config.TJ_MaxRate
	_quit(root,Updated,updated)
	config.SetConfig(NewConfig)


def PopConfigMenuWindow(root:tk.Misc,config:CONFIG)-> bool:
	"弹出设置窗口，更改设置"
	
	#构建窗口
	win_config = tk.Toplevel(root)
	#隐藏最小化最大化按钮
	win_config.transient(root)
	#窗口的大小标题和图标
	win_config.geometry("290x270+400+200")
	win_config.title("设置")
	win_config.iconphoto(False,tk.PhotoImage(file="./Resource/icon.png"))
	#点叉号按钮时关闭窗口的函数
	win_config.protocol('WM_DELETE_WINDOW',lambda:Quit(win_config))

	#安放强制出车标题与会徽的框架
	Frametitle = tk.Frame(win_config)
	Frametitle.pack()
	#强制出车的标题
	Title = tk.Label(Frametitle,text='出车系统设置',font=('华文魏碑',25,"bold"),justify='left',fg='blue4')
	Title.pack(side=tk.RIGHT)
	#会徽
	YAS_logo = ImageTk.PhotoImage(Image.open("./Resource/YAS.png").resize((45,45)))
	Logo = tk.Label(Frametitle, image=YAS_logo,width=40,height=40)
	Logo.pack(side=tk.LEFT)

	#承载全部结果的变量
	OldConfig = config.GetConfig()
	Vars:dict[str,Union[tk.BooleanVar,tk.DoubleVar]] = {cfg:tk.BooleanVar(win_config,value=OldConfig[cfg]) for cfg in OldConfig if isinstance(OldConfig[cfg],bool)}
	Vars["TJ Maxmess Rate"] = tk.DoubleVar(win_config,value=OldConfig["TJ Maxmess Rate"])

	#为UI加上提示窗口，提示窗口的代码是网上代码改的
	Balloon = FakeBalloon(win_config)

	#赤道仪的最大承载重量比例的滑动条
	RateFrame = tk.Frame(win_config)
	RateFrame.pack()
	TJ_RateScale = tk.Scale(RateFrame,label='赤道仪质量占比',font=('方正书宋GBK',11),from_=0.4,to=1.0,orient=tk.HORIZONTAL,resolution=0.01,length=120)
	TJ_RateScale.configure(variable=Vars["TJ Maxmess Rate"])
	TJ_RateScale.pack(pady=5)
	Balloon.bind_widget(TJ_RateScale,"调整望远镜允许的最大重量占\n赤道仪承重多少，该设置可在\n完成后生效，但需要重新进行\n粗细检查")

	#承载设置的复选框
	ConfigFrame = tk.Frame(win_config)
	ConfigFrame.pack(pady=5)

	#显示隐藏器材
	EnableDisableButton = tk.Checkbutton(ConfigFrame,text='显示隐藏器材',font=('方正书宋GBK',11),cursor="hand2",onvalue=True,offvalue=False)
	Balloon.bind_widget(EnableDisableButton,"显示器材列表中被隐藏的器材\n该设置可在完成后立即生效")
	EnableDisableButton.configure(variable=Vars["Display Disable Equipment"])
	EnableDisableButton.grid(row=0,column=0)
	#自动进行细查
	EnableAutoButton = tk.Checkbutton(ConfigFrame,text='自动进行细查',font=('方正书宋GBK',11),cursor="hand2",onvalue=True,offvalue=False)
	Balloon.bind_widget(EnableAutoButton,"在粗检查通过的情况下自动执行细致检查\n该设置可在完成后立即生效")
	EnableAutoButton.configure(variable=Vars["AutoCheckStepTwo"])
	EnableAutoButton.grid(row=0,column=1)
	#按分类导入1
	DetailAlphaButton = tk.Checkbutton(ConfigFrame,text='按分类导入1',font=('方正书宋GBK',11),cursor="hand2",onvalue=True,offvalue=False)
	Balloon.bind_widget(DetailAlphaButton,"若选项为真，则出车系统导入出车记录\n（非临时记录）时会将全部系统分类设\n为器组，否则按当时扫描时的器组情况\n处理。该设置需重新导入记录才能生效")
	DetailAlphaButton.configure(variable=Vars["ImportDataDisplaySoltDetail_Alpha"])
	DetailAlphaButton.grid(row=1,column=0)
	#按分类导入2
	DetailBetaButton = tk.Checkbutton(ConfigFrame,text='按分类导入2',font=('方正书宋GBK',11),cursor="hand2",onvalue=True,offvalue=False)
	Balloon.bind_widget(DetailBetaButton,"若选项为真，则收车系统导入出车记录\n（非临时记录）时会将全部系统分类设\n为器组，否则按当时扫描时的器组情况\n处理。该设置需重新导入记录才能生效")
	DetailBetaButton.configure(variable=Vars["ImportDataDisplaySoltDetail_Beta"])
	DetailBetaButton.grid(row=1,column=1)
	#设置需要密码
	NeedPasswordButton = tk.Checkbutton(ConfigFrame,text='设置需要密码',font=('方正书宋GBK',11),cursor="hand2",onvalue=True,offvalue=False)
	Balloon.bind_widget(NeedPasswordButton,"弹出该窗口需要输入密码\n该设置可在完成后立即生效")
	NeedPasswordButton.configure(variable=Vars["ConfigNeedPassword"])
	NeedPasswordButton.grid(row=2,column=0)
	#禁用版本检测
	EnableOldLogButton = tk.Checkbutton(ConfigFrame,text='禁用版本检测',font=('方正书宋GBK',11),cursor="hand2",onvalue=True,offvalue=False)
	Balloon.bind_widget(EnableOldLogButton,"尝试对储存规则与当前版本\n不同的文件进行导入（可能\n会有bug），但对文件还是\n有基本要求（无法导入2.3\n及以前的版本），该设置可\n在完成后立即生效")
	EnableOldLogButton.configure(variable=Vars["Enable Old Logs"])
	EnableOldLogButton.grid(row=2,column=1)
	
	#确定与返回按钮
	ButtonFrame = tk.Frame(win_config)
	ButtonFrame.pack(pady=5)

	#变量，储存是否更新过赤道仪承载量
	TJ_Updated = tk.BooleanVar(win_config)
	TJ_Updated.set(False)

	tk.Button(ButtonFrame,text='返 回',font=('方正书宋GBK',13),justify='center',cursor="hand2",command=lambda:Quit(win_config)).pack(side=tk.LEFT,padx=5)
	tk.Button(ButtonFrame,text='确 定',font=('方正书宋GBK',13),justify='center',cursor="hand2",command=lambda:UpdateConfig(win_config,config,Vars,TJ_Updated)).pack(side=tk.LEFT,padx=5)

	win_config.focus_force()
	change_language("EN")
	win_config.mainloop()

	return TJ_Updated.get()


def Pop_KeycodeInputWindow(root:tk.Misc,config:CONFIG) -> bool:
	"弹出输入新器组的窗口"
	#构建窗口
	win_keycode = tk.Toplevel(root)
	#隐藏最小化最大化按钮
	win_keycode.transient(root)
	#窗口的大小标题和图标
	win_keycode.geometry("320x100+200+200")
	win_keycode.title("请输入密码")
	win_keycode.iconphoto(False,tk.PhotoImage(file="./Resource/icon.png"))
	#标签与输入框
	tk.Label(win_keycode,text='',font=('方正书宋GBK',6),justify='left').pack()
	tk.Label(win_keycode,text='请输入密码',font=('方正书宋GBK',11),justify='left').pack()
	KeycodeInput = tk.Entry(win_keycode,show="*",font=('Arial Unicode MS',11),width=14)
	KeycodeInput.pack()
	#储存是否继续的结果
	Pass = tk.BooleanVar(win_keycode)
	
	#响应按下回车
	def GetEvent(config:CONFIG,event:tk.Event,VAR:tk.Entry):
		"响应回车键"
		if not (event.keycode == 13):
			return
		if VAR.get() == config.ConfigPassword:
			_quit(win_keycode,Pass,True)
		else:
			messagebox.showwarning("密码错误 ","请输入正确的密码！")
			KeycodeInput.focus_set()
	
	#按叉号退出窗口
	win_keycode.protocol('WM_DELETE_WINDOW',lambda:_quit(win_keycode,Pass,False))
	#按下回车时检查密码
	KeycodeInput.bind('<Key>',lambda event,var=KeycodeInput:GetEvent(config,event,var))
	#聚焦窗口,程序进入主循环，直到窗口被摧毁然后退出并返回相应数值
	win_keycode.focus_force()
	KeycodeInput.focus_set()
	change_language("EN")
	win_keycode.mainloop()
	#返回密码是否正确
	return Pass.get()


def FullPopupConfig(root:tk.Misc,config:CONFIG):
	"验证密码并弹出窗口"
	if config.ConfigNeedPassword and not Pop_KeycodeInputWindow(root,config):
		return False
	return PopConfigMenuWindow(root,config)



	

if __name__ == "__main__":
	win = tk.Tk()
	from ConfigReader import Config
	FullPopupConfig(win,Config)