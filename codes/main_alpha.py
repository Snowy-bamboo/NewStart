import os

# Ensure all "./Appdata" and "./Resource" relative paths resolve from NewStart.
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DataReader import jsonDict,Check_NessName,DefaultPPmess
from UI_alpha import UI_alpha
from UI_alpha import Pop_StepOneWarningWindow, Pop_StepOneCYWarningWindow, Pop_StepTwoPPMessInputWindow, Pop_FinalConfirmWindow, Pop_LastStepWindow

from ConfigReader import Config

#多导一个库，用于type hint（数据类型注释）
from typing import Union




#==============================================为算法准备的数据类型======================================================================

class Memory:
	"相当于全局变量，储存各种跨函数信息"
	def __init__(self):
		self.Counter:dict[str,int] = dict()
		self.DefaultPPmess:dict[str,int] = DefaultPPmess.copy()
		self.pkdata:list[dict[str,Union[str,bool,list[str]]]] = []
		self.warndata:dict[str,list[str]] = dict()
		self.pushdata:dict[str,str] = {"type":"例观", "place":"静园草坪","person":"", "notes":""}
	
	def UpdatePushData(self,newpushdata:dict[str,str]):
		"更新全局变量的出车信息存储"
		self.pushdata.update(newpushdata)
	
	def GetPushData(self):
		"导出全局变量的出车信息存储"
		return self.pushdata.copy()

class Equipment:
	"器材类，包含了器材的全部信息"
	def __init__(self, code:str):
		#录入器材的基本信息
		data:dict = jsonDict[code]
		self.code:str = code
		self.type:str = data["type"] if "type" in data else code[:2]
		self.name:str = data['name']
		self.warning:list[str] = data['warning'] if "warning" in data else []
		self.provide:list[str] = data['provide'] if "provide" in data else []
		self.ness:list[str] = data['ness'] if "ness" in data else []
		self.new_package = False #对于特殊器材，此值更新为True
		self.OutOfQZ = True #器材是在某个器组中还是在散件中

		#对于特殊器材，需要在程序中该器材是否建立新的器材包
		if "new_package" in data:
			self.new_package = True
			#判断该包是否要程序进行望远镜，重锤与电源匹配
			self.TJ_pair = bool(data["new_package"]["TJ_judge"])
			self.PP_judge = bool(data["new_package"]["PP_judge"])
			self.DC_judge = bool(data["new_package"]["DC_judge"])
			#重锤的信息录入，缺省值-1代表这个包需要后续判断
			if self.TJ_pair:
				self.CY_maxprovidmess:float = data["TJ_information"]['CY_maxprovidmess'] * Config.TJ_MaxRate #该数值为赤道仪的最大载重乘以设置的比例
			if self.PP_judge:
				PP_data:dict = data["PP_information"] if "PP_information" in data else dict()
				self.PP_type:str = PP_data["PPType"] if "PPType" in PP_data else "PP" #该变量为赤道仪用的重锤种类，如埃顿与信达
				self.nessPPmess:int = PP_data["nessPPmess"] if "nessPPmess" in PP_data else -1 #该值为-1时由望远镜传入，否则由json传入（如星野）
				self.Decay_PPmess:int = PP_data["Decay_PPmess"] if "Decay_PPmess" in PP_data else 0 #该值为赤道仪自身可平衡部分重量（如谐波）
				self.default_PPmess:int = PP_data["default_PPmess"] if "default_PPmess" in PP_data else 10 #该数值为赤道仪默认安装重锤质量
			#电源接口信息录入
			if self.DC_judge:
				self.EQPort:str = data["DC_information"]["EQPort"] #该变量为用电器的母头

		#对于望远镜，录入其质量与需要重锤质量
		elif self.type == "TJ":
			self.nessCYmess:float = data["TJ_information"]['nessCYmess'] #该数值为望远镜需要赤道仪的载重
			self.nessPPmess:int = data["TJ_information"]['nessPPmess'] #该数值为望远镜需要的重锤质量
		#对于重锤,录入其对应重锤类型(默认为【PP】)与重锤数量(默认为5)
		elif self.type == "PP":
			PP_data = data["PP_information"] if "PP_information" in data else dict()
			self.PP_type:str = PP_data['PPType'] if "PPType" in PP_data else "PP" #该变量为重锤的种类，如埃顿与信达
			self.mess:int = PP_data['Mess'] if "Mess" in PP_data else 5 #该变量为重锤的重量
		#对于电池，录入其接口种类和最大输出电流(如果有的话，默认为-1代表无限制或未定义)
		elif self.type == "DC":
			self.DCPort:str = data["DC_information"]['DCPort'] #该变量为电池的公头
			self.maxCurrent:float = data["DC_information"]['maxCurrent'] if "maxCurrent" in data["DC_information"] else -1 #该变量为电池的最大输出电流，-1代表未定义，后续代码中-1认为无限制
		#对于电线，录入其电源端与器材端种类
		elif self.type == "DX":
			self.EQPort:str = data["DC_information"]['EQPort'] #该变量为电线的公头
			self.DCPort:str = data["DC_information"]['DCPort'] #该变量为电线的母头

	def __str__(self) -> str:
		return f"code={self.code},name={self.name}"
	
	def __repr__(self) -> str:
		return str(self)

class Package:
	"对器材进行打包，并储存器材依旧需要的需求"
	def __init__(self, root:Equipment,initCounter:dict[str,int],FreeEquipment:set[str]):
		"添加包的根器材"
		#器材基本信息的录入，包含名称、警告、普通的需求与提供
		root.OutOfQZ = (root.code in FreeEquipment)
		self.root = root
		self.name = root.name #利用根器材的名称来命名包
		self.Equipment_list = [root]
		self.warning = {root.code: root.warning.copy()}
		self.Counter = initCounter.copy()
		self.FreeEquipment = FreeEquipment
		for item in root.ness:
			self.Counter[item] -= 1
		for item in root.provide:
			self.Counter[item] += 1
		#记录package望远镜质量是否超标(先设为否，靠后面望远镜来更新)、是否重锤匹配、是否电源匹。如果是，录入匹配的信息。
		self.TJ_pair = root.TJ_pair
		self.PP_judge =  root.PP_judge
		self.DC_judge = root.DC_judge
		if self.TJ_pair:
			#该器材包为赤道仪可架望远镜，导入赤道仪最大载重
			self.CY_maxprovidmess = root.CY_maxprovidmess
		if self.PP_judge:
			#该器材包需要匹配重锤，导入重锤种类质量需求与赤道仪自带承重（如谐波）
			self.PP_type:str = root.PP_type
			self.nessPPmess:int = root.nessPPmess
			self.Decay_PPmess:int = root.Decay_PPmess
		if self.DC_judge:
			#该器材包需要供电，导入器材母头的类型
			self.EQPort:str = root.EQPort
	
	def __str__(self) -> str:
		"debug输出用"
		PP_str_output = f"PP_information:\nPP_type: {self.PP_type}\nness_PPmess: {self.nessPPmess}" if self.PP_judge else "No PP_judge"
		DC_str_output = f"Equipment_Port: {self.EQPort}" if self.PP_judge else "No DC_judge"
		return f"Counter = {self.Counter}\nList = {list(map(lambda x:x.code,self.Equipment_list))}\n{PP_str_output}\n{DC_str_output}"
	
	def __repr__(self) -> str:
		"debug输出用"
		return str(list(map(lambda x:x.code,self.Equipment_list)))

	def __iter__(self):
		"返回全部器材"
		return iter(self.Equipment_list)

	def __len__(self) -> int:
		return len(self.Equipment_list)

	def addTJ(self,TJ:Equipment):
		"为赤道仪添加望远镜，或将不需要望远镜的赤道仪更新其状态"
		if isinstance(TJ,str):
			#将没有望远镜的赤道仪设为空
			self.TJ_pair = False
		else:
			#除了添加常规器材流程外，还要将包的名称添加望远镜的名称，并将缺省的重锤质量更新
			TJ.OutOfQZ = (TJ.code in self.FreeEquipment)
			self.append(TJ)
			self.name += f' + {TJ.name}' #包的名称加上望远镜的名字
			self.nessPPmess = TJ.nessPPmess - self.Decay_PPmess #谐波的作用相当于是少架10kg重锤
			self.nessCYmess = TJ.nessCYmess #导入

	def addPP(self,PP:Equipment):
		"重锤判断添加重锤"
		PP.OutOfQZ = (PP.code in self.FreeEquipment)
		self.Equipment_list.append(PP)
		self.nessPPmess -= PP.mess

	def append(self, equipment:Equipment):
		"添加常规的器材"
		#添加器材与其警告
		equipment.OutOfQZ = (equipment.code in self.FreeEquipment)
		self.Equipment_list.append(equipment)
		self.warning[equipment.code] = equipment.warning.copy()
		#统计需求变化
		for item in equipment.ness:
			self.Counter[item] -= 1
		for item in equipment.provide:
			self.Counter[item] += 1

	def get_UI_Data(self) -> dict[str, Union[str,bool,list[str]]]:
		"为结果UI提供全部信息"
		Warn:list[str] = []
		Lack:list[str] = []
		TJPairWarning:Union[str,bool] = False
		if self.Counter["CY"] > 0:
			Warn.append("该赤道仪并未架设望远镜")
			TJPairWarning = "该赤道仪并未架设望远镜"
		elif self.Counter["CY"] < 0:
			Warn.append("该望远镜无赤道仪")
			TJPairWarning = "该望远镜无赤道仪"
		if self.TJ_pair and self.CY_maxprovidmess < self.nessCYmess:
			Lack.append("赤道仪载重不够")
		if self.PP_judge and self.nessPPmess > 0:
			Lack.append(f"缺少重锤{self.nessPPmess}kg")
		if self.DC_judge:
			DC = 'Lack'
			DX = 'Lack'
			for item in self.Equipment_list:
				if item.type == 'DC':
					DC = item
				elif item.type == 'DX':
					DX = item
			#【这里写or是尽量防止出现报错，虽然这种情况不可能发生且python的惰性逻辑会跳过后面】
			if isinstance(DC,str) or isinstance(DX,str):
				Lack.append("缺少电池或电源线")
			else:
				if self.EQPort != DX.EQPort:
					Warn.append("器材处接口不同")
				if DC.DCPort != DX.DCPort:
					Warn.append("电源处接口不同")
		
		for ness in self.Counter:
			if ness!= 'CY' and self.Counter[ness] < 0:
				Lack.append(f"{Check_NessName(ness)}: {self.Counter[ness]}")

		#包内真有的器材与在器组中的器材
		Contain = list(map(lambda eq: eq.code, filter(lambda eq: eq.OutOfQZ, self.Equipment_list)))
		Out = list(map(lambda eq: eq.code, filter(lambda eq: not eq.OutOfQZ, self.Equipment_list)))
		return {"Name":self.name, "Warn":Warn, "Lack":Lack,"Inside":Contain, "Outside":Out, "IsQZ":False, "TJPairWarning":TJPairWarning}
	
	def getWarning(self) -> dict[str,list[str]]:
		"返回全部警告信息"
		result:dict[str,list[str]] = dict()
		codes = list(filter(lambda cd:len(self.warning[cd]), self.warning))
		for cd in codes:
			result[cd] = self.warning[cd]
		return result


class Redundant_Package:
	"存储多余器材的占位类"
	def __init__(self,name:str,eq_list:list[str],isqz:bool=False):
		self.name:str = name
		self.isqz:bool = isqz
		self.Equipment_list:list[str] = eq_list.copy()
		self.Equipment_list.sort(key=lambda x: x.code)
		self.warning:dict[str,list[str]] = {item.code:item.warning.copy() for item in eq_list}
		self.TJ_pair = False
		self.PP_judge = False
		self.DC_judge = False

	def __len__(self) -> int:
		return len(self.Equipment_list)
	
	def __repr__(self) -> str:
		return str(list(map(lambda x:x.code,self.Equipment_list)))
	
	def __str__(self) -> str:
		return str(list(map(lambda x:x.code,self.Equipment_list)))
	
	def get_UI_Data(self) -> dict[str, Union[str,bool,list[str]]]:
		"为结果UI提供全部信息"
		Inside = list(map(lambda eq: eq.code, self.Equipment_list))
		return {"Name":self.name, "Warn":[], "Lack":[], "Inside":Inside, "Outside":[], "IsQZ":self.isqz, "TJPairWarning":False}

	def getWarning(self) -> dict[str,list[str]]:
		"返回全部警告信息"
		result:dict[str,list[str]] = dict()
		codes = list(filter(lambda cd:len(self.warning[cd]), self.warning))
		for cd in codes:
			result[cd] = self.warning[cd]
		return result



def StepOne(UI:UI_alpha,memory:Memory):
	"按下粗检查按钮发生的事情"
	#将扫码的器材全部转为Equipment，存入Equipment_list
	Code_list = UI.GetInputEquipmentList()
	##debug## Code_list = "TJ001 TJ002 TJ003 TJ004 TJ005 TJ501 TJ502 TJ503 TJ504 CY001 CY002 CY004 CY501 CY502 CY503".split()
	Equipment_list = list(map(Equipment,Code_list))

	#粗查核心模块，构建存储各种需求是否满足的字典，并对每种需求进行检测，随后检查是否通过需求计数
	memory.Counter.clear()
	Counter = {"CY":0,"指星笔":0,"防潮垫":0,"SJ":0,"手机支架":0,"头灯":0,"手电":0}
	for item in Equipment_list:
		#需求，表中数值-1
		for ness in item.ness:
			if ness in Counter:
				Counter[ness] -= 1
			else:
				Counter[ness] = -1
		#提供，表中数值+1
		for provide in item.provide:
			if provide in Counter:
				Counter[provide] += 1
			else:
				Counter[provide] = 1

	#检测粗查不能通过的情况，包括望远镜赤道仪数目检测与普通配件检测
	if Pop_StepOneCYWarningWindow(UI.win,Counter["CY"]) or Pop_StepOneWarningWindow(UI.win,Counter.copy()):
		#若弹窗得到的选择是重新检查，则退出粗查程序
		UI.CheckUI_ResetFirstResult()
		UI.Focus()
		return
	
	memory.Counter.update(Counter)

	#将杂项的数目进行统计以通讯给UI
	ZX_data = {code:0 for code in ["DC","DX","SJ","PAD","LASER","PHONE"]}
	ZX_data["SJ"] = Counter["SJ"]
	ZX_data["PAD"] = Counter["防潮垫"]
	ZX_data["LASER"] = Counter["指星笔"]
	ZX_data["PHONE"] = Counter["手机支架"]
	ZX_data["LIGHT"] = Counter["头灯"]+Counter["手电"]
	
	TJ_data:dict[str,float] = dict()
	Root_data:dict[str,dict[str,Union[float,bool]]] = dict()
	#将望远镜与根器材的数据进行整理，以互相通讯的格式传给中部的配对UI，顺便计算电池数目。
	for item in Equipment_list:
		if item.new_package:
			Root_data[item.code] = {"mess":(item.CY_maxprovidmess if item.TJ_pair else -1), "DC":item.DC_judge}
		elif item.type == 'TJ':
			TJ_data[item.code] = item.nessCYmess
		elif item.type == 'DC':
			ZX_data["DC"] += 1
		elif item.type == 'DX':
			ZX_data["DX"] += 1
	
	#重置中部UI并将这些信息传递给中部UI
	UI.Middle_Reset()
	UI.Middle_UpdateZX(ZX_data)
	UI.Middle_BuildCYPair(TJ_data,Root_data)

	#更新按钮下方状态
	UI.CheckUI_FirstStep(min(Counter.values()) >= 0)
	#聚焦
	UI.Focus()




def StepTwo(UI:UI_alpha,memory:Memory):
	"细检查，为器材进行最后的配对"
	#清空之前存储的器材包信息
	memory.pkdata.clear()
	memory.warndata.clear()
	#获取扫描的全部器材
	Equipment_list = list(map(Equipment, UI.GetInputEquipmentList()))
	#获取器材的树结构
	Equipment_Tree = UI.GetEquipmentTree()
	#获取全部散件
	FreeEquipment = Equipment_Tree.pop("")["inside"]
	#记录配对过程中发现的多余器材
	Redundant_list:list[Equipment] = []

	#储存全部包
	Package_list:list[Package] = []
	#获取全部包的信息（是否进行望远镜匹配与电池匹配）
	TJ_Pair_data, DC_data = UI.GetPackageData()
	#全部包的列表
	Root_list = list(TJ_Pair_data)
	#记录全部望远镜
	Paired_TJ:set[str] = set(TJ_Pair_data[rt] for rt in TJ_Pair_data if TJ_Pair_data[rt] != "Empty")
	UnPaired_TJ_list:list[Equipment] = [] #未配对的望远镜
	DC_list:list[Equipment] = [] #此DC_list为局域变量，用于匹配，非之前判断电源数的全局变量
	PP_list:list[Equipment] = [] #记录重锤信息
	DX_list:list[Equipment] = [] #电源线
	Other_list:list[Equipment] = [] #最后再决定的各种普通配件

	#对器材进行分类，加入各个list
	for item in Equipment_list:
		if item.new_package:
			pass
		elif item.type == "TJ":
			UnPaired_TJ_list.append(item) if item.code not in Paired_TJ else None
		elif item.type == 'PP':
			PP_list.append(item)
		elif item.type == 'DX':
			DX_list.append(item)
		elif item.type == 'DC':
			DC_list.append(item)
		elif len(item.provide) == 0:
			Redundant_list.append(item)
		else:
			Other_list.append(item)
	
	#====================================================================================#
	#==========================出车系统核心配对程序开始====================================#
	#====================================================================================#


	#【匹配1：望远镜匹配】
	#建立新的器材包，对可行的包进行望远镜匹配
	InitCounter = {ness:0 for ness in memory.Counter} #全部指标为0的统计字典传入器材包(器材包内自带copy，故一定为浅拷贝)
	for root in Root_list:
		#新建新的器材包
		pk = Package(Equipment(root), InitCounter, FreeEquipment)
		#对配对望远镜的器材包添加望远镜
		tj_code = TJ_Pair_data[root]
		pk.addTJ("NO_TJ_pair" if tj_code == "Empty" else Equipment(tj_code))
		pk.DC_judge = DC_data[root]
		Package_list.append(pk)


	#【匹配2：重锤匹配】
	#第零步，获取全部需要重锤配对的包，并获取没有望远镜的赤道仪需要的重锤质量
	PP_judge_list = list(filter(lambda pk:pk.PP_judge, Package_list))
	#找到需要进行重锤匹配但并未传入重锤质量需求的器材包(多数情况为空赤道仪)，并弹出弹窗来采集信息。
	Lack_information_package_list = list(filter(lambda pk:pk.nessPPmess == -1, PP_judge_list))

	#若有不知道重锤需求质量的包，则弹出重锤质量窗口来获取重锤质量
	if len(Lack_information_package_list):
		#传输进前端的数据。此处用列表是因为需要保序
		Package_name_list = [pk.name for pk in Lack_information_package_list]
		Package_defaultmess_list = [memory.DefaultPPmess[pk.root.code] for pk in Lack_information_package_list]
		#弹出重锤质量窗口，记录返回结果
		BreakStepTwo, NessPPmess_List = Pop_StepTwoPPMessInputWindow(UI.win,Package_name_list, Package_defaultmess_list)
		#关闭窗口后,若选择中断则停止检查，否则录入重锤配对信息
		if BreakStepTwo:
			UI.Right_Reset()
			UI.CheckUI_ResetSecondResult()
			UI.Focus()
			return
		else:
			#将重锤信息录入赤道仪并更新memory中赤道仪需要重锤质量的默认值	
			for pk, pk_npm in zip(Lack_information_package_list, NessPPmess_List):
				pk.nessPPmess = int(pk_npm)
				memory.DefaultPPmess[pk.root.code] = pk.nessPPmess
	

	#第一步，将重锤进行分类，随后按各个类别来分别进行重锤匹配
	PPtype_set = set(map(lambda pk:pk.PP_type, PP_judge_list)) #记录全部重锤种类的组合
	PP_dict:dict[str,list[Equipment]] = {pptype:[] for pptype in PPtype_set} #记录重锤分类的字典
	#将重锤按照种类进行分类
	for pp in PP_list:
		if pp.PP_type in PPtype_set:
			#待会要配对的重锤进行分类
			PP_dict[pp.PP_type].append(pp)
		else:
			#绝不会用到的重锤放入多余器材【现实中谁会闲的用到这行啊！！ 开玩笑的，别删，要不然万一不小心多扫一个就吞器材了】
			Redundant_list.append(pp)

	#第二步，按照重锤的类别来依次匹配
	#匹配逻辑是依次将大的重锤匹配给目前离平衡最远的
	#【目前程序可能存在的问题之一！！！贪心法匹配重锤只对当前学会已有器材有效！！！无法解决特殊质量重锤！！！】

	for pptype in PPtype_set: #遍历全部的重锤种类
		#获取使用该种类重锤的全部包
		single_pk_list = list(filter(lambda pk:pk.PP_type == pptype, PP_judge_list))
		#获取对同种类型的重锤并由重到轻排序
		single_pp_list = PP_dict[pptype]
		single_pp_list.sort(key=lambda x: -x.mess)
		#每次将离平衡最远的赤道仪匹配最重的重锤
		for pp in single_pp_list:
			#获取离平衡最远的赤道仪
			pk = max(single_pk_list, key=(lambda PK: PK.nessPPmess))
			#匹配重锤或弃掉重锤
			if pk.nessPPmess > 0:
				pk.addPP(pp)
			else:
				Redundant_list.append(pp)
	


	#【匹配3：电池与电源线的匹配】
	#目前的算法是利用满足尽可能多需求的方法进行分配
	#详细说明见文档（文档已经咕了）

	#器材构建器材的列表(母头是否需要带锁)
	Need_DC_Package_list = list(filter(lambda pk:(pk.DC_judge and pk.EQPort != 'AVX'), Package_list))
	Need_DC_AVX_list = list(filter(lambda pk:(pk.DC_judge and pk.EQPort == 'AVX'), Package_list))
	#五类电线。其中带锁延长线母头永远是5521
	line_25to21_list = list(filter(lambda dx:(dx.DCPort == '5525' and dx.EQPort == '5521'), DX_list))
	line_21to21_list = list(filter(lambda dx:(dx.DCPort == '5521' and dx.EQPort == '5521'), DX_list))
	line_25to25_list = list(filter(lambda dx:(dx.DCPort == '5525' and dx.EQPort == '5525'), DX_list))
	line_21to25_list = list(filter(lambda dx:(dx.DCPort == '5521' and dx.EQPort == '5525'), DX_list))
	line_AVX_list = list(filter(lambda dx:(dx.EQPort == 'AVX'), DX_list))


	#按照接头类型对器材与电池进行排序
	#EQ:[25->->->21]
	#DC:[25->->->21]
	keyfuncValue = {"5521":1,"5525":0}
	Need_DC_Package_list.sort(key= lambda x: keyfuncValue[x.EQPort])
	DC_list.sort(key= lambda x: keyfuncValue[x.DCPort])

	#第一步：对带锁延长线(适用于AVX)进行匹配。带锁延长线母头永远为21
	#对于带锁延长线，电池要尽可能匹配公头为21的，用光了再匹配25的
	#程序用for循环是为了避免潜在的死循环（虽然本质上更适合用while循环）
	for _ in range(len(Need_DC_AVX_list)):
		if len(line_AVX_list) and len(DC_list):
			avx = Need_DC_AVX_list.pop()
			avx.append(DC_list.pop())
			avx.append(line_AVX_list.pop())
		else:
			break
	
	#第二步：将多出的AVX按照正常的母头为5521的器材进行判断
	"""不允许AVX用非带锁线，这段逻辑橄榄了
	for pk in Need_DC_AVX_list:
		pk.EQPort = '5521'
		Need_DC_Package_list.append(pk)"""

	#第三步：去除多余电池（优先剔除公头为5521的电池）
	while len(DC_list) > len(Need_DC_Package_list):
		Redundant_list.append(DC_list.pop())

	#第四步：定25to21的线。这是最垃圾的线，只能连一种情况，所以优先级最高。
	DC_list.reverse()
	#EQ:[25->->->21]
	#DC:[21->->->25]
	for line in line_25to21_list:
		if len(DC_list) and DC_list[-1].DCPort == '5525' and Need_DC_Package_list[-1].EQPort == '5521':
			pk = Need_DC_Package_list.pop()
			pk.append(DC_list.pop())
			pk.append(line)
		else:
			Redundant_list.append(line)

	#第五步，定21to21的线。这种线与25to25的线平级，谁先谁后其实无所谓。
	DC_list.reverse()
	#EQ:[25->->->21]
	#DC:[25->->->21]
	for line in line_21to21_list:
		if len(DC_list) and Need_DC_Package_list[-1].EQPort == '5521':
			pk = Need_DC_Package_list.pop()
			pk.append(DC_list.pop())
			pk.append(line)
		else:
			Redundant_list.append(line)

	#第六步，定25to25的线
	DC_list.reverse()
	Need_DC_Package_list.reverse()
	#EQ:[21->->->25]
	#DC:[21->->->25]
	for line in line_25to25_list:
		if len(DC_list) and DC_list[-1].DCPort == '5525':
			pk = Need_DC_Package_list.pop()
			pk.append(DC_list.pop())
			pk.append(line)
		else:
			Redundant_list.append(line)
	
	#第七步，定21to25的线。这种线是万能线，所以随意匹配。
	for line in line_21to25_list:
		if len(DC_list):
			pk = Need_DC_Package_list.pop()
			pk.append(DC_list.pop())
			pk.append(line)
		else:
			Redundant_list.append(line)
		
	#第八步，将之前AVX临时改成5521的口换回AVX
	"""现在这段逻辑被禁止了
	for pk in Need_DC_AVX_list:
		pk.EQPort = 'AVX'
	"""
	
	#第九步，记录多余的AVX线和电池
	Redundant_list += line_AVX_list
	Redundant_list += DC_list



	#将多余的望远镜写入package
	for root in UnPaired_TJ_list:
		root.TJ_pair = False
		root.PP_judge = False
		root.DC_judge = False
		Package_list.append(Package(root, InitCounter,FreeEquipment))

	#利用贪婪法对一般的器材进行分类与匹配，每个器材都优先给最缺的。
	#【目前程序可能存在的问题之一！！！贪心法只能实现每个器材提供一个provide的情况！！！】
	for item in Other_list:
		if len(Package_list) and min(pk.Counter[item.provide[0]] for pk in Package_list) < 0:
			min(Package_list,key=lambda x:x.Counter[item.provide[0]]).append(item)
		else:
			Redundant_list.append(item)

	
	#====================================================================================#
	#==========================出车系统核心配对程序结束====================================#
	#====================================================================================#


	#建立几个分组，来装多余的器材
	True_redundant_list:list[Equipment] = []
	MJ_list:list[Equipment] = []
	PL_list:list[Equipment] = []
	SJ_list:list[Equipment] = []
	ZX_list:list[Equipment] = []

	#对于未配对的器材进行分类
	for item in filter(lambda x:x.code in FreeEquipment ,Redundant_list):
		if item.type == 'MJ':
			MJ_list.append(item)
		elif item.type == 'PL':
			PL_list.append(item)
		elif item.type == 'SJ':
			SJ_list.append(item)
		elif item.type == 'ZX':
			ZX_list.append(item)
		else:
			True_redundant_list.append(item)

	#为每个器组建立伪器材包
	for qz in Equipment_Tree.values():
		Package_list.append(Redundant_Package(qz["name"],list(map(Equipment,qz["inside"])),True))
	#为其余分类建立伪器材包
	if len(MJ_list):
		Package_list.append(Redundant_Package("目镜",MJ_list))
	if len(PL_list):
		Package_list.append(Redundant_Package("滤镜",PL_list))
	if len(SJ_list):
		Package_list.append(Redundant_Package("双筒",SJ_list))
	if len(ZX_list):
		Package_list.append(Redundant_Package("杂项",ZX_list))
	if len(True_redundant_list):
		Package_list.append(Redundant_Package("多余器材",True_redundant_list))

	#更新器材包信息
	memory.pkdata = list(map(lambda x:x.get_UI_Data(), Package_list))
	Warndata:dict[str,list[str]] = dict()
	for pk in Package_list:
		Warndata.update(pk.getWarning())
	memory.warndata = Warndata
	#更新UI
	UI.Right_UpdateData(memory.pkdata)
	Checkpass = len(Package_list) == 0 or max(len(x.get_UI_Data()["Lack"]) for x in Package_list) == 0
	UI.CheckUI_SecondStep(Checkpass)
	UI.Focus()
	


def FinalConfirm(UI:UI_alpha, memory:Memory)-> bool:
	"传入信息，输入光速进行检查"
	if any(map(lambda x:len(x["Lack"]),memory.pkdata)) or any(map(lambda x:isinstance(x["TJPairWarning"],str),memory.pkdata)):
		return Pop_FinalConfirmWindow(UI.win,memory.pkdata)

	return True
	



def LastStep(UI:UI_alpha, memory:Memory):
	"传入信息，弹出出车窗口"
	warn_data = memory.warndata
	zx_counts, zx_colors = UI.GetZXData()
	push_data = memory.GetPushData()
	pk_data = memory.pkdata
	Pop_LastStepWindow(UI.win,warn_data, zx_counts, zx_colors, push_data, pk_data,memory.UpdatePushData)

#================================封装GUI用的class=====================================

def mainalpha():
	memory = Memory()
	UI =  UI_alpha()
	UI.BondButtonFunction(
		UpdateMemory=memory.UpdatePushData,
		GetMemory=memory.GetPushData,
		StepOneFunction=(lambda ui=UI,m=memory: StepOne(ui,m)),
		StepTwoFunction=(lambda ui=UI,m=memory: StepTwo(ui,m)),
		Final_Confirm=(lambda ui=UI,m=memory: FinalConfirm(ui,m)),
		LastStep=(lambda ui=UI,m=memory: LastStep(ui,m))
		)
	UI.mainloop()

if __name__ == "__main__":
	mainalpha()
