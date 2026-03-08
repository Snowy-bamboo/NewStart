import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk

import time

from DataReader import AllEquipmentList,AllQZDict,AllTypenameList, SortedAllEquipmentList
from DataReader import Check_Enable, Check_Name, Check_NessName, Check_QZInside, Check_Classify
from DataReader import ReadLog, WriteCurrentLog, WriteLog

from ConfigReader import Config
from UI_config import FullPopupConfig

from ChangeLanguage import change_language

from Doc_alpha import gen_docx, CompileDoc

#多导一个库，用于type hint（数据类型注释）
from typing import Union, Callable


def Foo():
	"调试时的占位函数，最终版橄榄"
	messagebox.showwarning("该程序无功能","请不要点UI.py文件\n如果你正常启动系统\n并遇到该弹窗,联系孙先生")
	return True


#================================全部的UI汇总，程序前端与后端的全部接口走这里。=====================================

class UI_alpha:
	"出车系统的全部UI的容器,包括了大框架与菜单和各类接口"

	#=======初始化===========
	def __init__(self) -> None:
		#构造窗口
		self.win = tk.Tk()
		self.win.transient()
		self.Init_win()
		#构建UI
		self.left_ui = Left_UI(self.win)
		self.middle_ui = Middle_UI(self.win)
		self.right_ui= Right_UI(self.win)
		self.checkui = CheckUI(self.win)
		#构建菜单
		self.Init_Menu()
		#导入UI间跨区域联动的函数
		self.middle_ui.ImportFunction(self.left_ui.Focus, self.checkui.ResetSecondResult)
		self.right_ui.ImportFunction(self.left_ui.Focus)
	
	def BondButtonFunction(self,UpdateMemory:Callable[[dict[str,str]],None], GetMemory:Callable[[],dict[str,str]], StepOneFunction:Callable[[],None], StepTwoFunction:Callable[[],None], Final_Confirm:Callable[[],bool], LastStep:Callable[[],None]):
		"绑定按钮与主逻辑的四个函数"
		#函数与按钮的绑定
		self.checkui.BondButtonFunction(self.left_ui.Focus,self.middle_ui.Check_TJ,StepOneFunction,StepTwoFunction,Final_Confirm,LastStep)
		self.left_ui.ImportFunction(UpdateMemory,self.checkui.ResetFirstResult)
		self.GetMemory = GetMemory
		self.GenerateDoc = (lambda: self.checkui.StepFinalFunction_Judged(Final_Confirm,LastStep))
		#函数与菜单的绑定
		self.filemenu.entryconfig(2,label='生成档案',command=self.GenerateDoc)
		self.win.bind("<Control-p>",lambda event:self.GenerateDoc())
		self.win.bind("<Control-P>",lambda event:self.GenerateDoc())

	#=======WIN的构建===========
	def Init_win(self):
		"以win为基础构造主窗口的主要部件"
		#窗口长宽与弹出位置
		self.win.geometry("%dx%d+%d+%d" % self.win_w_h())
		#窗口边框名称
		self.win.title(f"器材管理系统v{Config.Version}")
		#窗口图标
		self.win.iconphoto(False,tk.PhotoImage(file="./Resource/icon.png"))
		#点叉号按钮时关闭窗口的函数
		self.win.protocol('WM_DELETE_WINDOW', self.QUIT)
		#安放出车系统几个大字与会徽的框架
		self.Frametitle = tk.Frame(self.win)
		self.Frametitle.place(relx=0.5,rely=0.014,anchor='n')
		#出车系统几个大字
		self.Title = tk.Label(self.Frametitle,text=f'器材管理系统v{Config.Version}',font=('华文魏碑',25,'bold'),justify='center',fg='blue4')
		self.Title.pack(side=tk.RIGHT)
		#学会的会徽
		self.YAS_logo = ImageTk.PhotoImage(Image.open("./Resource/YAS.png").resize((45,45)))
		self.Logo = tk.Label(self.Frametitle, image=self.YAS_logo,width=40,height=40)
		self.Logo.pack(side=tk.LEFT)
		#我的名字
		self.Sign = tk.Label(self.win,text='by The Wolf-Rayet',font=('timesnewrom',12,'bold'),justify='center',fg='blue4')
		self.Sign.place(relx=1,rely=1,anchor="se")

	def Init_Menu(self):
		"为出车系统添加头部的菜单"
		#菜单
		self.Menu = tk.Menu(self.win)
		self.win.config(menu=self.Menu)
		#文件部分
		self.filemenu = tk.Menu(self.Menu,tearoff=0)
		self.filemenu.add_command(label="导入记录",command=self.left_ui.Loaddata,accelerator="Ctrl+O")
		self.win.bind("<Control-o>",lambda event:self.left_ui.Loaddata())
		self.win.bind("<Control-O>",lambda event:self.left_ui.Loaddata())
		self.filemenu.add_command(label="暂存记录",command=self.Savedata,accelerator="Ctrl+S")
		self.win.bind("<Control-s>",lambda event:self.Savedata())
		self.win.bind("<Control-S>",lambda event:self.Savedata())
		self.filemenu.add_command(label="",accelerator="Ctrl+P")
		self.filemenu.add_separator()
		self.filemenu.add_command(label="退出",command=self.QUIT,accelerator="Alt+F4")
	
		#编辑部分
		self.editmenu = tk.Menu(self.Menu,tearoff=0,postcommand=self.left_ui.UpdateSubTreeMenuScan)
		self.editmenu.add_command(label="新建器组",command=self.left_ui.AddQZ,accelerator="Ctrl+N")
		self.win.bind("<Control-n>",lambda event:self.left_ui.AddQZ())
		self.win.bind("<Control-N>",lambda event:self.left_ui.AddQZ())
		self.editmenu.add_cascade(label="添加器材",menu=self.left_ui.ChoiceBoxmenuMain)
		self.editmenu.add_command(label="撤销",command=self.left_ui.undo,accelerator="Ctrl+Z")
		self.win.bind("<Control-z>",lambda event:self.left_ui.undo())
		self.win.bind("<Control-Z>",lambda event:self.left_ui.undo())
		self.editmenu.add_command(label="恢复",command=self.left_ui.redo,accelerator="Ctrl+Y")
		self.win.bind("<Control-y>",lambda event:self.left_ui.redo())
		self.win.bind("<Control-Y>",lambda event:self.left_ui.redo())

		#扫码枪扫入器组部分
		self.editmenu.add_cascade(label="扫码枪扫入",menu=self.left_ui.SubTreeMenuScan)
		#继续编辑部分
		self.editmenu.add_separator()
		self.editmenu.add_command(label="清空列表",command=self.left_ui.TreeClear)
		#查看部分
		self.viewmenu = tk.Menu(self.Menu,tearoff=0)
		self.viewmenu.add_command(label="首页",command=lambda:self.right_ui.GotoPage(0),accelerator="Home")
		self.win.bind("<Home>",lambda event:self.right_ui.GotoPage(0))
		self.viewmenu.add_command(label="尾页",command=lambda:self.right_ui.GotoPage(self.right_ui.TotalPage),accelerator="End")
		self.win.bind("<End>",lambda event:self.right_ui.GotoPage(self.right_ui.TotalPage))
		self.viewmenu.add_command(label="上一页",command=lambda:self.right_ui.LeftButtonFunction(),accelerator="PgUp")
		self.win.bind("<Prior>",lambda event:self.right_ui.LeftButtonFunction())
		self.viewmenu.add_command(label="下一页",command=lambda:self.right_ui.RightButtonFunction(),accelerator="PgDn")
		self.win.bind("<Next>",lambda event:self.right_ui.RightButtonFunction())


		self.left_ui.EquipmentTree.bind("<Delete>",lambda event:self.left_ui.TreeDelete())

		#self.win.bind("<Up>",lambda event:self.right_ui.LeftButtonFunction())
		#self.win.bind("<Down>",lambda event:self.right_ui.RightButtonFunction())
		#self.win.bind("<Left>",lambda event:self.right_ui.LeftButtonFunction())
		#self.win.bind("<Right>",lambda event:self.right_ui.RightButtonFunction())

		#设置部分
		self.setmenu = tk.Menu(self.Menu,tearoff=0)
		self.setmenu.add_command(label="设置",command=lambda:[self.ConfigFunction(),self.Focus()],accelerator="F9")
		self.win.bind("<F9>",lambda event: [self.ConfigFunction(),self.Focus()])
		#帮助部分
		self.helpmenu = tk.Menu(self.Menu,tearoff=0)
		self.helpmenu.add_command(label="帮助",command=lambda:messagebox.showwarning("才不是作者懒得写文档","赶紧去培训，\n不会出车的东西！"),accelerator="F10")
		self.win.bind("<F10>",lambda event:messagebox.showwarning("才不是作者懒得写文档","赶紧去培训，\n不会出车的东西！"))
		self.helpmenu.add_separator()
		self.helpmenu.add_command(label="关于",command=lambda:messagebox.showinfo("关于系统",
			f"版本: v{Config.Version}\n作者: The Wolf-Rayet\n不要用出车系统2.0的存档做测试，会弹窗\n不易发现的更新:\n最右侧检查报告界面点每个具体器组试试\n然后再点该器组标题试试"))
		#整合菜单
		self.Menu.add_cascade(label="文件",menu=self.filemenu)
		self.Menu.add_cascade(label="编辑",menu=self.editmenu)
		self.Menu.add_cascade(label="查看",menu=self.viewmenu)
		self.Menu.add_cascade(label="设置 ",menu=self.setmenu)
		self.Menu.add_cascade(label="帮助",menu=self.helpmenu)

	def ConfigFunction(self):
		"按下设置键执行的函数"
		if FullPopupConfig(self.win,Config):
			self.CheckUI_ResetFirstResult()
		self.left_ui.Init_Choice_BoxMenu()
		self.editmenu.entryconfigure(1,menu=self.left_ui.ChoiceBoxmenuMain)

	#=======保存档案===========
	def Savedata(self):
		"将当前出车状态储存为临时文件"
		treedata = self.GetEquipmentTree()
		pushdata = self.GetMemory()
		currentcode = self.left_ui.FakeCode
		WriteCurrentLog(treedata, pushdata, currentcode)

	#=======前端与后端的几个接口===========
	def Focus(self):
		"将光标移到输入框，方便扫码枪输入"
		self.left_ui.Focus()
	
	def GetInputEquipmentList(self) -> list[str]:
		"返回扫码枪输入的器材列表"
		#从左侧UI中调用该功能
		return self.left_ui.GetEquipmentList()

	def GetEquipmentTree(self) -> dict[str,dict[str,Union[str, list[str]]]]:
		"返回器材的树结构"
		return self.left_ui.GetEquipmentTree()

	def Middle_Reset(self):
		"重置中部的UI，清空杂项区与器材配对菜单，将UI回到未检测器材的时候"
		self.middle_ui.Reset()
	
	def Middle_UpdateZX(self,ZX_data:dict[str,int]):
		"更新屏幕中部的杂项统计菜单"
		self.middle_ui.UpdateZX(ZX_data)
	
	def Middle_BuildCYPair(self,TJ_data:dict[str,float],Root_data: dict[str,dict[str, Union[float,bool]]]):
		"将输入的望远镜与赤道仪按照默认配对，并在中部构建菜单"
		#==================数据的交互格式=========================
		#TJ_data = {code1:mess1,...} 记录每个望远镜的载重
		#Root_data = {code1:{"mess":mess1, "DC":T/F},...} 记录每个根器材的承重与是否可供电
		#若某个根器材不匹配望远镜，则该器材的mess数值设为-1
		self.middle_ui.BuildCYPair(TJ_data,Root_data)

	def GetPackageData(self)->tuple[dict[str,str],dict[str,bool]]:
		"将望远镜匹配的数据传出"
		return self.middle_ui.GetPackageData()

	def GetZXData(self)-> tuple[dict[str,str],dict[str,str]]:
		"返回杂项统计菜单的数据与颜色"
		return self.middle_ui.GetZXData()

	def Right_Reset(self):
		"重置显示最后配对结果的UI"
		self.right_ui.Reset()

	def Right_UpdateData(self,pk_data:list[dict[str,Union[str,bool,list[str]]]]):
		"将器材包信息传入UI"
		self.right_ui.UpdateData(pk_data)

	def CheckUI_FirstStep(self,StepOneCheckResult:bool):
		"根据粗检查后的结果对UI的通过标签进行更新"
		self.checkui.FirstStep(StepOneCheckResult)

	def CheckUI_SecondStep(self,StepTwoCheckResult:bool):
		"根据细检查后的结果对UI的通过标签进行更新"
		self.checkui.SecondStep(StepTwoCheckResult)
	
	def CheckUI_ResetFirstResult(self):
		"由于更新导致粗检查与细检查结果均作废,需要改变结果的记录状态并对UI的标签进行更新"
		self.checkui.ResetFirstResult()

	def CheckUI_ResetSecondResult(self):
		"由于更新导致细检查结果作废,需要改变结果的记录状态并对UI的标签进行更新"
		self.checkui.ResetSecondResult()

	#窗口的弹出位置设置，某种意义上是一坨祖传屎山，望后人更仔细的调参
	def win_w_h(self,screen_height = 1200,screen_width = 2200):
		"窗口格式长宽高弹出位置的设置"
		win_width = 0.46 * screen_width
		win_height = 0.57 * screen_height
		show_width = (screen_width - win_width) / 8
		show_height = (screen_height - win_height) / 8
		return win_width, win_height, show_width, show_height

	#窗口的弹出
	def mainloop(self):
		"开始前端UI窗口的主循环"
		#将语言换为英文
		change_language("EN")
		self.win.focus_force()
		self.Focus()
		self.win.mainloop()

	#退出程序时的警告
	def QUIT(self):
		"退出出车系统，点X时运行。"
		if messagebox.askokcancel(title='警告',message='确认退出系统?'):
			self.win.quit()
			self.win.destroy()
		else:
			self.Focus()
			
		


#================================封装GUI用的class=====================================

class Left_UI:
	"出车系统左半边UI，包含了扫描部分与输入框"
	#==================撤销与恢复操作的存储格式=========================
	#添加操作：{"active":"add", "item":[code1,...]}
	#移动操作：{"active":"move", "item":code, "parent":parent, "index":index}
	#删除操作：{"active":"delete", "item":code, "parent":parent, "index":index, "child":(code1,...))}
	#重做添加操作：{"redo":"add", "list":[{"item":item,"parent":parent,"index":index},....], "undocommand":command}
	#重做移动操作：{"redo":"move", "item":code, "parent":parent, "index":index, "undocommand":command}
	#重做删除操作：{"redo":"delete", "item":code, "undocommand":command}

	#=======初始化===========
	def __init__(self, win:tk.Misc):
		#存储完成的操作
		self.Actives:list[dict[str,Union[str,list,int]]] = list()
		#存储已完成的撤销操作（即可以重做的）
		self.UndoActives:list[dict[str,Union[str,list,int,dict]]] = list()
		#存储扫码枪输入的器组，默认为根目录
		self.CurrentRoot = tk.StringVar(win)
		self.CurrentRoot.set("")
		#储存全部器组，包括新增的
		self.AllQZDict = AllQZDict.copy()
		#存储当前的伪code
		self.FakeCode = 1

		#构建UI
		self.win = win
		self.Init_upUI()
		self.Init_Choice_BoxMenu()
		self.Init_downUI()
		self.Init_TreeMenu()

	def ImportFunction(self,UpdateMemory:Callable[[dict[str,str]],None], CheckUI_updatefunction:Callable[[],None]):
		"导入与memory交互的函数和重置checkUI的函数"
		self.UpdatePushData = UpdateMemory
		self.CheckUI_updatefunction = CheckUI_updatefunction

	def Check_Name(self,code:str)->str:
		"改写的CheckName，适用于自定义器组"
		if code in self.AllQZDict:
			return self.AllQZDict[code]
		else:
			return Check_Name(code)

	#=====各种UI的初始化=====
	def Init_upUI(self):
		"构建上半部分UI"
		#构建UI上一半区域的UI
		self.FrameInput = tk.Frame(self.win,width=200,height=60)
		self.FrameInput.place(relx=1/6,rely=0.1,anchor='n')
		#标题
		self.inputlabel = tk.Label(self.FrameInput,text='请输入器材编号',font=('方正书宋GBK',11),justify='left')
		self.inputlabel.grid(column=0,row=0,sticky='w')
		#手动选择器材的菜单
		self.ChoiceCode = tk.Button(self.FrameInput,text='选择',font=('方正书宋GBK',11),justify='center',cursor="hand2")
		self.ChoiceCode.grid(column=1,row=0,sticky='e')
		self.ChoiceCode.config(command=self.ChoiceMenuPopup)
		#器材编号输入框并绑定指令
		self.ActiveCode = tk.Entry(self.FrameInput,show=None,font=('Arial Unicode MS',11),width=14)
		self.ActiveCode.grid(column=0,row=1,sticky='w',padx=2)
		self.ActiveCode.bind('<Key>',self.InputEnter)
		#确定输入的按钮
		self.EnterButton =  tk.Button(self.FrameInput,text='确定',font=('方正书宋GBK',11),justify='center',command=self.GetCode,cursor="hand2")
		self.EnterButton.grid(column=1,row=1,sticky='e')
		#导入记录按钮
		self.LoadButton = tk.Button(self.FrameInput,text='导入使用记录',width=12,font=('方正书宋GBK',10),justify='center',command=self.Loaddata,cursor="hand2")
		self.LoadButton.grid(column=0,row=2,sticky='w',pady=2,padx=2)

	def Init_downUI(self):
		"构建下半部分UI"
		#下半部分Frame
		self.FrameList = tk.Frame(self.win,width=160,height=395)
		self.FrameList.place(relx=1/6,rely=0.26,anchor='n')
		#下半部分标签
		self.labelframe = tk.Frame(self.FrameList,width=120,height=40)
		self.labelframe.pack(side=tk.TOP,fill=tk.BOTH)
		self.listlabel = tk.Label(self.labelframe,text='当前器材列表',font=('方正书宋GBK',11),justify="left")
		self.listlabel.pack(side=tk.LEFT)
		#Canvas，承载撤销恢复与新建器组按钮
		self.EqboxTitle = tk.Canvas(self.FrameList,width=150,height=40)
		self.EqboxTitle.pack(side=tk.TOP,fill=tk.X)
		#撤销与恢复按钮
		#self.undoredo = tk.Canvas(self.EqboxTitle,width=120,height=40)
		#self.undoredo.pack(side=tk.RIGHT)
		#撤销按钮
		self.UndoButton = tk.Button(self.EqboxTitle,text='撤销',font=('方正书宋GBK',10),justify='center',command=self.undo,cursor="hand2")
		self.UndoButton.pack(side=tk.LEFT,fill=tk.X)
		#恢复按钮
		self.RedoButton = tk.Button(self.EqboxTitle,text='恢复',font=('方正书宋GBK',10),justify='center',command=self.redo,cursor="hand2")
		self.RedoButton.pack(side=tk.RIGHT)
		#新建按钮
		self.NewQZButton = tk.Button(self.EqboxTitle,text='自定义器组',font=('方正书宋GBK',10),justify='center',command=self.AddQZ,cursor="hand2")
		self.NewQZButton.pack(side=tk.BOTTOM,fill=tk.BOTH)
		

		#Frame,承装列表和滚动条
		self.FrameTree = tk.Frame(self.FrameList,width=170,height=350)
		self.FrameTree.pack(side=tk.TOP,fill=tk.BOTH)
		#滚动条
		self.scroll = tk.Scrollbar(self.FrameTree,orient="vertical")
		self.scroll.pack(side=tk.RIGHT,fill=tk.Y)
		#配置器材列表的样式
		style = ttk.Style()
		style.configure('Treeview',font=(None,10),borderwidth=0)
		#器材列表
		self.EquipmentTree = ttk.Treeview(self.FrameTree,show="tree",selectmode="browse",height=18,yscrollcommand=self.scroll.set,columns = ['text'])
		self.EquipmentTree.pack(side=tk.LEFT,fill=tk.BOTH)
		self.EquipmentTree.column("#0", width=20, minwidth=20)
		self.EquipmentTree.column("text",width=130, minwidth=130)
		self.EquipmentTree.bind("<Button-3>", self.TreeMenuPopup)
		#绑定滚动条
		self.scroll.config(command=self.EquipmentTree.yview)
		#颜色设置
		self.EquipmentTree.tag_configure("InQZ",foreground="silver")
		self.EquipmentTree.tag_configure("OutQZ",foreground="black")

	def Init_Choice_BoxMenu(self):
		"构建手动选择器材菜单"
		#创建下拉菜单
		self.ChoiceBoxmenuMain = tk.Menu(self.ChoiceCode,tearoff=0)
		#添加子菜单
		#创建一些列菜单，记录着每种器材种类对应的菜单是哪个(这里面同时包含了一级和二级菜单)
		self.PopupMenuDict = {tp:tk.Menu(self.ChoiceBoxmenuMain,tearoff=0) for tp in AllTypenameList}
		#大部分种类，一级菜单即可满足要求
		for tp in self.PopupMenuDict:
			self.ChoiceBoxmenuMain.add_cascade(label=tp,menu=self.PopupMenuDict[tp])
		#构建每个具体器材，点击该器材可以将其编号输入输入框
		
		for eq in filter(Check_Enable,SortedAllEquipmentList):
			self.PopupMenuDict[Check_Classify(eq)].add_command(label=f'{eq}: {self.Check_Name(eq)}',command=lambda code=eq: self.ChoiceEquipment(code))
		
	def Init_TreeMenu(self):
		"构建在器材列表右键出现的UI"
		self.TreeMenu = tk.Menu(self.win,tearoff=0)
		#第一行显示器材的编号，随右键点击事件自动更换内容
		self.TreeMenu.add_command(label="Undefined Value", command=self.Focus)
		#第二行为删除单件器材
		self.TreeMenu.add_command(label="删除", command=self.TreeDelete)
		#第三行是根目录转移菜单
		self.SubTreeMenuMove = tk.Menu(self.TreeMenu,tearoff=0)
		self.TreeMenu.add_cascade(label="移动到",menu=self.SubTreeMenuMove)
		#第四行是将扫码枪扫入
		self.SubTreeMenuScan = tk.Menu(self.TreeMenu,tearoff=0)
		self.TreeMenu.add_cascade(label="扫码枪扫入",menu=self.SubTreeMenuScan)
		#第五行为清空列表，与前两行之间加下划线
		self.TreeMenu.add_separator()
		self.TreeMenu.add_command(label="清空列表", command=self.TreeClear)

	#===按下各个按钮时的操作===
	def InputEnter(self,event:tk.Event):
		"输入框按下回车键时执行响应"
		if event.keycode == 13:
			self.GetCode()

	def GetCode(self):
		"按下确定按钮时的操作"
		self.Focus()
		code = self.ActiveCode.get()
		self.ActiveCode.delete("0","end")
		if code in AllEquipmentList:
			#状态设置成刚出车
			self.CheckUI_updatefunction()
			#在UI里添加
			self.TreeAdd(code)

	def undo(self):
		"按下撤销按钮时执行"
		self.Focus()
		#确定列表不为空	
		if not len(self.Actives):
			return
		#读取指令
		command = self.Actives.pop()
		#按添加 移动 删除三种情况记录数据并执行逆操作
		if command["active"] == "add":
			RedoList = []
			for item in command["item"]:
				#记录数据
				parent = self.EquipmentTree.parent(item)
				index = self.EquipmentTree.index(item)
				RedoList.append({"item":item,"parent":parent,"index":index})
				#执行撤销操作
				self.EquipmentTree.delete(item)
			#保存撤销操作
			RedoList.reverse()
			self.UndoActives.append({"redo":"add","list":RedoList,"undocommand":command})
			#状态设置成刚出车
			self.CheckUI_updatefunction()
		
		elif command["active"] == "move":
			#保存撤销操作
			code = command["item"]
			redoparent = self.EquipmentTree.parent(code)
			redoindex = self.EquipmentTree.index(code)
			self.UndoActives.append({"redo":"move","item":code,"parent":redoparent,"index":redoindex,"undocommand":command})
			#执行撤销操作
			self.EquipmentTree.move(code,command["parent"],command["index"])
		
		elif command["active"] == "delete":
			#保存撤销操作
			code = command["item"]
			self.UndoActives.append({"redo":"delete","item":code,"undocommand":command})
			#执行撤销操作		
			self.EquipmentTree.insert(command["parent"],command["index"],iid=code,text='',value=[self.Check_Name(code)])
			for index,item in enumerate(command["child"],0):
				self.EquipmentTree.insert(code,index,iid=item,text='',value=[self.Check_Name(item)])
			#状态设置成刚出车
			self.CheckUI_updatefunction()
		
		#更新颜色
		self.UpdateColor()
	
	def redo(self):
		"按下恢复按钮时执行"
		self.Focus()
		#确定列表不为空
		if not len(self.UndoActives):
			return
		#读取指令并更新撤销列表
		command = self.UndoActives.pop()
		self.Actives.append(command["undocommand"])
		#重做添加 移动 删除三种情况
		if command["redo"] == "add":
			#重做该操作
			for active in command['list']:
				self.EquipmentTree.insert(active["parent"],active["index"],iid=active["item"],text='',value=[self.Check_Name(active["item"])])
			#状态设置成刚出车
			self.CheckUI_updatefunction()
		if command["redo"] == "move":
			#重做该操作
			self.EquipmentTree.move(command["item"],command["parent"],command["index"])
		elif command["redo"] == "delete":
			#重做该操作
			self.EquipmentTree.delete(command["item"])
			#状态设置成刚出车
			self.CheckUI_updatefunction()
		
		#更新颜色
		self.UpdateColor()

	def AddQZ(self):
		"添加自定义器组时的函数"
		new = Pop_NewQZInputWindow(self.win)
		if len(new):
			#构造伪code，并使得伪code加一
			code = "FakeQZ"+str(self.FakeCode)
			self.FakeCode += 1
			#将自定义器组加入字典
			self.AllQZDict[code] = new
			#添加该器组至树
			self.TreeAdd(code)

	def Loaddata(self):
		"导入出车记录"
		#获取文件路径
		path = filedialog.askopenfilename(title='选择导入的观测记录',initialdir ='./Temporary',filetypes=[('json','*.json'),('All Files','*')])
		#导入文件
		log =  ReadLog(path)

		#对导入不正确情况的检测(关闭窗口或文件名有误)
		if path == "":
			return
		elif isinstance(log,bool):
			messagebox.showwarning("系统提示","请输入正确的文件！")
			return
		#清空原来的数据
		self.TreeClear(pop=False)
		#更新参数
		self.UpdatePushData(log["pushdata"])
		self.FakeCode:int = log["other"]["currentcodefull"] if Config.Detail_Alpha else log["other"]["currentcodetree"]
		pkdata = log["pkdata"] if Config.Detail_Alpha else log["treedata"]
		pkdata.sort(key=lambda pk: (-len(pk["inside"]) if (pk["code"] != "") else 1))
		#重新构建树，这里先跳过
		for pk in pkdata:
			pk:dict[str,Union[str,list[str]]]
			root:str = pk["code"]
			name:str = pk["name"]
			if root != "":
				self.EquipmentTree.insert("",tk.END,iid=root,text='',value=[name])
				self.AllQZDict[root] = name
			for item in pk["inside"]:
				self.EquipmentTree.insert(root,tk.END,iid=item,text='',value=[self.Check_Name(item)])
		#聚焦
		self.Focus()
		self.UpdateColor()

	
	#===选择器材弹出菜单的函数===
	def ChoiceMenuPopup(self):
		"按手动选择器材按钮时弹出"
		self.Focus()
		self.ChoiceBoxmenuMain.tk_popup(self.ChoiceCode.winfo_rootx()+0, self.ChoiceCode.winfo_rooty()+28, 0)

	def ChoiceEquipment(self,code:str):
		"手动输入器材菜单选择某个器材时执行"
		self.ActiveCode.delete(0,tk.END)
		self.ActiveCode.insert(0,code)
		self.Focus()

	def TreeMenuPopup(self,event:tk.Event):
		"在器材列表右键时执行"
		#获取菜单的位置
		code = self.EquipmentTree.selection()
		self.Focus()
		#跳过空表
		if not len(code):
			return
		code = code[0]
		#第一步，改名字
		self.TreeMenu.entryconfig(0,label=code)
		#第二步，更新UI
		self.SubTreeMenuMove.delete(0,tk.END)
		#器组可以设为默认输入者
		#器组无法移动，非器组可以引动到根目录与全部其他器组
		if code not in self.AllQZDict:
			self.SubTreeMenuMove.add_command(label='根目录',command=lambda g='': self.TreeMove(g))
			for qz in self.EquipmentTree.get_children(""):
				self.SubTreeMenuMove.add_command(label=self.Check_Name(qz),command=lambda g=qz: self.TreeMove(g)) if qz in self.AllQZDict else None
		else:
			self.SubTreeMenuMove.add_command(label='器组无法移动')
		#更新“扫描进”菜单
		self.UpdateSubTreeMenuScan()
		#弹出窗口
		self.TreeMenu.post(event.x_root, event.y_root)

	def UpdateSubTreeMenuScan(self):
		"更新扫码枪扫入的菜单"
		self.SubTreeMenuScan.delete(0,tk.END)
		self.SubTreeMenuScan.add_command(label='根目录',command=lambda g='': self.CurrentRoot.set(g))
		CurrentAllQZ = list(filter((lambda code:code in self.AllQZDict), self.EquipmentTree.get_children('')))	
		if len(CurrentAllQZ):
			self.SubTreeMenuScan.add_separator()
		for qz in CurrentAllQZ:
			self.SubTreeMenuScan.add_radiobutton(label=self.Check_Name(qz),value=qz, command=lambda g=qz: self.CurrentRoot.set(g),variable=self.CurrentRoot)


	#===对器材列表的操作===
	def TreeAdd(self,code:str):
		"在器材列表里增加器材"
		#储存要添加的东西
		Appendlist = []

		#添加器材
		if code in AllQZDict: #！！！这里是特指真器组而非自己创建的伪器组，所以是全局变量！！！
			#添加器组的情况，先添加根目录
			if not self.EquipmentTree.exists(code):
				self.EquipmentTree.insert('',tk.END,iid=code,text='',value=[self.Check_Name(code)])
				Appendlist.append(code)
			#添加每一个器材
			for item in Check_QZInside(code):
				if not self.EquipmentTree.exists(item):
					Appendlist.append(item)
					self.EquipmentTree.insert(code,tk.END,iid=item,text='',value=[self.Check_Name(item)])
		elif code in self.AllQZDict:
			#自定义器组的情况
			Appendlist.append(code)
			#添加器材至当前指定的目录
			self.EquipmentTree.insert("",tk.END,iid=code,text='',value=[self.Check_Name(code)])
		elif not self.EquipmentTree.exists(code):
			#添加新器材的情况
			Appendlist.append(code)
			#添加器材至当前指定的目录
			self.EquipmentTree.insert(self.CurrentRoot.get(),tk.END,iid=code,text='',value=[self.Check_Name(code)])
		
		#若确实添加了东西，则加入操作顺序并清空“恢复”列表
		if len(Appendlist):
			Appendlist.reverse()
			self.Actives.append({"active":"add","item":Appendlist})
			self.UndoActives.clear()
		
		#更新颜色
		self.UpdateColor()

	def TreeMove(self,goal:str):
		"将器材移动到某个器组内"
		code = self.EquipmentTree.selection()[0]
		parent = self.EquipmentTree.parent(code)
		index = self.EquipmentTree.index(code)
		#移动，在操作记录中添加该记录并清空“恢复”列表
		if parent != goal:
			self.EquipmentTree.move(code,goal,tk.END)
			self.Actives.append({"active":"move", "item":code, "parent":parent, "index":index})
			self.UndoActives.clear()
		self.Focus()

		#更新颜色
		self.UpdateColor()

	def TreeDelete(self):
		"删除单独的物品"
		code = self.EquipmentTree.selection()[0]
		parent = self.EquipmentTree.parent(code)
		index = self.EquipmentTree.index(code)
		child = self.EquipmentTree.get_children(code)
		#删除并将扫码枪扫入目录回归根目录
		if self.CurrentRoot.get() == code:
			self.CurrentRoot.set("")
		self.EquipmentTree.delete(code)
		#操作记录中添加该记录
		self.Actives.append({"active":"delete", "item":code, "parent":parent, "index":index, "child":child})
		#清空“恢复”列表
		self.UndoActives.clear()
		self.Focus()
		#状态设置成刚出车
		self.CheckUI_updatefunction()

		#更新颜色
		self.UpdateColor()

	def TreeClear(self,pop=True):
		"清空列表"
		if pop and (not messagebox.askokcancel("警告","确定删除全部器材？\n该过程无法被撤销！")):
			return
		#重置自定义器组数据
		self.CurrentRoot.set("")
		self.AllQZDict.clear()
		self.AllQZDict = AllQZDict.copy()
		self.FakeCode = 1
		#UI重置
		self.EquipmentTree.delete(*self.EquipmentTree.get_children(""))
		self.Actives.clear()
		self.UndoActives.clear()
		self.Focus()
		#状态设置成刚出车
		self.CheckUI_updatefunction()

	def UpdateColor(self):
		"更新每个器材的颜色"
		for code in self.EquipmentTree.get_children(""):
			self.EquipmentTree.item(code,tags="OutQZ")
			list(map(lambda x:self.EquipmentTree.item(x,tags="InQZ"),self.EquipmentTree.get_children(code)))
				

	#===鼠标焦点回到输入框===
	def Focus(self):
		"将光标挪到输入框，提高出车系统稳定性"
		self.ActiveCode.focus_set()
	
	#===返回全部器材的清单，接入下游程序===
	def GetEquipmentList(self)->list[str]:
		"返回全部器材的列表"
		EquipmentList = []
		for code in self.EquipmentTree.get_children(""):
			if code in self.AllQZDict:
				EquipmentList += list(self.EquipmentTree.get_children(code))
			else:
				EquipmentList.append(code)
		return EquipmentList

	def GetEquipmentTree(self) -> dict[str,dict[str,Union[str,list[str]]]]:
		"返回器材的树结构"
		EquipmentDict:dict[str,dict[str,Union[str,list[str]]]] = {"":{"name":"root","inside":[]}}
		for code in self.EquipmentTree.get_children(""):
			if code in self.AllQZDict:
				EquipmentDict[code] = {"name":self.AllQZDict[code],"inside":list(self.EquipmentTree.get_children(code))}
			else:
				EquipmentDict[""]["inside"].append(code)
		return EquipmentDict




class Middle_UI:
	"出车系统中间部分UI，包含了赤道仪配对部分与杂项统计"
	#==================数据的交互格式=========================
	#TJ_mess = {code1:mess1,...} 记录每个望远镜的载重
	#Root_data = {code1:{"mess":mess1, "DC":T/F},...} 记录每个根器材的承重与是否可供电
	#若某个根器材不匹配望远镜，则该器材的mess数值设为-1

	#=======初始化===========
	def __init__(self,win:tk.Misc):
		#数据初始化
		self.TJ_mess:dict[str,float] = dict() #存储望远镜的质量
		self.Root_mess:dict[str,float] = dict() #存储赤道仪的可承受载重
		self.OptionDict:dict[str,str] = dict() #下拉菜单的望远镜列表与code的关系
		self.PackageData:dict[str,dict[str,Union[tk.BooleanVar,tk.StringVar]]] = dict() #记录望远镜与赤道仪配对信息与是否要电源
		self.CYUI_Data:dict[str,dict[str,Union[tk.Label,tk.OptionMenu,tk.Checkbutton]]] = dict() #记录该部分的UI
		self.N_TJ = 0 #望远镜数目
		self.N_DC = 0 #电池数目
		self.N_DX = 0 #电线数目
		#UI初始化
		self.win = win
		self.Init_upUI()
		self.Init_downUI()

	def ImportFunction(self, LeftUI_focusfunction:Callable[[],None], CheckUI_updatefunction:Callable[[],None]):
		"将聚焦左侧UI输入框的函数与更新检查结果UI的函数导入"
		self.LeftUI_focusfunction = LeftUI_focusfunction
		self.CheckUI_updatefunction = CheckUI_updatefunction

	#=====各种UI的初始化=====
	def Init_upUI(self):
		"望远镜与赤道仪匹配菜单初始化"
		#赤道仪匹配的标签
		self.LabelCY = tk.Label(self.win,text='赤道仪匹配',font=('方正书宋GBK',11),justify='left')
		self.LabelCY.place(relx=0.5,rely=0.1,anchor='n')
		#该部分的主框架与为了滚动条的Canvas
		self.Frame = tk.Frame(self.win,width=200,height=290)
		self.Frame.place(relx=0.5,rely=0.14,anchor='n')
		self.Canvas = tk.Canvas(self.Frame,width=184)
		self.Canvas.place(relx=0,rely=0.5,relheight=1,anchor='w')
		#真正的容纳UI的框架
		self.FrameCYlist = tk.Frame(self.Frame)
		self.FrameCYlist.place(relx=0.5,rely=0.5,relheight=1,relwidth=1,anchor='center')
		#滚动条
		self.scroll = tk.Scrollbar(self.Frame,orient="vertical")
		self.scroll.place(relx=1,rely=0.5,relheight=1,anchor='e')
		#将框架放入Canvas中
		self.Canvas.create_window((0,0),window=self.FrameCYlist,anchor='nw')
		#滚动条绑定
		self.scroll.config(command=self.Canvas.yview)
		self.Canvas.config(yscrollcommand=self.scroll.set,scrollregion=self.Canvas.bbox("all"))
		#撑开框架
		tk.Label(self.FrameCYlist,text=f"           ",font=('方正书宋GBK',11),justify='center').grid(column=0,row=0)
		tk.Label(self.FrameCYlist,text=f"           ",font=('方正书宋GBK',11),justify='center').grid(column=2,row=0)
		#更新UI与滚动条
		self.UpdateScroll()
	
	def Init_downUI(self):
		"杂项的统计菜单"
		#各种杂项统计菜单的Frame
		self.FrameOther = tk.Frame(self.win,width=250,height=150)
		self.FrameOther.place(relx=0.5,rely=0.60,anchor='n')
		#占空间用Label，作为文字与数字间的空格
		self.SpaceLabel = tk.Label(self.FrameOther,text='     ',font=('方正书宋GBK',11),justify='left')
		self.SpaceLabel.grid(row=0,column=1)

		#各个检查项的名称标签UI
		self.OtherCheckLabels:dict[str,tk.Label] = dict()
		#各个检查项的结果显示UI
		self.OtherCheckDatas:dict[str,tk.Label] = dict()
		#各个检查项的名称
		self.ZXNames = {"查重检测":"查重检测","DC":"电池数","DX":"电线数","SJ":"双筒数","PAD":"防潮垫数","LASER":"指星笔数","PHONE":"手机支架","LIGHT":"光源"}
		#各个检查项的默认最低数目
		self.ZXBaseNumber = {"SJ":2,"PAD":1,"LASER":2,"PHONE":0,"LIGHT":0}

		for Row,code in enumerate(["查重检测","DC","DX","SJ","PAD","LASER","PHONE","LIGHT"]):
			#标签
			self.OtherCheckLabels[code] = tk.Label(self.FrameOther,text=self.ZXNames[code],font=('方正书宋GBK',11),justify='left')
			self.OtherCheckLabels[code].grid(row=Row,column=0,sticky=tk.W)
			#数值
			self.OtherCheckDatas[code] = tk.Label(self.FrameOther,text="0",font=('方正书宋GBK',11),justify='left',fg="orange")
			self.OtherCheckDatas[code].grid(row=Row,column=2)
		#将查重检测默认改为未检测
		self.OtherCheckDatas["查重检测"].config(text="未检测",fg="orange")

	#=====传入数据时UI的构建=====
	def UpdateZX(self,ZX_data:dict[str, int]):
		"更新杂项统计菜单"
		self.N_DC = ZX_data["DC"] #记录电池数目
		self.N_DX = ZX_data["DX"] #记录电线数目
		COLOR = lambda x: "green" if x>=0 else "orange" #每种东西的颜色
		#数目更新
		for item in ZX_data:
			self.OtherCheckDatas[item].config(text=str(ZX_data[item]))
		#颜色更新
		for item in self.ZXBaseNumber:
			self.OtherCheckDatas[item].config(fg=COLOR(ZX_data[item]-self.ZXBaseNumber[item]))

	def BuildCYPair(self,TJ_mess:dict[str,float],Root_data:dict[str,dict[str,Union[bool, float]]]):
		"构建赤道仪菜单"
		self.TJ_mess = TJ_mess.copy()
		self.Root_mess = {code:Root_data[code]["mess"] for code in Root_data}
		Root_DC:dict[str,bool] = {code:Root_data[code]["DC"] for code in Root_data}
		#望远镜的数目
		self.N_TJ = len(TJ_mess)
		#记录每个跟器材所匹配的的状态，作为参数传入第二步细检查
		self.PackageData = {code:{"TJ":tk.StringVar(self.FrameCYlist), "DC":tk.BooleanVar(self.FrameCYlist)} for code in Root_data}
		#储存每个根器材连接的UI
		self.CYUI_Data = {code:dict() for code in Root_data}

		#从重到轻对望远镜与根器材排序
		TJ_list = sorted(list(TJ_mess),key = lambda tj: -TJ_mess[tj])
		#对于不支持望远镜配对的器材，由于mess为-1，故会排在最后
		Root_list = sorted(list(Root_data),key = lambda root: -self.Root_mess[root])
		#复选框的选项表
		self.OptionDict = {f"{cd}:{Check_Name(cd)}":cd for cd in TJ_list}
		self.OptionDict.update({"Empty":"Empty"})

		#绘制望远镜赤道仪匹配UI
		#利用ROW来对行进行计数
		#每一组Ui为2-4行，对应着每个器材包
		#第一行显示包的根器材code与根器材名称
		#第二行显示望远镜的总表单与其匹配的望远镜的名称(可以为【Empty】)，若该根器材可配对望远镜
		#第三行显示该器材包是否接受电源匹配的复选框与结果，若该根器材支持电源匹配
		#第四行为空行，即两个器材包UI显示之间的间隔

		index = 0 #记录望远镜选到了第几个
		Row = 0 #让每个控件更新时记录其所在第几行
		for index,root in enumerate(Root_list,0):
			#======第一行内容========
			#包的根器材编码
			self.CYUI_Data[root]["root_code"] = tk.Label(self.FrameCYlist,text=root,font=('方正书宋GBK',11),justify='center')
			self.CYUI_Data[root]["root_code"].grid(column=0,row=Row)
			#包的根器材名字
			self.CYUI_Data[root]["root_name"] = tk.Label(self.FrameCYlist,text=Check_Name(root),font=('方正书宋GBK',11),justify='center',wraplength=80)
			self.CYUI_Data[root]["root_name"].grid(column=1,row=Row)
			Row += 1

			#=======第二行内容=========
			#每个器材中望远镜的默认值
			tj = (TJ_list[index] if index < len(TJ_list) else "Empty") if self.Root_mess[root] > 0 else "disable"
		
			if tj == "disable": #情况1，不支持望远镜配对
				#后面跳过望远镜匹配
				self.PackageData[root]["TJ"].set("Empty")
			
			elif tj == "Empty": #情况2，望远镜数目不够用光了
				#后面跳过望远镜匹配
				self.PackageData[root]["TJ"].set("Empty")
				#望远镜选择的复选框
				self.CYUI_Data[root]["tj_option"] = tk.OptionMenu(self.FrameCYlist,self.PackageData[root]["TJ"],*self.OptionDict,command=(lambda TJ,ROOT1=root: self.Update_tj_pair(TJ,ROOT1)))
				self.CYUI_Data[root]["tj_option"].configure(cursor="hand2")
				self.CYUI_Data[root]["tj_option"].grid(column=0,row=Row)
				#对应的望远镜名字设为无名称
				self.CYUI_Data[root]["tj_name"] = tk.Label(self.FrameCYlist,text="---",font=('方正书宋GBK',11),justify='center',fg='orange')
				self.CYUI_Data[root]["tj_name"].grid(column=1,row=Row)
				Row += 1
			
			else: #情况3：正常情况
				#比较赤道仪望远镜载重决定显示颜色
				color = 'green' if self.Root_mess[root] >= TJ_mess[tj] else 'red'
				#记录望远镜的code的默认值
				self.PackageData[root]["TJ"].set(tj)
				#望远镜选择的复选框
				self.CYUI_Data[root]["tj_option"] = tk.OptionMenu(self.FrameCYlist,self.PackageData[root]["TJ"],*self.OptionDict,command=(lambda TJ,ROOT1=root: self.Update_tj_pair(TJ,ROOT1)))
				self.CYUI_Data[root]["tj_option"].configure(cursor="hand2")
				self.CYUI_Data[root]["tj_option"].grid(column=0,row=Row)
				#对应的望远镜名字，颜色按重量决定
				self.CYUI_Data[root]["tj_name"] = tk.Label(self.FrameCYlist,text=Check_Name(tj),font=('方正书宋GBK',11),justify='center',fg=color,wraplength=80)
				self.CYUI_Data[root]["tj_name"].grid(column=1,row=Row)
				Row += 1
			
			#=======第三行内容=========
			#默认所有可以使用电源的根器材都配电池
			self.PackageData[root]["DC"].set(Root_DC[root])
			#在包支持电池匹配时
			if Root_DC[root]:
				#添加复选框与结果
				self.CYUI_Data[root]["dc_option"] = tk.Checkbutton(self.FrameCYlist,text='使用电源',cursor="hand2",onvalue=True,offvalue=False,variable=self.PackageData[root]["DC"],command=(lambda ROOT2=root: self.Update_dc_use(ROOT2)))
				self.CYUI_Data[root]["dc_option"].grid(column=0,row=Row)
				self.CYUI_Data[root]["dc_result"] = tk.Label(self.FrameCYlist,text=f"YES",font=('方正书宋GBK',11),justify='center',fg="green")
				self.CYUI_Data[root]["dc_result"].grid(column=1,row=Row)
				Row += 1
			
			#=======第四行内容=========
			#占位空行
			self.CYUI_Data[root]["newline"] = tk.Label(self.FrameCYlist,text=f"           ",font=('方正书宋GBK',11),justify='center')
			self.CYUI_Data[root]["newline"].grid(column=0,row=Row)
			Row += 1
		
		#更新各种状态
		self.Check_TJ()
		self.Check_DC()
		self.UpdateScroll()

	#=====望远镜选择菜单与电源匹配复选框的两个函数=====
	def Update_tj_pair(self, TJ:str, root:str):
		"更新望远镜匹配时ui变化的函数"
		#将望远镜的code写入数据
		tj = self.OptionDict[TJ]
		self.PackageData[root]["TJ"].set(tj)
		#选择更新时，原先细检测结果作废
		self.CheckUI_updatefunction()
		#UI更新
		if tj == "Empty": 
			#画橘色占位符 ---
			self.CYUI_Data[root]["tj_name"].config(text="---", fg="orange")
		else:
			#写入器材名称并根据重量判断颜色
			self.CYUI_Data[root]["tj_name"].config(text=Check_Name(tj), fg=('green' if self.Root_mess[root] >= self.TJ_mess[tj] else 'red'))
		#器材名称变化可能会改变行数引起滚动条变化
		self.UpdateScroll()
		#更新查重
		self.Check_TJ()
		#状态设置为未进行细检查
		self.CheckUI_updatefunction()
		#聚焦左侧UI输入框
		self.LeftUI_focusfunction()

	def Update_dc_use(self, root:str):
		"按下电源复选框时的函数"
		#选择更新，原先细检测作废
		self.CheckUI_updatefunction()
		#更新是否选用电源
		use = self.PackageData[root]["DC"].get()
		if use:
			self.CYUI_Data[root]["dc_result"].config(text="YES", fg="green")
		else:
			self.CYUI_Data[root]["dc_result"].config(text="NO", fg="red")
		#检查电池与电线数目是否够
		self.Check_DC()
		#状态设置为未进行细检查
		self.CheckUI_updatefunction()
		#聚焦左侧UI输入框
		self.LeftUI_focusfunction()

	#====在UI发生变化时，UI的各种状态更新函数====
	def UpdateScroll(self):
		"更新UI与滚动条"
		self.FrameCYlist.update()
		self.scroll.config(command=self.Canvas.yview)
		self.Canvas.config(yscrollcommand=self.scroll.set,scrollregion=self.Canvas.bbox("all"))

	def Check_TJ(self) -> bool:
		"进行查重检测并更新UI状态"
		#提取出所有已匹配的望远镜
		Paired_TJ = [data["TJ"].get() for data in self.PackageData.values() if data["TJ"].get() != "Empty"]
		#判断三种情况
		if any(Paired_TJ[i] == Paired_TJ[j] for i in range(len(Paired_TJ)) for j in range(i)):
			#有两个望远镜相同，查重未通过(最高优先级)
			self.OtherCheckDatas["查重检测"].config(text='检查未通过',fg='red')
			return False
		elif len(Paired_TJ) < self.N_TJ:
			#存在未匹配的望远镜的情况
			self.OtherCheckDatas["查重检测"].config(text='有多余望远\n镜尚未匹配',justify='center',fg='orange')
		else:
			self.OtherCheckDatas["查重检测"].config(text='检查通过',fg='green')
		return True #查重通过

	def Check_DC(self):
		"进行电池与电线数目是否足够的检测并更新UI状态"
		#计算目前全部Package需要的电池数
		N_Paired_DC = sum(map(lambda data:int(data["DC"].get()), self.PackageData.values()))
		#进行UI的颜色更改
		self.OtherCheckDatas["DC"].config(fg="green" if N_Paired_DC <= self.N_DC else "red")
		self.OtherCheckDatas["DX"].config(fg="green" if N_Paired_DC <= self.N_DX else "red")

	#====数据传出====
	def GetPackageData(self)-> tuple[dict[str,str],dict[str,bool]]:
		"将望远镜匹配的数据传出"
		pairdata = {cd:self.PackageData[cd]["TJ"].get() for cd in self.PackageData}
		dcdata = {cd:self.PackageData[cd]["DC"].get() for cd in self.PackageData}
		return pairdata, dcdata

	def GetZXData(self)-> tuple[dict[str,str],dict[str,str]]:
		"返回全部杂项统计数目(前)与其颜色(后)"
		ZX_Counts:dict[str,str] = dict()
		ZX_Colors:dict[str,str] = dict()
		for zx in self.OtherCheckDatas:
			Name = self.ZXNames[zx]
			Count = self.OtherCheckDatas[zx].cget("text")
			Color = self.OtherCheckDatas[zx].cget("fg")
			ZX_Counts[Name] = Count
			ZX_Colors[Name] = Color
		ZX_Counts.pop("查重检测")
		ZX_Colors.pop("查重检测")
		return ZX_Counts, ZX_Colors
			

	#====重置该UI====
	def Reset(self):
		"重置UI到未检测器材的状态"
		#清空uI
		for tkitem in self.FrameCYlist.winfo_children():
			tkitem.destroy()
		#清空存储的数据
		self.TJ_mess.clear()
		self.Root_mess.clear()
		self.OptionDict.clear()
		self.PackageData.clear()
		self.CYUI_Data.clear()
		self.N_TJ = 0
		self.N_DC = 0
		self.N_DX = 0

		#占位置的
		tk.Label(self.FrameCYlist,text=f"           ",font=('方正书宋GBK',11),justify='center').grid(column=0,row=0)
		tk.Label(self.FrameCYlist,text=f"           ",font=('方正书宋GBK',11),justify='center').grid(column=1,row=0)
		#杂项复原
		for item in self.OtherCheckDatas:
			self.OtherCheckDatas[item].config(text="0",fg="orange")
		self.OtherCheckDatas["查重检测"].config(text="未检测",fg="orange")
		#更新滚动条
		self.UpdateScroll()





class Right_UI:
	"显示最后的器材配对"
	#==================数据的交互格式=========================
	#pk_data = [pk1,pk2...]
	#pk = {"Name":self.name, "Warn":Warn, "Lack":Lack,"Inside":Contain, "Outside":Out, "IsQZ":bool}

	#=======初始化===========
	def __init__(self,win:tk.Misc):
		self.TotalPage = 0
		self.CurrentPage = "Undefine"
		self.DisplayOutside = tk.BooleanVar(win)
		self.DisplayOutside.set(True)
		self.win = win
		self.Init_UI()
	
	def ImportFunction(self, LeftUI_focusfunction:Callable[[],None]):
		"将聚焦左侧UI输入框的函数导入"
		self.LeftUI_focusfunction = LeftUI_focusfunction

	def Init_UI(self):
		#安放最后UI的窗口
		self.FrameFinal = tk.Frame(self.win,width=200,height=400)
		self.FrameFinal.place(relx=5/6,rely=0.15,anchor='n')
		#标签
		self.label = tk.Label(self.win,text='检查报告',font=('方正书宋GBK',11),justify='center',height=1)
		self.label.place(relx=5/6,rely=0.1,anchor='n')
		#左按钮
		self.left_button = tk.Button(self.win,text='<',font=('方正书宋GBK',10),justify='center',height=1,command=self.LeftButtonFunction,cursor="hand2")
		self.left_button.place(relx=5/6-0.05,rely=0.1,anchor='ne')
		#右按钮
		self.right_button = tk.Button(self.win,text='>',font=('方正书宋GBK',10),justify='center',height=1,command=self.RightButtonFunction,cursor="hand2")
		self.right_button.place(relx=5/6+0.05,rely=0.1,anchor='nw')
		#承载器材列表与滚动条
		self.CanvasFinal = tk.Canvas(self.FrameFinal,width=184)
		self.CanvasFinal.place(relx=0,rely=0,relheight=0.9,anchor='nw')
		#器材列表所在框架
		self.FrameFinal_list = tk.Frame(self.CanvasFinal)
		self.FrameFinal_list.place(relx=0.5,rely=0.5,relheight=1,relwidth=1,anchor='center')
		#滚动条
		self.scroll = tk.Scrollbar(self.FrameFinal,orient="vertical")
		self.scroll.place(relx=1,rely=0,relheight=0.9,anchor='ne')
		self.CanvasFinal.create_window((0,0),window=self.FrameFinal_list,anchor='nw')
		self.scroll.config(command=self.CanvasFinal.yview)
		self.CanvasFinal.config(yscrollcommand=self.scroll.set,scrollregion=self.CanvasFinal.bbox("all"))
		#复选框
		self.displaybutton = tk.Checkbutton(self.FrameFinal,text='显示非散件',cursor="hand2",onvalue=True,offvalue=False,variable=self.DisplayOutside,command=self.UpdateDisplay)
		self.displaybutton.place(relx=0,rely=1,anchor='sw')

	#====左右选择按钮与复选框的功能====
	def LeftButtonFunction(self):
		"按下左按钮时UI的反应"
		if isinstance(self.CurrentPage, str):
			return
		if self.CurrentPage > 0:
			self.CurrentPage -= 1
			self.Final_UI_Update(self.CurrentPage)

	def RightButtonFunction(self):
		"按下左按钮时UI的反应"
		if isinstance(self.CurrentPage, str):
			return
		if self.CurrentPage < self.TotalPage:
			self.CurrentPage += 1
			self.Final_UI_Update(self.CurrentPage)

	def UpdateDisplay(self):
		if self.TotalPage:
			self.Final_UI_Update(self.CurrentPage)

	#====与后端的接口，传入包的信息====
	def UpdateData(self, pk_data:list[dict[str,Union[str,bool,list[str]]]]):
		"将器材包信息传入UI的函数"
		self.pk_data = pk_data
		self.TotalPage = len(pk_data)
		if self.TotalPage:
			self.CurrentPage = 0
			self.Final_UI_Update(0)
		else:
			self.Reset()

	#====构建UI的主函数====	
	def HomePage(self):
		"主页，直观展示各个组合及其是否通过"
		if self.TotalPage == 0:
			return
		#未通过统计的器材包计数
		UnPassCount = 0
		WarnCount = 0
		#页码更新
		self.label.config(text=f"检查报告1/{self.TotalPage+1}")
		#一些标题
		ResultLabel = tk.Label(self.FrameFinal_list,text="检查报告:未知",font=('方正书宋GBK',11),justify='left',fg = 'orange',wraplength=170)
		ResultLabel.grid(column=0,row=0,sticky='w')
		PassLabel = tk.Label(self.FrameFinal_list,text="通过器组数:0",font=('方正书宋GBK',11),justify='left',fg = 'black',wraplength=170)
		PassLabel.grid(column=0,row=1,sticky='w')
		UnPassLabel = tk.Label(self.FrameFinal_list,text="未通过器组数:0",font=('方正书宋GBK',11),justify='left',fg = 'black',wraplength=170)
		UnPassLabel.grid(column=0,row=2,sticky='w')
		WarnLabel = tk.Label(self.FrameFinal_list,text="警告的器组数:0",font=('方正书宋GBK',11),justify='left',fg = 'black',wraplength=170)
		WarnLabel.grid(column=0,row=3,sticky='w')
		#占位空行
		tk.Label(self.FrameFinal_list,text="",font=('方正书宋GBK',11),justify='left',wraplength=170).grid(column=0,row=4,sticky='w')
		#开始器组列表
		ListLabel = tk.Label(self.FrameFinal_list,text="器组列表:",font=('方正书宋GBK',11),justify='left',fg = 'orange',wraplength=170)
		ListLabel.grid(column=0,row=5,sticky='w')
		#显示各个器材包，统计是否通过
		Row = 6
		for index,pk in enumerate(self.pk_data,0):
			Lack:list[str] = pk["Lack"]
			Name:str = pk["Name"]
			Warn:bool = len(pk["Warn"]) or pk["TJPairWarning"]
			Color = ('red' if len(Lack) else ("orange" if Warn else 'black'))
			label = tk.Label(self.FrameFinal_list,text=Name,font=('方正书宋GBK',11),justify='left',fg = Color,wraplength=170,cursor="hand2")
			label.grid(column=0,row=Row,sticky='w')
			label.bind("<Button-1>",lambda event, x=index+1:self.GotoPage(x))
			UnPassCount += bool(len(Lack))
			WarnCount += Warn
			Row += 1
			if index < self.TotalPage-1 and self.pk_data[index]["IsQZ"] ^ self.pk_data[index+1]["IsQZ"]:
				label = tk.Label(self.FrameFinal_list,text="",font=('方正书宋GBK',11),justify='left',wraplength=170)
				label.grid(column=0,row=Row,sticky='w')
				Row += 1
		#更新通过与未通过的器组数
		PassCount = self.TotalPage-UnPassCount-WarnCount
		ResultLabel.configure(text=f"检查报告:{'未通过' if UnPassCount else '通过'}")
		ResultLabel.configure(fg=('red' if UnPassCount else 'green'))
		PassLabel.configure(text=f"通过器组数:{PassCount}")
		UnPassLabel.configure(text=f"未通过器组数:{UnPassCount}")
		WarnLabel.configure(text=f"警告的器组数:{WarnCount}")
		ListLabel.configure(fg=('red' if UnPassCount else 'green'))
		self.UpdateScroll()
		self.LeftUI_focusfunction()

	def Final_UI_Update(self, index:int):
		"按照页码更新显示部分的UI"
		#清空原来的UI
		for tkitem in self.FrameFinal_list.winfo_children():
			tkitem.destroy()
		
		if index == 0:
			self.HomePage()
			return

		pk = self.pk_data[index-1]
		Lack:list[str] = pk["Lack"]
		Warn:list[str] = pk["Warn"]
		Inside:list[str] = list(map(Check_Name,pk["Inside"]))
		Outside:list[str] = list(map(Check_Name,pk["Outside"]))
		Name:str = pk["Name"] + ("（散件）" if all([self.DisplayOutside.get(),not pk["IsQZ"],len(Inside),len(Outside)]) else "")

		#页码更新
		self.label.config(text=f"检查报告{self.CurrentPage+1}/{self.TotalPage+1}")

		#第一部分，包的名称
		NameLabel = tk.Label(self.FrameFinal_list,text=Name,font=('方正书宋GBK',11),justify='left',fg = ('orange' if len(Lack) else 'green'),wraplength=170,cursor="hand2")
		NameLabel.grid(column=0,row=0,sticky='w')
		NameLabel.bind("<Button-1>",lambda event: self.GotoPage(0))
		Row = 1
		#第二部分，缺失的需求
		if len(Lack):
			tk.Label(self.FrameFinal_list,text='',font=('方正书宋GBK',11),justify='left').grid(column=0,row=Row,sticky='w')
			Row += 1
			tk.Label(self.FrameFinal_list,text='缺乏的器材表:',font=('方正书宋GBK',11),justify='left',fg='red').grid(column=0,row=Row,sticky='w')
			Row += 1
			for lk in Lack:
				tk.Label(self.FrameFinal_list,text=lk,font=('方正书宋GBK',11),justify='left',wraplength=170).grid(column=0,row=Row,sticky='w')
				Row += 1
		#第三部分，系统提示
		if len(Warn):
			tk.Label(self.FrameFinal_list,text='',font=('方正书宋GBK',11),justify='left').grid(column=0,row=Row,sticky='w')
			Row += 1
			tk.Label(self.FrameFinal_list,text='系统提示:',font=('方正书宋GBK',11),justify='left',fg='orange').grid(column=0,row=Row,sticky='w')
			Row += 1
			for wn in Warn:
				tk.Label(self.FrameFinal_list,text=wn,font=('方正书宋GBK',11),justify='left',wraplength=170).grid(column=0,row=Row,sticky='w')
				Row += 1
		#第四部分，器材列表（散件）
		if len(Inside):
			tk.Label(self.FrameFinal_list,text='',font=('方正书宋GBK',11),justify='left').grid(column=0,row=Row,sticky='w')
			Row += 1
			tk.Label(self.FrameFinal_list,text='组合内散件表:',font=('方正书宋GBK',11),justify='left',fg = ('orange' if len(Lack) else 'green')).grid(column=0,row=Row,sticky='w')
			Row += 1
			for eq in Inside:
				tk.Label(self.FrameFinal_list,text=eq,font=('方正书宋GBK',11),justify='left',wraplength=170).grid(column=0,row=Row,sticky='w')
				Row += 1
		#第五部分，器材列表（属于QZ）
		if len(Outside) and self.DisplayOutside.get():
			tk.Label(self.FrameFinal_list,text='',font=('方正书宋GBK',11),justify='left').grid(column=0,row=Row,sticky='w')
			Row += 1
			tk.Label(self.FrameFinal_list,text='非散件器材:',font=('方正书宋GBK',11),justify='left',fg = ('orange' if len(Lack) else 'green')).grid(column=0,row=Row,sticky='w')
			Row += 1
			for eq in Outside:
				tk.Label(self.FrameFinal_list,text=eq,font=('方正书宋GBK',11),fg="silver",justify='left',wraplength=170).grid(column=0,row=Row,sticky='w')
				Row += 1
	
		#更新滑动条
		self.UpdateScroll()
		self.LeftUI_focusfunction()

	#====更新滚动条====
	def UpdateScroll(self):
		"更新UI与滚动条"
		self.FrameFinal_list.update()
		self.scroll.config(command=self.CanvasFinal.yview)
		self.CanvasFinal.config(yscrollcommand=self.scroll.set,scrollregion=self.CanvasFinal.bbox("all"))

	#===跳转到其他页的函数===
	def GotoPage(self,target:int):
		"跳转到某页"
		self.CurrentPage = target
		self.Final_UI_Update(target)

	#====重置该UI====
	def Reset(self):
		"重置该UI"
		self.TotalPage = 0
		self.CurrentPage = "Undefine"
		self.label.config(text=f"检查报告")
		for tkitem in self.FrameFinal_list.winfo_children():
			tkitem.destroy()
		self.UpdateScroll()




class CheckUI:
	"出车系统的三个控制按钮，以及各种检查的结果"
	def __init__(self,win:tk.Tk):
		#是否允许执行下一步
		self.Enable_StepTwo = False #是否允许执行细检查按钮
		self.Enable_Final = False #是否允许执行出车按钮
		self.StepOneResult = "undefine" #粗检查是否通过，缺省值为undefine
		self.StepTwoResult = "undefine"	#细检查是否通过，缺省值为undefine
		#UI初始化
		self.win = win
		self.InitUI()

	def BondButtonFunction(self, Focus:Callable[[],None], CheckTJ:Callable[[],bool], StepOneFunction:Callable[[],None], StepTwoFunction:Callable[[],bool], Final_Confirm:Callable[[],bool], LastStep:Callable[[],None]):
		"将三个按钮绑定四个函数"
		#带执行条件判定的细检查与出车按钮函数
		self.Focus = Focus
		self.CheckTJ = CheckTJ
		judged_steptwo = lambda f2=StepTwoFunction: self.StepTwoFunction_Judged(f2)
		judged_finalstep = lambda f1=Final_Confirm,f2=LastStep: self.StepFinalFunction_Judged(f1,f2)
		auto_stepone = lambda f1=StepOneFunction,f2=judged_steptwo: self.AutoStepOneFunction(f1,f2)
		#按钮绑定
		self.StepOneButton.config(command=auto_stepone)
		self.StepTwoButton.config(command=judged_steptwo)
		self.FinalButton.config(command=judged_finalstep)
	
	#=====UI的初始化=====
	def InitUI(self):
		"初始化三个按钮"
		#第一步粗检查的按钮与标签
		self.StepOneButton = tk.Button(self.win,text='粗略检查',font=('方正书宋GBK',13),justify='center',cursor="hand2")
		self.StepOneButton.place(relx=0.16,rely=0.87,anchor='n')
		self.StepOneResultUI = tk.Label(self.win,text='尚未检查',font=('方正书宋GBK',11),justify='center',fg='orange')
		self.StepOneResultUI.place(relx=0.16,rely=0.92,anchor='n')
		#第二步细检查的按钮与标签
		self.StepTwoButton = tk.Button(self.win,text='严格检查',font=('方正书宋GBK',13),justify='center',cursor="hand2")
		self.StepTwoButton.place(relx=0.5,rely=0.87,anchor='n')
		self.StepTwoResultUI = tk.Label(self.win,text='尚未检查',font=('方正书宋GBK',11),justify='center',fg='orange')
		self.StepTwoResultUI.place(relx=0.5,rely=0.92,anchor='n')
		#UI后出车的按钮
		self.FinalButton = tk.Button(self.win,text='生成档案',font=('方正书宋GBK',18),justify='center',cursor="hand2")
		self.FinalButton.place(relx=5/6,rely=0.8,anchor='n')

	#在左侧中侧的UI改变时执行的函数
	def ResetFirstResult(self):
		"系统粗检查与细检查结果均作废"
		self.Enable_StepTwo = False
		self.Enable_Final = False
		self.StepOneResult = "undefine"
		self.StepTwoResult = "undefine"
		self.StepOneResultUI.config(text='尚未检查', fg='orange')
		self.StepTwoResultUI.config(text='尚未检查', fg='orange')
	
	def ResetSecondResult(self):
		"细检查结果作废"
		self.Enable_Final = False
		self.StepTwoResult = "undefine"
		self.StepTwoResultUI.config(text='尚未检查', fg='orange')

	#粗检查与细检查得到结果后的更新函数
	def FirstStep(self,result:bool):
		"粗检查得到结果后更新"
		self.ResetSecondResult()
		self.Enable_StepTwo = True
		self.StepOneResult = result
		if result:
			self.StepOneResultUI.config(text='检查通过',fg='green')
		else:
			self.StepOneResultUI.config(text='检查未通过',fg='red')
	
	def SecondStep(self,result:bool):
		"细检查得到结果后更新"
		self.Enable_Final = True
		self.StepTwoResult = result
		if result:
			self.StepTwoResultUI.config(text='检查通过',fg='green')
		else:
			self.StepTwoResultUI.config(text='检查未通过',fg='red')

	#带执行条件判定的细检查函数与最终检查函数
	def AutoStepOneFunction(self,step_one:Callable,step_two:Callable):
		"在设置允许的情况下，在第一步通过时自动进行第二步"
		step_one()
		if Config.AutoCheckStepTwo and self.Enable_StepTwo and self.StepOneResult:
			self.StepTwoFunction_Judged(step_two)

	def StepTwoFunction_Judged(self,step_two:Callable):
		"带执行条件判定的细检查函数"
		if not self.Enable_StepTwo:
			messagebox.showwarning("系统提示","请先完成粗略检查！")
			self.Focus()
		elif not self.CheckTJ():
			messagebox.showwarning("系统提示","望远镜查重检测未通过！")
			self.Focus()
		else:
			step_two()

	def StepFinalFunction_Judged(self,final_confirm:Callable,last_step:Callable):
		"带执行条件判定的最终检查函数"
		if not self.Enable_Final:
			messagebox.showwarning("系统提示","请先完成严格检查！")
			self.Focus()
		elif final_confirm():
			last_step()
		else:
			self.Focus()








#=======================================占位函数，在弹出窗口点击叉号时跳过====================================
def NO_QUIT():
	"让关闭按钮无作用的占位函数"
	pass

def _quit(win:tk.Toplevel, var:Union[tk.StringVar,tk.BooleanVar], newvar:Union[str,bool]):
	"真正结束窗口时的操作"
	win.quit()
	win.destroy()
	var.set(newvar)
	change_language("EN")



#=======================================各种弹出窗口====================================
def Pop_NewQZInputWindow(root:tk.Misc) -> str:
	"弹出输入新器组的窗口"
	win_newqz = tk.Toplevel(root)
	#隐藏最小化最大化按钮
	win_newqz.transient(root)
	#窗口的大小标题和图标
	win_newqz.geometry("320x100+200+200")
	win_newqz.title("自定义器组")
	win_newqz.iconphoto(False,tk.PhotoImage(file="./Resource/icon.png"))
	#标签与输入框
	tk.Label(win_newqz,text='请输入器组名称',font=('方正书宋GBK',11),justify='left').pack()
	NewQZName = tk.Entry(win_newqz,show=None,font=('Arial Unicode MS',11),width=14)
	NewQZName.pack()
	#储存新器组名称的结果
	qzname = tk.StringVar(win_newqz)
	
	#响应按下回车
	def GetEvent(event:tk.Event,VAR:tk.Entry):
		"响应回车键"
		if event.keycode == 13 and len(VAR.get()):
			_quit(win_newqz,qzname,VAR.get())
	#按叉号退出程序
	win_newqz.protocol('WM_DELETE_WINDOW', lambda: _quit(win_newqz,qzname,""))
	#按下回车
	NewQZName.bind('<Key>',lambda event,var=NewQZName:GetEvent(event,var))
	#聚焦窗口,程序进入主循环，直到窗口被摧毁然后退出并返回相应数值
	win_newqz.focus_force()
	NewQZName.focus_set()
	change_language("ZH")
	win_newqz.mainloop()
	return qzname.get()

def Pop_StepOneCYWarningWindow(root:tk.Misc,N_CY:int) -> bool:
	"若望远镜与支架数目不匹配，则弹出该窗口"
	#若望远镜与支架数目相等，则跳过整个函数。函数返回False代表继续出车，True为重新检查
	if N_CY == 0:
		return False
	#构建窗口，设置图标标题与窗口大小，覆写叉号按钮
	win_stop = tk.Toplevel(root)
	#隐藏最小化最大化按钮
	win_stop.transient(root)
	#窗口的大小标题和图标
	win_stop.geometry("320x320+500+200")
	win_stop.title("警告！望远镜与支架数目不等！")
	win_stop.iconphoto(False,tk.PhotoImage(file="./Resource/icon.png"))
	win_stop.protocol('WM_DELETE_WINDOW', NO_QUIT)
	#窗口的内容

	#安放警告标题与会徽的框架
	Frametitle = tk.Frame(win_stop)
	Frametitle.pack(pady=10)
	#强制出车的标题
	tk.Label(Frametitle,text='Warning',font=('timesnewrom',25,"bold"),justify='left',fg='red2').pack(side=tk.RIGHT)
	#会徽
	YAS_logo = ImageTk.PhotoImage(Image.open("./Resource/YAS.png").resize((45,45)))
	Logo = tk.Label(Frametitle, image=YAS_logo,width=40,height=40)
	Logo.pack(side=tk.LEFT)

	tk.Label(win_stop,text="望远镜与赤道仪数目不等",font=('方正书宋GBK',17),justify='left').pack(pady=3)
	tk.Label(win_stop,text=(f'望远镜多出{-N_CY}个' if N_CY < 0 else f'望远镜支架多出{N_CY}个'), font=('方正书宋GBK',17),justify='left').pack(pady=3)
	tk.Label(win_stop,text="是否要继续出车吗？",font=('方正书宋GBK',17),justify='left').pack(pady=3)
	#继续出车还是重新检查的选择，Stop为False代表继续出车，True为重新检查
	Stop = tk.BooleanVar(win_stop)
	Stop.set(True)
	tk.Button(win_stop,text='重新检查',font=('方正书宋GBK',17),justify='center',cursor="hand2",command=(lambda: _quit(win_stop,Stop,True))).pack(pady=10)
	tk.Button(win_stop,text='继续出车',font=('方正书宋GBK',17),justify='center',cursor="hand2",command=(lambda: _quit(win_stop,Stop,False))).pack(pady=5)
	#聚焦窗口,程序进入主循环，直到窗口被摧毁然后退出并返回相应数值
	win_stop.focus_force()
	change_language("EN")
	win_stop.mainloop()
	return Stop.get()

def Pop_StepOneWarningWindow(root:tk.Misc,Counter:dict[str,int]) -> bool:
	"在粗查时有需求未满足，缺乏普通器材弹出窗口"

	#赤道仪与望远镜的情况之前的窗口已经统计了，故不用考虑
	Counter.pop("CY")
	#若全部需求均已满足，则跳过整个函数。函数返回False代表继续出车，True为重新检查
	if min(Counter.values()) >= 0:
		return False
		
	#构建窗口，设置图标标题与窗口大小，覆写叉号按钮
	win_stepone = tk.Toplevel(root)
	#隐藏最小化最大化按钮
	win_stepone.transient(root)
	#窗口的大小标题和图标
	win_stepone.geometry("360x500+500+200")
	win_stepone.title("发车未通过")
	win_stepone.iconphoto(False,tk.PhotoImage(file="./Resource/icon.png"))
	win_stepone.protocol('WM_DELETE_WINDOW', NO_QUIT)

	#安放标题与会徽的框架
	Frametitle = tk.Frame(win_stepone)
	Frametitle.pack(pady=10)
	#强制出车的标题
	tk.Label(Frametitle,text='检查未通过!',font=('华文魏碑',25,'bold'),justify='left',fg='red2').pack(side=tk.RIGHT)
	#会徽
	YAS_logo = ImageTk.PhotoImage(Image.open("./Resource/YAS.png").resize((45,45)))
	Logo = tk.Label(Frametitle, image=YAS_logo,width=40,height=40)
	Logo.pack(side=tk.LEFT)

	#窗口的标题
	tk.Label(win_stepone,text='缺少器材',font=('华文魏碑',17),justify='left').pack(pady=3)

	#构建窗口Canvas与滚动条
	Canvas_stop = tk.Canvas(win_stepone,width=200,height=350)
	Canvas_stop.pack(side=tk.TOP)
	Frame_stop = tk.Frame(Canvas_stop,width=200,height=350)
	Frame_stop.pack(side=tk.TOP)
	sc = tk.Scrollbar(Frame_stop,orient="vertical")
	sc.pack(side=tk.RIGHT,fill=tk.Y)
	#显示各种需求的缺少量的窗口
	Lackbox = tk.Listbox(Frame_stop, selectmode='single',yscrollcommand=sc.set,height=17)
	Lackbox.pack(side=tk.LEFT,fill=tk.BOTH)
	#添加各种需求
	for ness in Counter:
		Lackbox.insert(tk.END,f'{Check_NessName(ness)}: {Counter[ness]}') if Counter[ness] < 0 else None
	
	#继续出车还是重新检查的选择，Stop为False代表继续出车，True为重新检查
	Stop = tk.BooleanVar(win_stepone)
	Stop.set(True)
	tk.Button(win_stepone,text='重新检查',font=('方正书宋GBK',13),justify='center',cursor="hand2",command=(lambda: _quit(win_stepone,Stop,True))).pack(pady=3)
	tk.Button(win_stepone,text='继续出车',font=('方正书宋GBK',13),justify='center',cursor="hand2",command=(lambda: _quit(win_stepone,Stop,False))).pack(pady=3)
	#更新滚动条并聚焦窗口
	sc.config(command=Lackbox.yview)
	win_stepone.focus_force()
	#程序进入主循环，直到窗口被摧毁然后退出并返回相应数值
	change_language("EN")
	win_stepone.mainloop()
	return Stop.get()

def Pop_StepTwoPPMessInputWindow(root:tk.Misc,Package_name_list:list[str], Package_defaultmess_list:list[int]) -> tuple[bool,list[int]]:
	"输入赤道仪需要的重锤质量信息"
	#构建窗口
	win_nessPPmess = tk.Toplevel(root)
	#隐藏最小化最大化按钮
	win_nessPPmess.transient(root)
	#窗口的大小标题和图标
	win_nessPPmess.geometry("380x520+500+200")
	win_nessPPmess.title("重锤质量需求的录入")
	win_nessPPmess.iconphoto(False,tk.PhotoImage(file="./Resource/icon.png"))
	win_nessPPmess.protocol('WM_DELETE_WINDOW', NO_QUIT)

	#安放警告标题与会徽的框架
	Frametitle = tk.Frame(win_nessPPmess)
	Frametitle.pack(pady=10)
	#强制出车的标题
	tk.Label(Frametitle,text='请录入重锤质量',font=('华文魏碑',25,"bold"),justify='center',fg='blue4',wraplength=320).pack(side=tk.RIGHT)
	#会徽
	YAS_logo = ImageTk.PhotoImage(Image.open("./Resource/YAS.png").resize((45,45)))
	Logo = tk.Label(Frametitle, image=YAS_logo,width=40,height=40)
	Logo.pack(side=tk.LEFT)

	#Label
	tk.Label(win_nessPPmess,text='请输入重锤的质量(单位:Kg)',font=('华文魏碑',13),justify='center').pack(pady=1)
	#构建承载输入重锤的Frame
	FramePP = tk.Frame(win_nessPPmess,width=220,height=300)
	FramePP.pack(pady=10)
	CanvasPP = tk.Canvas(FramePP,width=184)
	CanvasPP.place(relx=0,rely=0.5,relheight=1,anchor='w')
	FramePPlist = tk.Frame(CanvasPP)
	FramePPlist.place(relx=0.5,rely=0.5,relheight=1,relwidth=1,anchor='center')
	#构造滚动条
	scroll = tk.Scrollbar(FramePP,orient="vertical")
	scroll.place(relx=1,rely=0.5,relheight=1,anchor='e')
	CanvasPP.create_window((0,0),window=FramePPlist,anchor='nw')
	#绑定滚动条
	scroll.config(command=CanvasPP.yview)
	CanvasPP.config(yscrollcommand=scroll.set,scrollregion=CanvasPP.bbox("all"))
	tk.Label(FramePPlist,text=f"           ",font=('方正书宋GBK',13),justify='center').grid(column=0,row=0)
	tk.Label(FramePPlist,text=f"           ",font=('方正书宋GBK',13),justify='center').grid(column=1,row=0)

	#=============================================================
	#录入每个包需要重锤质量的UI
	#与之前的UI类似，每个包有三行。
	#第一行显示包的名称
	#第二行录入其需要的重锤质量
	#第三为空行，分隔两个器材包
	#【目前缺陷：无法构造只能输入数字的输入方式而只能靠判断！！！】
	#==============================================================

	#录入每个包的信息
	NessPPmess_List = []
	for index, name in enumerate(Package_name_list,0):
		#构建变量存储每个package的重锤需求量，并将默认值赋予它
		pk_nessppmess = tk.StringVar(win_nessPPmess)
		pk_nessppmess.set(str(Package_defaultmess_list[index]))
		NessPPmess_List.append(pk_nessppmess)
		#开始构造UI,第一行显示包的名称
		tk.Label(FramePPlist,text="包的名称:",font=('方正书宋GBK',12),justify='center').grid(column=0,row=3*index)
		tk.Label(FramePPlist,text=name, font=('方正书宋GBK',12),justify='center',wraplength=80).grid(column=1,row=3*index)
		#第二行录入其需要的重锤质量
		tk.Label(FramePPlist,text="重锤质量:",font=('方正书宋GBK',12),justify='center').grid(column=0,row=3*index+1)
		tk.Entry(FramePPlist,textvariable=pk_nessppmess,show=None,font=('Arial Unicode MS',12),width=6).grid(column=1,row=3*index+1)
		#第三行为空行，分隔两个器材包
		tk.Label(FramePPlist,text=f"           ",font=('方正书宋GBK',12),justify='center').grid(column=0,row=3*index+2)
	
	#更新滚动条
	FramePPlist.update()
	scroll.config(command=CanvasPP.yview)
	CanvasPP.config(yscrollcommand=scroll.set,scrollregion=CanvasPP.bbox("all"))

	#返回时程序的行为
	def __quit(NessPPmess_List,win:tk.Toplevel, var:tk.BooleanVar, newvar:bool):
		"在原先_quit的基础上加上输入检测功能"
		if not (newvar or all(map(lambda x:x.get().isdigit(), NessPPmess_List))):
			messagebox.showwarning("系统提示","赤道仪质量请输入自然数！")
			win_nessPPmess.focus()
			return
		else:
			_quit(win,var,newvar)
		
	#用该变量追踪窗口关闭后的状态
	Check_Stop = tk.BooleanVar(win_nessPPmess)
	Check_Stop.set(True)
	tk.Button(win_nessPPmess,text='退出检查',font=('方正书宋GBK',13),justify='center',cursor="hand2",command=(lambda: __quit(NessPPmess_List,win_nessPPmess,Check_Stop,True))).pack(pady=3)
	tk.Button(win_nessPPmess,text='继续出车',font=('方正书宋GBK',13),justify='center',cursor="hand2",command=(lambda: __quit(NessPPmess_List,win_nessPPmess,Check_Stop,False))).pack(pady=3)
		
	#窗口的主循环
	change_language("EN")
	win_nessPPmess.focus_force()
	win_nessPPmess.mainloop()

	#返回判断结果与数据
	return Check_Stop.get(), list(map(lambda x:x.get(), NessPPmess_List))

def Pop_FinalConfirmWindow(root:tk.Misc,pk_data:list[dict[str,Union[str,bool,list[str]]]]):
	"强制出车的弹出窗口"

	def check():
		"检查输入的光速是否正确"
		if Code.get() == '299792458':
			_quit(win_confirm, StopVar, True)
	
	def InputEnter(event:tk.Event):
		"按下回车时响应该函数"
		if event.keycode == 13:
			check()
	

	#窗口
	win_confirm = tk.Toplevel(root)
	#隐藏最小化最大化按钮
	win_confirm.transient(root)
	#窗口的标题和图标
	win_confirm.geometry("380x470+500+200")
	win_confirm.title("强制出车确定")
	win_confirm.iconphoto(False,tk.PhotoImage(file="./Resource/icon.png"))
	win_confirm.protocol('WM_DELETE_WINDOW', (lambda: _quit(win_confirm,StopVar,False)))
	
	#返回函数结果的变量
	StopVar = tk.BooleanVar(win_confirm)
	StopVar.set(False)

	#安放强制出车标题与会徽的框架
	Frametitle = tk.Frame(win_confirm)
	Frametitle.pack(pady=10)
	#强制出车的标题
	Title = tk.Label(Frametitle,text='是否强制出车？',font=('华文魏碑',25,"bold"),justify='left',fg='red2')
	Title.pack(side=tk.RIGHT)
	#会徽
	YAS_logo = ImageTk.PhotoImage(Image.open("./Resource/YAS.png").resize((45,45)))
	Logo = tk.Label(Frametitle, image=YAS_logo,width=40,height=40)
	Logo.pack(side=tk.LEFT)


	tk.Label(win_confirm,text='缺少器材的组合',font=('华文魏碑',16,"bold"),justify='left',fg='blue4').pack(pady=3)

	#需求画布
	Canvas_confrim = tk.Canvas(win_confirm,width=200,height=350)
	Canvas_confrim.pack(side=tk.TOP)
	Frame_stop = tk.Frame(Canvas_confrim,width=200,height=350)
	Frame_stop.pack(side=tk.TOP)
	scroll = tk.Scrollbar(Frame_stop,orient="vertical")
	scroll.pack(side=tk.RIGHT,fill=tk.Y)


	#配置树的样式
	style = ttk.Style()
	style.configure('Treeview',font=(None,10),borderwidth=0)
	#需求显示
	Lacktree = ttk.Treeview(Frame_stop,show="tree",selectmode="browse",height=13,yscrollcommand=scroll.set,columns = ['text'])
	Lacktree.pack(side=tk.LEFT,fill=tk.BOTH)
	Lacktree.column("#0", width=20, minwidth=20)
	Lacktree.column("text",width=130, minwidth=130)
	Lacktree.tag_configure("InPK",foreground="red2")
	Lacktree.tag_configure("PK",foreground="black")
	FakeCode = 0
	for pk in pk_data:
		lk_list = pk["Lack"] + ([pk["TJPairWarning"]] if pk["TJPairWarning"] else [])
		if not len(lk_list):
			continue
		FakeCode += 1
		Lacktree.insert("",tk.END,iid=f"PK{FakeCode}",text='',value=[pk["Name"]+":"],tags="PK",open=True)
		for index,lk in enumerate(lk_list):
			Lacktree.insert(f"PK{FakeCode}",tk.END,iid=f"PK{FakeCode}NUM{index}",text='',value=[lk],tags="InPK")
	scroll.config(command=Lacktree.yview)

	#执行码检验
	tk.Label(win_confirm,text='请输入光速进行验证:').place(relx=0.45,rely=0.8,anchor='center')
	Code = tk.Entry(win_confirm,show=None,font=('Arial Unicode MS',11),width=15)
	Code.place(relx=0.45,rely=0.85,anchor='center')
	Code.bind('<Key>',InputEnter)
	Code.focus_force()
	
	tk.Button(win_confirm,text='强制出车',font=('方正书宋GBK',11),justify='center',cursor="hand2",command=check).place(relx=0.72,rely=0.85,anchor='center')
	tk.Button(win_confirm,text='返回',font=('方正书宋GBK',13),justify='center',cursor="hand2",command=lambda: _quit(win_confirm,StopVar,False)).place(rely=0.9,relx=0.45,anchor='n')
	change_language("EN")
	win_confirm.mainloop()
	return StopVar.get()

def Pop_LastStepWindow(root:tk.Misc,Warn_Data:dict[str,list[str]], ZX_Counts:dict[str,str], ZX_Colors:dict[str,str], Push_Data:dict[str,str],PK_Data:dict[str,dict[str,Union[bool,str,list[str]]]],UpdatePushData_Function:Callable[[dict[str,StopIteration]],None]):
	"最后的确认窗口"
	def Pop_Boxmenu(event:tk.Event):
		"弹出菜单"
		code = WarningTree.selection()
		if not len(code):
			return
		code = code[0]
		parent = WarningTree.parent(code)
		TrueCode = parent if len(parent) else code
		boxmenu.entryconfig(0,label=Check_Name(TrueCode))
		boxmenu.post(event.x_root, event.y_root)
	
	def default_location(option:str):
		"更新活动类型的默认地点"
		LOCATIONS = {"例观":"静园草坪","外出":"吕营","展示":"百讲门口","借出":"","其他":""}
		AC_var.set("活动")
		act.delete("0","end")
		act.insert(0, ("" if option =="其他" else option))
		Place.delete("0","end")
		Place.insert(0,LOCATIONS[option])
		UseAppendix.set(option=="外出")

	def set_location(option:str):
		"更新活动地点"
		PL_var.set("地点")
		Place.delete("0","end")
		Place.insert(0,option)

	def get_PushData()-> dict[str,str]:
		"给出当前各输入框的数值"
		Push_Data:dict[str,str] = dict()
		Push_Data["type"] = act.get()
		Push_Data["time"] = A_Time.get()
		Push_Data["place"] = Place.get()
		Push_Data["person"] = Person.get()
		Push_Data["notes"] = Notes.get('1.0',tk.END)
		UpdatePushData_Function(Push_Data)
		return Push_Data

	def GenerateLogDoc(pkdata:dict[str,dict[str,Union[bool,str,list[str]]]]):
		if not HaveBeenChecked.get():
			return
		pushdata = get_PushData()
		Log = WriteLog(pkdata, pushdata)
		file_root, file_dir, file_name = gen_docx(Log,UseAppendix.get())
		CompileDoc(file_root, file_dir, file_name)
	
	def Quit():
		get_PushData()
		win_f.quit()
		win_f.destroy()
		change_language("EN")

	#窗口
	win_f = tk.Toplevel(root)
	#隐藏最小化最大化按钮
	win_f.transient(root)
	#窗口的大小标题和图标
	win_f.geometry("500x530+300+200")
	win_f.title("生成出车档案")
	win_f.iconphoto(False,tk.PhotoImage(file="./Resource/icon.png"))
	#关闭按钮
	win_f.protocol('WM_DELETE_WINDOW', Quit)


	#安放标题与会徽的框架
	Frametitle = tk.Frame(win_f)
	Frametitle.place(relx=0.5,rely=0,anchor='n')
	#强制出车的标题
	Title = tk.Label(Frametitle,text='生成出车档案',font=('华文魏碑',25),justify='center',fg="blue4")
	Title.pack(side=tk.RIGHT)
	#会徽
	YAS_logo = ImageTk.PhotoImage(Image.open("./Resource/YAS.png").resize((45,45)))
	Logo = tk.Label(Frametitle, image=YAS_logo,width=40,height=40)
	Logo.pack(side=tk.LEFT)

	#左右分区画布
	FrameLeft = tk.Frame(win_f,width=200)
	FrameLeft.place(relx=0.27,rely=0.1,relheight=0.85,anchor='n')

	CanvasRight = tk.Canvas(win_f,width=170)
	CanvasRight.place(relx=3/4,rely=0.1,relheight=0.6,anchor='n')
	FrameRight = tk.Frame(CanvasRight)
	FrameRight.place(relx=0.5,rely=0.5,relheight=1,relwidth=1,anchor='center')

	FrameOtherFinal = tk.Frame(win_f,width=180)
	FrameOtherFinal.place(relx=3/4,rely=0.75,relheight=0.3,anchor='n')

	#左半边
	tk.Label(FrameLeft,text='活动类型:',font=('方正书宋GBK',12)).grid(column=0,row=0,sticky='w',pady=3)
	act_frame = tk.Frame(FrameLeft,height=12)
	act_frame.grid(column=0,row=1,sticky='w',pady=1)

	#活动类型，默认为例观，其选择会影响地点的默认值
	OPTIONS = ["例观","外出","展示","借出","其他"]
	AC_var = tk.StringVar(win_f)
	AC_var.set("活动")
	AC_TypeOption = tk.OptionMenu(act_frame,AC_var,*OPTIONS,command=default_location)
	AC_TypeOption.configure(width=4,height=1,cursor="hand2")
	AC_TypeOption.pack(side='left',fill=tk.X)
	act = tk.Entry(act_frame,show=None,font=('Arial Unicode MS',12),width=13)
	act.insert(0,Push_Data["type"])
	act.pack(side='left')

	#活动时间，默认为当前系统时间
	tk.Label(FrameLeft,text='活动时间:',font=('方正书宋GBK',12)).grid(column=0,row=2,sticky='w',pady=3)
	A_Time = tk.Entry(FrameLeft,show=None,font=('Arial Unicode MS',12),width=22)
	A_Time.insert(0,"%d年%d月%d日%d点%d分"%time.localtime(time.time())[:5])
	A_Time.grid(column=0,row=3,sticky='w',pady=1)


	#活动地点
	tk.Label(FrameLeft,text='活动地点:',font=('方正书宋GBK',12)).grid(column=0,row=4,sticky='w',pady=3)
	LOC_OPTIONS = ["静园草坪","蹊径坪","理二门口","明安图","乌兰哈达","吕营","百讲门口","物理学院","石舫","理一楼顶","华海田园","花台","孙栅子村","脑木更苏木","巴彦淖尔"]
	PL_var = tk.StringVar(win_f)
	PL_var.set("地点")
	place_frame = tk.Frame(FrameLeft,height=12)
	place_frame.grid(column=0,row=5,sticky='w',pady=1)
	PlaceOption = tk.OptionMenu(place_frame,PL_var,*LOC_OPTIONS,command=set_location)
	PlaceOption.configure(width=4,height=1,cursor="hand2")
	PlaceOption.pack(side='left',fill=tk.X)
	Place = tk.Entry(place_frame,show=None,font=('Arial Unicode MS',12),width=13)
	Place.insert(0,Push_Data["place"])
	Place.pack(side='left')

	#活动负责人
	tk.Label(FrameLeft,text='活动负责人:',font=('方正书宋GBK',12)).grid(column=0,row=6,sticky='w',pady=3)
	Person = tk.Entry(FrameLeft,show=None,font=('Arial Unicode MS',12),width=22)
	Person.insert(0,Push_Data["person"])
	Person.grid(column=0,row=7,sticky='w',pady=1)

	#备注
	tk.Label(FrameLeft,text='备注:',font=('方正书宋GBK',12)).grid(column=0,row=8,sticky='w',pady=3)
	Notes = tk.Text(FrameLeft,font=('方正书宋GBK',12),wrap='char',width=22,height=5)
	Notes.insert("1.0",Push_Data["notes"])
	Notes.grid(column=0,row=9,sticky='w',pady=1)

	#外出器材观测表
	UseAppendix = tk.BooleanVar(win_f)
	UseAppendix.set(False)
	tk.Checkbutton(FrameLeft,text='使用外观器材登记表',cursor="hand2",font=('方正书宋GBK',12),onvalue=True,offvalue=False,variable=UseAppendix).grid(column=0,row=10,sticky='w')

	#最后的复选框
	HaveBeenChecked = tk.BooleanVar(win_f)
	HaveBeenChecked.set(False)
	tk.Checkbutton(FrameLeft,text='本人已认真检查',cursor="hand2",font=('方正书宋GBK',12),onvalue=True,offvalue=False,variable=HaveBeenChecked).grid(column=0,row=11,sticky='w',pady=5)
	
	#生成档案按钮
	tk.Button(FrameLeft,text='生成出车档案',font=('方正书宋GBK',13),cursor="hand2",command=lambda :GenerateLogDoc(PK_Data)).grid(column=0,row=12,pady=5)



	#右半区

	tk.Label(FrameRight,text='Warnings:',font=('timesnewrom',12),justify='left').pack(side=tk.TOP)

	scroll = tk.Scrollbar(FrameRight,orient="vertical")
	scroll.pack(side=tk.RIGHT,fill=tk.BOTH)

	#配置树的样式
	style = ttk.Style()
	style.configure('Treeview',font=(None,10),borderwidth=0)
	#警告的树
	WarningTree = ttk.Treeview(FrameRight,show="tree",selectmode="browse",height=17,yscrollcommand=scroll.set,columns = ['text'])
	WarningTree.pack(side=tk.LEFT,fill=tk.BOTH)
	WarningTree.column("#0", width=20, minwidth=20)
	WarningTree.column("text",width=135, minwidth=135)
	WarningTree.tag_configure("Leaf",foreground="red2")
	WarningTree.tag_configure("Root",foreground="black")


	#警告更新
	for code in Warn_Data:
		WarningTree.insert("",tk.END,iid=code,text='',value=[code+":"],tags="Root",open=True)
		for index,warn in enumerate(Warn_Data[code]):
			WarningTree.insert(code,tk.END,iid=f"{code}+:+{index}",text='',value=warn,tags="Leaf")
	
	scroll.config(command=WarningTree.yview)

	#下拉菜单
	boxmenu = tk.Menu(win_f, tearoff=0)
	boxmenu.add_command(label="")
	WarningTree.bind("<Button-3>", Pop_Boxmenu)

	
	tk.Label(FrameOtherFinal,text='器材统计:',font=('方正书宋GBK',12)).grid(column=0,row=0,sticky='w')
	tk.Label(FrameOtherFinal,text='  ',font=('方正书宋GBK',12)).grid(column=1,row=0,sticky='w')
	for row,zx in enumerate(ZX_Counts,1):
		tk.Label(FrameOtherFinal,text=f'{zx}: {ZX_Counts[zx]}',fg =ZX_Colors[zx],font=('方正书宋GBK',12)).grid(column=2*(row%2),row=row//2,sticky='w')
	win_f.focus_force()
	change_language("ZH")
	win_f.mainloop()



if __name__ == "__main__":
	UI =  UI_alpha()
	UI.BondButtonFunction(lambda x:None, lambda:{"type":"例观", "place":"静园草坪","person":"", "notes":""},Foo,Foo,Foo,Foo)
	UI.mainloop()