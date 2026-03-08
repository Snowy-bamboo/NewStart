import json
from typing import Union


"""
当前版本默认config
{
    "Version":"3.0.2",
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

with open('./Appdata/config.json','r',encoding='utf8') as jsonfile:
	jsondata:dict[str,Union[str,int,float]] = json.loads(jsonfile.read())

class CONFIG:
	def __init__(self,config:dict[str,Union[str,int,float]]) -> None:
		self.Version:str =str(config["Version"])
		self.SaveRule:str = str(config["Data Save Rule"])
		self.EndableDisables:bool = bool(config["Display Disable Equipment"])
		self.TJ_MaxRate:float = float(config["TJ Maxmess Rate"])
		self.Detail_Alpha = bool(config["ImportDataDisplaySoltDetail_Alpha"])
		self.Detail_Beta = bool(config["ImportDataDisplaySoltDetail_Beta"])
		self.EnableOldLogs = bool(config["Enable Old Logs"])
		self.AutoCheckStepTwo = bool(config["AutoCheckStepTwo"])
		self.ConfigNeedPassword = bool(config["ConfigNeedPassword"])
		self.BetaPassword = str(config["Beta Password"])
		self.ConfigPassword = str(config["Config Password"])
	
	def SetConfig(self,config:dict[str,Union[str,bool,float]]):
		"更新设置并保存文件"
		self.__init__(config)
		self.UpdateConfigLog(config)
	
	def UpdateConfigLog(self,config:dict[str,Union[str,bool,float]]):
		"将更新后的配置存入文件"
		DATA:dict[str,Union[str,int,float]] = dict()
		for cfg in config:
			if isinstance(config[cfg],bool):
				DATA[cfg] = int(config[cfg])
			else:
				DATA[cfg] = config[cfg]
		with open('./Appdata/config.json','w',encoding='utf8') as Log:
			Log.write(json.dumps(DATA, sort_keys=False, indent=4, separators=(',', ': ')))


	def GetConfig(self)-> dict[str,Union[str,bool,float]]:
		"返回全部设置给UI"
		return {
    		"Version":self.Version,
			"Data Save Rule":self.SaveRule,
    		"Display Disable Equipment":self.EndableDisables,
    		"TJ Maxmess Rate":self.TJ_MaxRate,
    		"Enable Old Logs":self.EnableOldLogs,
			"ImportDataDisplaySoltDetail_Alpha":self.Detail_Alpha,
			"ImportDataDisplaySoltDetail_Beta":self.Detail_Beta,
			"AutoCheckStepTwo":self.AutoCheckStepTwo,
			"ConfigNeedPassword":self.ConfigNeedPassword,
			"Beta Password":self.BetaPassword,
			"Config Password":self.ConfigPassword
		}




	



Config = CONFIG(jsondata)

