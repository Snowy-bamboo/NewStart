import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk

import time

from DataReader import AllEquipmentList,AllQZDict,AllTypenameList, SortedAllEquipmentList
from DataReader import Check_Enable, Check_Name, Check_QZInside, Check_Classify
from DataReader import ReadLog

from ConfigReader import Config
from UI_config import FullPopupConfig

from ChangeLanguage import change_language

from Doc_beta import gen_docx,CompileDoc


#多导一个库，用于type hint（数据类型注释）
from typing import Union, Callable

class UI_beta:
	"收车系统的全部UI"
	def __init__(self) -> None:
		#储存器材分组的信息
		self.pkdata:list[dict[str,Union[str,list[str]]]] = list()
		#初始化UI
		self.win = tk.Tk()
		self.win.transient()
		self.Init_win()
		self.left_ui = Left_UI(self.win)
		self.left_ui.LoadButton.config(command=self.LoadData)
		self.right_ui = Right_UI(self.win)
		self.right_ui.Button.configure(command=self.GenerateTex)
		self.Init_Menu()
		
	
	def Init_win(self):
		"以win为基础构造主窗口的主要部件"
		#窗口长宽与弹出位置
		self.win.geometry("500x570+500+150")
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
		self.logoimag = ImageTk.PhotoImage(Image.open("./Resource/YAS.png").resize((45,45)))
		self.Logo = tk.Label(self.Frametitle, image=self.logoimag,width=40,height=40)
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
		self.filemenu.add_command(label="导入记录",command=lambda:[self.left_ui.GetPath(),self.LoadData()],accelerator="Ctrl+O")
		self.win.bind("<Control-o>",lambda event:[self.left_ui.GetPath(),self.LoadData()])
		self.win.bind("<Control-O>",lambda event:[self.left_ui.GetPath(),self.LoadData()])
		self.filemenu.add_command(label="生成档案",command=self.GenerateTex,accelerator="Ctrl+P")
		self.win.bind("<Control-p>",lambda event:self.GenerateTex())
		self.win.bind("<Control-P>",lambda event:self.GenerateTex())
		self.filemenu.add_separator()
		self.filemenu.add_command(label="退出",command=self.QUIT,accelerator="Alt+F4")
	
		#编辑部分
		self.editmenu = tk.Menu(self.Menu,tearoff=0)
		self.editmenu.add_cascade(label="选择器材",menu=self.left_ui.ChoiceBoxmenuMain)
		self.editmenu.add_command(label="撤销",command=self.left_ui.Undo,accelerator="Ctrl+Z")
		self.win.bind("<Control-z>",lambda event:self.left_ui.Undo())
		self.win.bind("<Control-Z>",lambda event:self.left_ui.Undo())
		self.editmenu.add_command(label="恢复",command=self.left_ui.Redo,accelerator="Ctrl+Y")
		self.win.bind("<Control-y>",lambda event:self.left_ui.Redo())
		self.win.bind("<Control-Y>",lambda event:self.left_ui.Redo())

		#设置部分
		self.setmenu = tk.Menu(self.Menu,tearoff=0)
		self.setmenu.add_command(label="设置",command=lambda: [self.ConfigFunction(),self.left_ui.Focus()],accelerator="F9")
		self.win.bind("<F9>",lambda event: [self.ConfigFunction(),self.left_ui.Focus()])
		#帮助部分
		self.helpmenu = tk.Menu(self.Menu,tearoff=0)
		self.helpmenu.add_command(label="帮助",command=lambda:messagebox.showwarning("才不是作者懒得写文档","赶紧去培训，\n不会出车的东西！"),accelerator="F10")
		self.win.bind("<F10>",lambda event:messagebox.showwarning("才不是作者懒得写文档","赶紧去培训，\n不会出车的东西！"))
		self.helpmenu.add_separator()
		self.helpmenu.add_command(label="关于",command=lambda:messagebox.showinfo("关于系统",
			f"版本: v{Config.Version}\n作者: The Wolf-Rayet\n不要用出车系统2.0的存档做测试，会弹窗"))
		#整合菜单
		self.Menu.add_cascade(label="文件",menu=self.filemenu)
		self.Menu.add_cascade(label="编辑",menu=self.editmenu)
		self.Menu.add_cascade(label="设置 ",menu=self.setmenu)
		self.Menu.add_cascade(label="帮助",menu=self.helpmenu)

	def ConfigFunction(self):
		"按下设置键执行的函数"
		FullPopupConfig(self.win,Config)
		self.left_ui.Init_Choice_BoxMenu()
		self.editmenu.entryconfigure(0,menu=self.left_ui.ChoiceBoxmenuMain)


	def LoadData(self):
		"导入出车记录"
		#获取文件路径
		path = self.left_ui.FileNameVar.get()
		#导入文件
		log =  ReadLog(path)
		#对导入不正确情况的检测(关闭窗口或文件名有误)
		if path == "":
			return
		elif isinstance(log,bool):
			messagebox.showwarning("系统提示","请输入正确的文件！")
			return
		#更新参数
		self.pkdata:list[dict[str,Union[str,list[str]]]] = log["pkdata"]
		self.right_ui.UpdatePushData(log["pushdata"])
		self.left_ui.UpdateTree(log["pkdata"] if Config.Detail_Beta else log["treedata"])
	
	def GenerateTex(self):
		"生成出车文档"
		#获取收车情况并进行检查
		CheckDict = self.left_ui.GetCheckDict()
		PushData = self.right_ui.get_PushData()
		if not len(CheckDict):
			return
		if  not (all(CheckDict.values()) or messagebox.askokcancel(title='警告',message='扫码未完成，确认生成档案?')):
			return
		
		messagebox.showwarning("记得充电","记得给大疆电池充电！")
		file_root, file_dir, file_name = gen_docx(self.pkdata,CheckDict,PushData)
		CompileDoc(file_root, file_dir, file_name)
		
	def QUIT(self):
		"关闭窗口时执行"
		if messagebox.askokcancel(title='警告',message='确认退出系统?'):
			self.win.quit()
			self.win.destroy()
		else:
			self.left_ui.Focus()
	
	def mainloop(self):
		"开始前端UI窗口的主循环"
		self.win.focus_force()
		self.left_ui.Focus()
		change_language("EN")
		self.win.mainloop()

class Left_UI:
	"收车系统的左半部分UI，负责扫描"
	#==================撤销与恢复操作的存储格式=========================
	#删除操作：[{"code":code1, "parent":parent1, "index":index1},...]
	#重做删除操作：[{"code":code1, "parent":parent1, "index":index1},...] 与删除的互为逆序


	#=======初始化===========
	def __init__(self,win:tk.Tk) -> None:
		"初始化器材信息与UI"
		#储存全部器组，用于自定义器组
		self.AllQZDict = dict()
		#储存全部器材的检查状态
		self.AllEquipmentCheck:dict[str,bool] = dict()
		#存储完成的操作
		self.Actives:list[list[dict[str,Union[str,int]]]] = list()
		#存储已完成的撤销操作（即可以重做的）
		self.UndoActives:list[list[dict[str,Union[str,int]]]] = list()

		#初始化UI
		tk.Label(win,text='文件导入与器材扫描',font=('方正书宋GBK',12),justify='left',fg='green').place(relx=0.24,rely=0.09,anchor='n')
		self.LeftFrame = tk.Frame(win)
		self.LeftFrame.place(relx=1/4,rely=0.125,relwidth=1/2,relheight=0.8,anchor='n')
		self.InitUpUI()
		self.InitDownUI()
		self.Init_Choice_BoxMenu()
	
	def Check_Name(self,code:str)->str:
		"改写的CheckName，适用于自定义器组"
		if code in self.AllQZDict:
			return self.AllQZDict[code]
		else:
			return Check_Name(code)

	#======各种UI的初始化======
	def InitUpUI(self):
		"初始化上部分UI"
		self.UpFrame = tk.Frame(self.LeftFrame)
		self.UpFrame.place(relx=0.5,rely=0.02,anchor='n')

		#导入文件部分
		self.LoadFileFrame = tk.Frame(self.UpFrame,width=200,height=60)
		self.LoadFileFrame.grid(column=0,row=0,sticky='w')
		#标题与选择文件名按钮按钮
		self.LoadLabel = tk.Label(self.LoadFileFrame,text='导入出车记录文件',font=('方正书宋GBK',11),justify='left')
		self.LoadLabel.grid(column=0,row=0,sticky='w')
		self.OpenButton = tk.Button(self.LoadFileFrame,text='打开',font=('方正书宋GBK',11),justify='center',command=self.GetPath,cursor="hand2")
		self.OpenButton.grid(column=1,row=0,sticky='e')
		#文件名称与导入按钮
		self.FileNameVar = tk.StringVar(self.UpFrame)
		self.FileNameVar.set("")
		self.FileNameEntry = tk.Entry(self.LoadFileFrame,show=None,font=('Arial Unicode MS',11),width=15,textvariable=self.FileNameVar)
		self.FileNameEntry.grid(column=0,row=1,sticky='w',padx=2)
		self.FileNameEntry.focus_set()
		self.LoadButton = tk.Button(self.LoadFileFrame,text='导入',font=('方正书宋GBK',11),justify='center',cursor="hand2")
		self.LoadButton.grid(column=1,row=1,sticky='e')
		
		#占位行
		tk.Label(self.UpFrame,text='   ',font=('方正书宋GBK',2)).grid(column=0,row=1)

		#器材输入部分
		self.InputFrame = tk.Frame(self.UpFrame,width=200,height=60)
		self.InputFrame.grid(column=0,row=2,sticky='w')
		#标题与手动选择器材的菜单
		self.InputLabel = tk.Label(self.InputFrame,text='请输入器材的编号',font=('方正书宋GBK',11),justify='left')
		self.InputLabel.grid(column=0,row=0,sticky='w')
		self.ChoiceCode = tk.Button(self.InputFrame,text='选择',font=('方正书宋GBK',11),justify='center',command=self.ChoiceMenuPopup,cursor="hand2")
		self.ChoiceCode.grid(column=1,row=0,sticky='e')
		#器材编号输入框与确定输入的按钮
		self.ActiveCode = tk.Entry(self.InputFrame,show=None,font=('Arial Unicode MS',11),width=15)
		self.ActiveCode.grid(column=0,row=1,sticky='w',padx=2)
		self.ActiveCode.bind('<Key>',self.InputEnter)
		self.EnterButton =  tk.Button(self.InputFrame,text='确定',font=('方正书宋GBK',11),justify='center',command=self.GetCode,cursor="hand2")
		self.EnterButton.grid(column=1,row=1,sticky='e')
	
	def InitDownUI(self):
		"初始化下半部分UI"
		#下半部分Frame
		self.ListFrame = tk.Frame(self.LeftFrame,width=160,height=395)
		self.ListFrame.place(relx=0.5,rely=0.3,anchor='n')
		#Canvas，承载撤销恢复按钮
		self.EqboxTitle = tk.Canvas(self.ListFrame,width=150,height=40)
		self.EqboxTitle.pack(side=tk.TOP,fill=tk.X)

		#标签,撤销与恢复按钮
		self.NewQZButton = tk.Label(self.EqboxTitle,text='当前器材列表',font=('方正书宋GBK',11),justify='center')
		self.NewQZButton.pack(side=tk.LEFT,fill=tk.X)
		#撤销按钮
		self.UndoButton = tk.Button(self.EqboxTitle,text='撤销',font=('方正书宋GBK',10),justify='center',command=self.Undo,cursor="hand2")
		self.UndoButton.pack(side=tk.LEFT,fill=tk.X)
		#恢复按钮
		self.RedoButton = tk.Button(self.EqboxTitle,text='恢复',font=('方正书宋GBK',10),justify='center',command=self.Redo,cursor="hand2")
		self.RedoButton.pack(side=tk.LEFT,fill=tk.X)

		#Frame,承装列表和滚动条
		self.FrameTree = tk.Frame(self.ListFrame,width=170,height=350)
		self.FrameTree.pack(side=tk.TOP,fill=tk.BOTH)
		#滚动条
		self.scroll = tk.Scrollbar(self.FrameTree,orient="vertical")
		self.scroll.pack(side=tk.RIGHT,fill=tk.Y)
		#配置器材列表的样式
		style = ttk.Style()
		style.configure('Treeview',font=(None,10),borderwidth=0)
		#器材列表
		self.EquipmentTree = ttk.Treeview(self.FrameTree,show="tree",selectmode="browse",height=14,yscrollcommand=self.scroll.set,columns = ['text'])
		self.EquipmentTree.pack(side=tk.LEFT,fill=tk.BOTH)
		self.EquipmentTree.column("#0", width=20, minwidth=20)
		self.EquipmentTree.column("text",width=130, minwidth=130)
		self.EquipmentTree.bind("<Button-3>", self.TreeMenuPopup)
		#绑定滚动条
		self.scroll.config(command=self.EquipmentTree.yview)
		#颜色设置
		self.EquipmentTree.tag_configure("InQZ",foreground="silver")
		self.EquipmentTree.tag_configure("OutQZ",foreground="black")

		#对应的菜单
		self.TreeMenu = tk.Menu(self.EquipmentTree,tearoff=0)
		#第一行显示器材的编号，随右键点击事件自动更换内容
		self.TreeMenu.add_command(label="Undefined Value", command=self.Focus)

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

	def TreeDelete(self,code:str):
		"当输入某个代码时执行的操作"
		#该列表储存了这一步扫描的器材
		Active:list[dict[str,Union[str,int]]] = list()
		#情况1，扫描的是器组（此处AllQZDict是全局变量，所以不包含自定义的）
		if code in AllQZDict:
			for item in Check_QZInside(code):
				#判断当前是否扫过该物品
				if self.EquipmentTree.exists(item):
					#获取物品的信息加并入操作列表，记录全部信息以防某物品被换了器组
					parent = self.EquipmentTree.parent(item)
					index = self.EquipmentTree.index(item)
					Active.append({"code":item, "parent":parent, "index":index})
					#更新器材状态并删除该物品
					self.AllEquipmentCheck[item] = True
					self.EquipmentTree.delete(item)

		#此时对应的肯定是普通物品
		elif self.EquipmentTree.exists(code):
			parent = self.EquipmentTree.parent(code)
			index = self.EquipmentTree.index(code)
			Active.append({"code":code, "parent":parent, "index":index})
			#更新器材状态并删除该物品
			self.AllEquipmentCheck[code] = True
			self.EquipmentTree.delete(code)
		
		#检查全部器组是否为空，如果为空就删除它并将它加入操作列表
		for qz in self.AllQZDict:
			if self.EquipmentTree.exists(qz) and len(self.EquipmentTree.get_children(qz)) == 0:
				qzindex = self.EquipmentTree.index(qz)
				Active.append({"code":qz, "parent":"", "index":qzindex})
				self.EquipmentTree.delete(qz)
		
		#更新操作列表
		self.Actives.append(Active)
		#清空重做列表
		self.UndoActives.clear()
		#聚焦输入框
		self.Focus()

	def Undo(self):
		"按下撤销按钮时执行的操作"
		#确定列表不为空	
		if not len(self.Actives):
			return
		#获取删除时的顺序，撤销按逆序添回列表
		Active = self.Actives.pop()
		Active.reverse()
		#重做列表添加逆序后的撤销操作
		self.UndoActives.append(Active)
		#按照列表内容依次添回器材，并将器材状态设置为未扫
		for active in Active:
			code = active["code"]
			parent = active["parent"]
			index = active["index"]
			#将器材环回列表
			self.EquipmentTree.insert(parent,index,iid=code,text='',value=[self.Check_Name(code)])
			#设置器材状态
			if code in self.AllEquipmentCheck:
				self.AllEquipmentCheck[code] = False
		#更新颜色
		self.UpdateColor()
		#聚焦
		self.Focus()
	
	def Redo(self):
		"按下重做按钮时执行的操作"
		if not len(self.UndoActives):
			return
		#获取添加时的顺序，撤销按逆序进行删除
		Active = self.UndoActives.pop()
		Active.reverse()
		#撤销列表添加逆序后的重做操作
		self.Actives.append(Active)
		#按照列表内容依次删除器材，并将器材状态设置为已扫
		for active in Active:
			code = active["code"]
			#将器材从列表中删除
			self.EquipmentTree.delete(code)
			#设置器材状态
			if code in self.AllEquipmentCheck:
				self.AllEquipmentCheck[code] = True
		#更新颜色
		self.UpdateColor()
		#聚焦
		self.Focus()

	def TreeClear(self,pop=True):
		"清空列表"
		if pop and (not messagebox.askokcancel("警告","确定删除全部器材？\n该过程为滕滕所禁止！")):
			return
		
		#器材状态词典更新，全部设为已出车
		for code in self.AllEquipmentCheck:
			self.AllEquipmentCheck[code] = True

		#记录删除全部现存器材的操作
		Active:list[dict[str,Union[str,int]]] = list()
		#获取全部的器组(普通器材相当于无内容器组)
		for code in self.EquipmentTree.get_children(""):
			#获取器组内的全部物品
			for item in self.EquipmentTree.get_children(code):
				#未撤销列表添加该操作
				index = self.EquipmentTree.index(item)
				Active.append({"code":item, "parent":code, "index":index})
				#删除该物品
				self.EquipmentTree.delete(item)
			#对该器组进行上述全部操作
			index = self.EquipmentTree.index(code)
			Active.append({"code":code, "parent":"", "index":index})
			self.EquipmentTree.delete(code)
		
		#更新操作列表
		self.Actives.append(Active)
		#清空重做列表
		self.UndoActives.clear()
		#聚焦输入框
		self.Focus()

	def UpdateTree(self,pkdata:list[dict[str,Union[str,list[str]]]]):
		#重置自定义器组数据
		self.AllQZDict.clear()
		self.AllEquipmentCheck.clear()
		self.Actives.clear()
		self.UndoActives.clear()
		#清空原先列表
		self.EquipmentTree.delete(*self.EquipmentTree.get_children(""))
		#重新构建列表
		pkdata.sort(key=lambda pk: (-len(pk["inside"]) if (pk["code"] != "") else 1))
		for pk in pkdata:
			root:str = pk["code"]
			name:str = pk["name"]
			if root != "":
				self.EquipmentTree.insert("",tk.END,iid=root,text='',value=[name])
				self.AllQZDict[root] = name
			for item in pk["inside"]:
				self.AllEquipmentCheck[item] = False
				self.EquipmentTree.insert(root,tk.END,iid=item,text='',value=[self.Check_Name(item)])
		#聚焦
		self.Focus()
		self.UpdateColor()

	#====聚焦====
	def Focus(self):
		"将光标挪到输入框，提高出车系统稳定性"
		self.ActiveCode.focus_set()

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
			self.TreeDelete(code)
		elif code == Config.BetaPassword:
			self.TreeClear()

	def ChoiceEquipment(self,code:str):
		"手动输入器材菜单选择某个器材时执行"
		self.ActiveCode.delete(0,tk.END)
		self.ActiveCode.insert(0,code)
		self.Focus()

	def UpdateColor(self):
		"更新每个器材的颜色"
		for code in self.EquipmentTree.get_children(""):
			self.EquipmentTree.item(code,tags="OutQZ")
			list(map(lambda x:self.EquipmentTree.item(x,tags="InQZ"),self.EquipmentTree.get_children(code)))

	def GetPath(self):
		"弹出文件弹窗并获取文件名称"
		path = filedialog.askopenfilename(title='选择导入的观测记录',initialdir ='./Log',filetypes=[('json','*.json'),('All Files','*')])
		self.FileNameVar.set(path)

	def ChoiceMenuPopup(self):
		"按手动选择器材按钮时弹出"
		self.Focus()
		self.ChoiceBoxmenuMain.tk_popup(self.ChoiceCode.winfo_rootx()+0, self.ChoiceCode.winfo_rooty()+28, 0)

	def TreeMenuPopup(self,event:tk.Event):
		"在器材列表右键时执行"
		#获取菜单的位置
		code = self.EquipmentTree.selection()
		self.Focus()
		#跳过空表
		if not len(code):
			return
		code = code[0]
		#改名字
		self.TreeMenu.entryconfig(0,label=code)
		#弹出窗口
		self.TreeMenu.post(event.x_root, event.y_root)

	#=====导出器材状态======
	def GetCheckDict(self)-> dict[str,bool]:
		"返回检查的状态"
		return self.AllEquipmentCheck

class Right_UI:
	"收车系统右半部分UI，复则其他信息"
	def __init__(self,win:tk.Tk):
		tk.Label(win,text='活动信息管理',font=('方正书宋GBK',12),justify='left',fg='green').place(relx=3/4,rely=0.09,anchor='n')
		self.RightFrame = tk.Frame(win)
		self.RightFrame.place(relx=3/4,rely=0.14,relheight=0.8,anchor='n')
		self.InitUI()

	def InitUI(self):
		"初始化出车信息的UI"
		#活动类型
		self.ActLabel = tk.Label(self.RightFrame,text='活动类型:',font=('方正书宋GBK',12))
		self.ActLabel.grid(column=0,row=0,sticky='w',pady=3)
		self.Act = tk.Entry(self.RightFrame,show=None,font=('Arial Unicode MS',12),width=22)
		self.Act.grid(column=0,row=1,sticky='w',pady=1)
		#活动开始时间，默认为当前系统时间
		self.B_TimeLabel = tk.Label(self.RightFrame,text='活动开始时间:',font=('方正书宋GBK',12))
		self.B_TimeLabel.grid(column=0,row=2,sticky='w',pady=3)
		self.B_Time = tk.Entry(self.RightFrame,show=None,font=('Arial Unicode MS',12),width=22)
		self.B_Time.grid(column=0,row=3,sticky='w',pady=1)
		#活动结束时间，默认为当前系统时间
		self.E_TimeLabel = tk.Label(self.RightFrame,text='活动结束时间:',font=('方正书宋GBK',12))
		self.E_TimeLabel.grid(column=0,row=4,sticky='w',pady=3)
		self.E_Time = tk.Entry(self.RightFrame,show=None,font=('Arial Unicode MS',12),width=22)
		self.E_Time.insert(0,"%d年%d月%d日%d点%d分"%time.localtime(time.time())[:5])
		self.E_Time.grid(column=0,row=5,sticky='w',pady=1)
		#活动地点
		self.PlaceLabel = tk.Label(self.RightFrame,text='活动地点:',font=('方正书宋GBK',12))
		self.PlaceLabel.grid(column=0,row=6,sticky='w',pady=3)
		self.Place = tk.Entry(self.RightFrame,show=None,font=('Arial Unicode MS',12),width=22)
		self.Place.grid(column=0,row=7,sticky='w',pady=1)
		#活动负责人
		self.PersonLabel = tk.Label(self.RightFrame,text='活动负责人:',font=('方正书宋GBK',12))
		self.PersonLabel.grid(column=0,row=8,sticky='w',pady=3)
		self.Person = tk.Entry(self.RightFrame,show=None,font=('Arial Unicode MS',12),width=22)
		self.Person.grid(column=0,row=9,sticky='w',pady=1)
		#备注
		self.NotesLabel = tk.Label(self.RightFrame,text='备注:',font=('方正书宋GBK',12))
		self.NotesLabel.grid(column=0,row=10,sticky='w',pady=3)
		self.Notes = tk.Text(self.RightFrame,font=('方正书宋GBK',12),wrap='char',width=22,height=5)
		self.Notes.grid(column=0,row=11,sticky='w',pady=1)
		#出车按钮
		self.Button = tk.Button(self.RightFrame,text='生成档案',font=('方正书宋GBK',15),justify='center',cursor="hand2")
		self.Button.place(relx=1/2,rely=0.85,anchor='n')

	def UpdatePushData(self,pushdata:dict[str,str]):
		"更新各个输入框的数值"
		self.Act.delete("0","end")
		self.Act.insert(0,pushdata["type"])
		self.B_Time.delete("0","end")
		self.B_Time.insert(0,pushdata["time"])
		self.E_Time.delete("0","end")
		self.E_Time.insert(0,"%d年%d月%d日%d点%d分"%time.localtime(time.time())[:5])
		self.Place.delete("0","end")
		self.Place.insert(0,pushdata["place"])
		self.Person.delete("0","end")
		self.Person.insert(0,pushdata["person"])
		self.Notes.delete("1.0","end")
		self.Notes.insert("1.0",pushdata["notes"])

	def get_PushData(self)-> dict[str,str]:
		"给出当前各输入框的数值"
		Push_Data:dict[str,str] = dict()
		Push_Data["type"] = self.Act.get()
		Push_Data["begin"] = self.B_Time.get()
		Push_Data["end"] = self.E_Time.get()
		Push_Data["place"] = self.Place.get()
		Push_Data["person"] = self.Person.get()
		Push_Data["notes"] = self.Notes.get('1.0',tk.END)
		return Push_Data


if __name__ == "__main__":
	UI = UI_beta()
	UI.mainloop()