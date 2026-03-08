import os

# Ensure all "./Appdata" and "./Resource" relative paths resolve from NewStart.
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from UI_beta import UI_beta

def mainbeta():
	UI =  UI_beta()
	UI.mainloop()

if __name__ == "__main__":
	mainbeta()
