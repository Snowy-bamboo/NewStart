import json
import os
import time
from typing import Union
from tkinter import filedialog
from ConfigReader import Config

#建立存储出车json文件与临时保存出车文件的文件夹
if not os.path.exists("./Log"):
	os.makedirs("./Log")

if not os.path.exists("./Temporary"):
	os.makedirs("./Temporary")


#读取数据，建立以code为索引的大字典
with open('./Appdata/equipment.json','r',encoding='utf8') as jsonfile:
	jsonlist:list[dict] = json.loads(jsonfile.read())
	jsonDict:dict[str,dict] = dict()
	for item in jsonlist:
		jsonDict.update({item['code']:item})
		#属于个人的器材要单独标注
		if item['code'][2] == '5':
			 jsonDict[item['code']]['name'] += '*'

#导入器材需求的亲民版名字
with open('./Appdata/ness_name.json','r',encoding='utf8') as jsonfile:
	nessDict:dict[str,str] = json.loads(jsonfile.read())

#导入各种类型器材的大类别汇总，用作器材输入菜单的分类处
with open('./Appdata/codetype.json','r',encoding='utf8') as jsonfile:
	CodeTypeDict:dict[str,str] = json.loads(jsonfile.read())

AllEquipmentList:set[str] = set(jsonDict)
SortedAllEquipmentList = list(jsonDict)
AllQZDict:dict[str,str] = {code:jsonDict[code]["name"] for code in jsonDict if code[:2] == 'QZ'}
AllTypenameList = list(CodeTypeDict.values())
QZDict:dict[str,list[str]] = {code:jsonDict[code]['inside'] for code in jsonDict if code[:2] == 'QZ'}
QZName:dict[str,str] = {jsonDict[code]['name']:code for code in AllQZDict}

def Check_NessName(ness:str) -> str:
	"查找需求的亲民版名字"
	return nessDict[ness] if ness in nessDict else ness

def Check_Enable(code:str) -> bool:
	"查看某项器材是否启用"
	Disable =  "disable" in jsonDict[code] and jsonDict[code]["disable"]
	return (not Disable) or Config.EndableDisables

def Check_Name(code:str) -> str:
	"查找器材的名字"
	return jsonDict[code]["name"]

def Check_QZInside(code:str) -> list:
	"查找器组的内容物"
	return jsonDict[code]['inside']

def Check_Classify(code:str) -> str:
	"返回手动化选择菜单的器材分类"
	if code[:2] == "DX":
		return CodeTypeDict[code[:3]]
	elif code[:2] == 'MJ':
		return ("目镜" if jsonDict[code]["provide"][0] in ("MJ","巴洛镜") else "天顶镜") if "provide" in jsonDict[code] else "减焦镜"
	else:
		return CodeTypeDict[code[:2]]


#构建赤道仪需要重锤默认数量的字典
DefaultPPmess:dict[str,int] = dict()
for data in jsonDict.values():
	if "new_package" in data and data["new_package"]["PP_judge"]:
		PP_data = data["PP_information"] if "PP_information" in data else {"default_PPmess":10}
		default_PPmess = PP_data["default_PPmess"] if "default_PPmess" in PP_data else 10
		DefaultPPmess[data["code"]] = default_PPmess


#pushdata = {"type":"例观", "place":"静园草坪","time":"1919年8月10日11时45分14秒" ,"person":"", "notes":""}
#pk = {"Name":str, "Warn":list[str], "Lack":list[str],"Inside":list[str], "Outside":list[str], "IsQZ":bool, "TJPairWarning":Union[str,bool]}

#pkdata = {"code":str, "name":str, "inside":list[str]}


#=========导出json=============

def WriteLog(pkdata:list[dict[str,Union[str,bool,list[str]]]], pushdata:dict[str,str]):
	"导出出车json文件"
	#记录伪器材的数目
	CurrentCode_Tree = 1
	CurrentCode_Full = 1
	#最后导入json的出车列表
	pklist:list[dict[str,Union[str,list[str]]]] = list()
	Simplifiedpkdata:list[dict[str,Union[str,list[str]]]] = list()
	#开始写入器材包记录，有三种情况
	#如果该包是由于分类产生的，则直接列入根目录不分类（可能会加些自定义设置去调节）。
	#如果该包是由于自定义器组产生的，则代码为FakeQZ
	#否则代码就是QZ
	for pk in pkdata:
		name:str = pk["Name"]
		if not pk["IsQZ"]:
			code = ""
		elif name in QZName:
			code = QZName[name]
		else:
			code = f"FakeQZ{CurrentCode_Tree}"
			CurrentCode_Tree += 1
		pklist.append({"code":code, "name":name, "inside":pk["Inside"]})
	
	for pk in pkdata:
		name:str = pk["Name"]
		if name in QZName:
			code = QZName[name]
		else:
			code = f"FakeQZ{CurrentCode_Full}"
			CurrentCode_Full += 1
		Simplifiedpkdata.append({"code":code, "name":name, "inside":pk["Inside"]})

	#最后存入的字典
	DATA = {"version":Config.SaveRule, "pkdata":Simplifiedpkdata,"treedata":pklist,"pushdata":pushdata, "other":{"currentcodetree":CurrentCode_Tree,"currentcodefull":CurrentCode_Full}}
	Path = './Log/'+str(int(time.time()))+'.json'

	with open(Path,'w',encoding='utf8') as Log:
		Log.write(json.dumps(DATA, sort_keys=False, indent=4, separators=(',', ': ')))
	
	return DATA


#=========导出缓存json=============

def WriteCurrentLog(treedata:dict[str,dict[str,Union[str,list[str]]]], pushdata:dict[str,str], CurrentCode:int):
	"导出缓存的json文件"

	#获取文件路径
	Path = filedialog.asksaveasfilename(title='暂存出车记录',
							defaultextension=".json",
							initialfile=str("%d年%d月%d日%d点%d分"%time.localtime(time.time())[:5]),
							initialdir ='./Temporary',
							filetypes=[('json','*.json'),('All Files','*')]
							)

	if not len(Path):
		return

	#器材列表
	treelist:list[dict[str,Union[str,list[str]]]] = list()
	for code in treedata:
		data = treedata[code]
		treelist.append({"code":code, "name":data["name"], "inside":data["inside"]})
	
	#添加时间
	pushdata["time"] = "%d年%d月%d日%d点%d分"%time.localtime(time.time())[:5]

	DATA = {"version":Config.SaveRule, "pkdata":treelist,"treedata":treelist,"pushdata":pushdata,"other":{"currentcodetree":CurrentCode,"currentcodefull":CurrentCode}}

	with open(Path,'w',encoding='utf8') as Log:
		Log.write(json.dumps(DATA, sort_keys=False, indent=4, separators=(',', ': ')))


#=========导入json=============


def ReadLog(path:str)-> Union[dict[str,Union[str,list[dict[str,Union[str,list[str]]]],dict[str,str],dict[str,int]]],bool]:
	"导入出车文件或临时文件"
	#检验文件是否存在
	if not os.path.exists(path):
		return False
	
	#读取文件
	with open(path,'r',encoding='utf8') as logfile:
		log:dict = json.loads(logfile.read())
	
	if set(log) == {"version","pkdata","pushdata","treedata","other"} and (log["version"] == Config.SaveRule or Config.EnableOldLogs):
		return log
	else:
		return False

#WriteLog([],{"type":"例观", "place":"静园草坪","time":"1919年8月10日11时45分14秒" ,"person":"", "notes":""},True)


