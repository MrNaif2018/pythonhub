import subprocess,requests,os,sys
ROOT=os.getcwd()
PYTHON=os.path.join(ROOT,"winpython/python-3.7.1/python.exe")
if os.path.exists(os.path.join(ROOT,"winpython")):
    sys.exit(0)
install_dir="winpython"
pip_pkgs=("PyQt5","requests","python-magic","python-magic-bin")
with open(os.path.join(ROOT,"Winpython32-3.7.1.0Zero.exe"),"wb") as f:
    f.write(requests.get("https://github.com/winpython/winpython/releases/download/1.11.20181031/Winpython32-3.7.1.0Zero.exe").content)
subprocess.getstatusoutput("\""+os.path.join(ROOT,"Winpython32-3.7.1.0Zero.exe")+"\" /VERYSILENT /DIR=\""+os.path.join(ROOT,install_dir)+"\"")
os.remove(os.path.join(ROOT,"Winpython32-3.7.1.0Zero.exe"))
subprocess.getstatusoutput("\""+PYTHON+"\" -m pip install "+" ".join(pip_pkgs))