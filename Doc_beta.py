import os
import shutil
from typing import Union, Callable
from DataReader import Check_Name

from typing import Union

BEGIN_DOC = r'''\documentclass{ctexart}
\usepackage{geometry}
\usepackage{float}
\usepackage{multirow}
\usepackage{longtable}
\usepackage{array}
\geometry{top=1.25in, bottom=1.25in, left=1in, right=1in}

\begin{document}
    \pagestyle{plain}
    \begin{center}
        \Large\textbf{器材使用记录表}
    \end{center}

'''



def gen_docx(equip_list:list[dict[str,Union[str,list[str]]]], check_dict:dict[str,bool], Push_Data:dict[str,str], MaxLine:int=30, MaxWidth:int=15) -> tuple[str]:
    "生成tex文档并返回文件路径"
    
    Type= Push_Data["type"]
    begin_time = Push_Data["begin"]
    end_time = Push_Data["end"]
    place = Push_Data["place"]
    person = Push_Data["person"]
    notes = Push_Data["notes"]
    
    file_name = "观测记录-%s-%s.tex"%(begin_time, place)
    file_dir = "./观测记录/收车记录/tex文档/观测记录-%s-%s/观测记录-%s-%s.tex"%(begin_time, place,begin_time, place)
    file_root = "./观测记录/收车记录/tex文档/观测记录-%s-%s"%(begin_time, place)
    if os.path.exists(file_root):
        for oldfile in os.listdir(file_root):
            os.remove(file_root+'/'+oldfile)
    else:
        os.makedirs(file_root)

    #开始写入LaTeX文档
    with open(file_dir, "w", encoding="utf-8") as f:
        f.write(BEGIN_DOC)
        f.write(f"活动类型：{Type}\n\n")
        f.write(f"活动地点：{place}\n\n")
        f.write(f"活动开始时间：{begin_time}\n\n")
        f.write(f"活动结束时间：{end_time}\n\n")
        f.write(f"器材负责人：{person}\n\n")
        
        #自动分页
        Index = 0
        DOC_list = [[]]
        for pack in equip_list:
            DOC_list[-1].append({"name":pack["name"],"inside":[]})
            for code in pack["inside"]:
                Index0 = len(Check_Name(code))//MaxWidth+ bool(len(Check_Name(code))%MaxWidth)
                if Index + Index0 > MaxLine:
                    DOC_list.append([{"name":pack["name"],"inside":[]}])
                    Index = 0
                    MaxLine = 35
                Index += Index0
                DOC_list[-1][-1]["inside"].append({"code":code,"name":Check_Name(code),"back":{True:"是",False:"否"}[check_dict[code]]})


        for Page in DOC_list:
            #每一页一张表
            f.write(r'''\begin{tabular}{|p{.2\textwidth}<{\centering}|p{.2\textwidth}<{\centering}|p{.3\textwidth}<{\centering}|p{.2\textwidth}<{\centering}|}
\hline
& 器材编号 & 器材名称 & 是否已归还 \\ \hline
''')
            #表里的每一组
            for pack in filter(lambda pk:len(pk["inside"])>0 ,Page):
                equip_num = len(pack["inside"])
                if not equip_num:
                    continue
                f.write("\\multirow{%d}{*}{%s}"%(equip_num,pack["name"]))
                f.write("\\cline{2-4}\n".join(map(lambda item: "& %s & %s & %s \\\\ "%(item["code"],item["name"],item["back"]), pack["inside"])))
                f.write(" \\hline\n")

            #结束表格换页
            if Page is DOC_list[-1]:
                f.write("\\end{tabular}\n")
            else:
                f.write("\\end{tabular}\n\\newpage\n")

        f.write("\\par 备注：%s\n\n"%notes)
        f.write("\\end{document}")
        #返回目录文件名
        return file_root, file_dir, file_name
        

def CompileDoc(file_root:str, file_dir:str, file_name:str):
    "编译文档并移动文件"
    os.system("xelatex -synctex=1 -interaction=nonstopmode -output-directory=%s %s"%(file_root,file_dir))
    pdf_dir = file_dir[:-4]+'.pdf'
    newpdf_dir = './观测记录/收车记录/'+file_name[:-4]+'.pdf'
    shutil.move(pdf_dir,newpdf_dir)
    os.system(f'start "" /max "{newpdf_dir}')

"""
旧代码，已废弃
if __name__ == "__main__":
    equip_list=[{"name":"第一组","CY001":"CEM70G","TJ001":"Dob12","ABC":"名字","ABC":"名字","ABC":"名字","ABC":"名字","ABC":"名字","ABC":"名字","ABC":"名字"},{"name":"第二组","CY002":"AVX","TJ003":"大黑","ABC":"名字","ABC":"名字","ABC":"名字","ABC":"名字","ABC":"名字","ABC":"名字"}]
    check_dict = {"CY001":True,"TJ001":True,"ABC":True,"CY002":True,"TJ003":True}
    file_root, file_dir, file_name = gen_docx(equip_list=equip_list,check_dict=check_dict, begin_time="这是时间", place="这是地点", person="负责人姓名", notes="备注备注备注备注备注")
    os.system("xelatex -synctex=1 -interaction=nonstopmode -output-directory=%s %s"%(file_root,file_dir))
    pdf_dir = file_dir[:-4]+'pdf'
    newpdf_dir = './观测记录/收车记录/'+file_name[:-4]+'.pdf'
    shutil.move(pdf_dir,newpdf_dir)
"""