import subprocess,requests,os,sys
ROOT=os.getcwd()
PYTHON=os.path.join(ROOT,"python/python.exe")
if os.path.exists(os.path.join(ROOT,"python")):
    sys.exit(0)
name="python"
install_dir="python"
pip_pkgs=("PyQt5","requests","python-magic","python-magic-bin")
with open(os.path.join(ROOT,"Miniconda_Install.exe"),"wb") as f:
    f.write(requests.get("https://repo.continuum.io/miniconda/Miniconda3-latest-Windows-x86.exe").content)
subprocess.getstatusoutput("\""+os.path.join(ROOT,"Miniconda_Install.exe")+"\" /S /AddToPath=0 /InstallationType=JustMe /RegisterPython=0 /NoRegistry=1 /D="+os.path.join(ROOT,install_dir))
os.remove(os.path.join(ROOT,"Miniconda_Install.exe"))
subprocess.getstatusoutput("\""+PYTHON+"\" -m pip install "+" ".join(pip_pkgs))