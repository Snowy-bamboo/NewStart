#############################################
#网上找的代码，代替tkinter.tix.Balloon实现功能
#参考 https://stackoverflow.com/a/36221216
#别问我这部分都写了啥，我也没仔细看，能用就行
#############################################

import tkinter as tk
from tkinter import ttk


class FakeBalloon:
	"代替原版tkinter的Balloon，实现提示窗口"
	def __init__(self,root:tk.Misc):
		self.root = root

	def bind_widget(self,widget:tk.Widget,text,timeout=200,offset=(0, -20),**kw):
		"将提示窗口与控件绑定"
		Tip(self.root,widget,text,timeout,offset,**kw)

class Tip:
	"网上抄的，针对指定的 widget 创建一个 tooltip"
	   
	def __init__(self,root:tk.Misc,widget:tk.Widget,text,timeout=200,offset=(0, -20),**kw):
		'''
		参数
		=======
		widget: tkinter 小部件
		text: (str) tooltip 的文本信息
		timeout: 鼠标必须悬停 timeout 毫秒，才会显示 tooltip
		'''
		# 设置 用户参数
		self.root = root
		self.widget = widget
		self.text = text
		self.timeout = timeout
		self.offset = offset
		# 内部参数初始化
		self._init_params()
		# 绑定事件
		self.widget.bind("<Enter>", self.enter)
		self.widget.bind("<Leave>", self.leave)
		
	def _init_params(self):
		'''内部参数的初始化'''
		self.id_after = None
		self.x, self.y = 0, 0
		self.tipwindow = None
		self.background = 'lightyellow'
		
	def cursor(self, event:tk.Event):
		'''设定 鼠标光标的位置坐标 (x,y)'''
		self.x = event.x
		self.y = event.y
		
	def unschedule(self):
		'''取消用于鼠标悬停时间的计时器'''
		if self.id_after:
			self.widget.after_cancel(self.id_after)
		else:
			self.id_after = None

	def tip_window(self):
		window = tk.Toplevel(self.root)
		# 设置窗体属性
		## 隐藏窗体的标题、状态栏等
		window.overrideredirect(True)
		## 保持在主窗口的上面
		window.attributes("-topmost")  # 也可以使用 `-topmost`
		window.attributes("-alpha", 0.92857142857)	# 设置透明度为 13/14
		x = self.widget.winfo_rootx() + self.x + self.offset[0]
		y = self.widget.winfo_rooty() + self.y + self.offset[1]
		window.wm_geometry("+%d+%d" % (x, y))
		return window
			
	def showtip(self):
		"""
		创建一个带有工具提示文本的 topoltip 窗口
		"""
		params = {
			'text': self.text, 
			'justify': 'left',
			'background': self.background,
			'relief': 'solid', 
			'borderwidth': 1
		}
		self.tipwindow = self.tip_window()
		label = ttk.Label(self.tipwindow, **params)
		label.grid(sticky='nsew')
			
	def schedule(self):
		"""
		安排计时器以计时鼠标悬停的时间
		"""
		self.id_after = self.widget.after(self.timeout, self.showtip)
		
	def enter(self, event:tk.Event):
		"""
		鼠标进入 widget 的回调函数
		
		参数
		=========
		:event:  来自于 tkinter，有鼠标的 x,y 坐标属性
		"""
		self.cursor(event)
		self.schedule()
		
	def hidetip(self):
		"""
		销毁 tooltip window
		"""
		if self.tipwindow:
			self.tipwindow.destroy()
		else:
			self.tipwindow = None
		  
	def leave(self, event):
		"""
		鼠标离开 widget 的销毁 tooltip window
		 
		参数
		=========
		:event:  来自于 tkinter，没有被使用
		"""
		self.unschedule()
		self.hidetip()