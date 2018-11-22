# *-* coding: utf-8 *-8
#pylint: disable=E0611
from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem,QApplication,QMainWindow,QPushButton,QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5 import uic,QtCore
import requests
import sys
import os
import magic
import shutil
import configparser
import subprocess
import platform
import traceback
try:
    import ujson as json
except ImportError:
    import json

ROOT=os.path.dirname(__file__)
if ROOT:
    os.chdir(ROOT)
PYTHON="\""+os.path.join(ROOT,"python/python.exe")+"\""
PIP=PYTHON+" -m pip"

if not os.path.exists(os.path.join(ROOT,"downloads")):
    os.mkdir(os.path.join(ROOT,"downloads"))
if not os.path.exists(os.path.join(ROOT,"index")):
    os.mkdir(os.path.join(ROOT,"index"))
if not os.path.exists(os.path.join(ROOT,"repos")):
    os.mkdir(os.path.join(ROOT,"repos"))

parser=configparser.ConfigParser()

def extract(file,path="."):
    mime=magic.from_file(file,mime=True).split("/")[-1]
    if mime == "x-gzip":
        mime="gztar"
    shutil.unpack_archive(file,path,mime)

def compress(path,file):
    ext=file.split(".")[1]
    file=file.split(".")[0]
    if ext == "tar.gz":
        ext="gztar"
    shutil.make_archive(file,ext,path)

if len(sys.argv) >= 2:
    if sys.argv[1] == "compress":
        folder=sys.argv[2]
        f=sys.argv[3]
        compress(folder,f)
    if sys.argv[1] == "extract":
        f=sys.argv[2]
        folder=sys.argv[3]
        extract(f,folder)
    sys.exit(0)

app = QApplication(sys.argv)
window=uic.loadUi(os.path.join(ROOT,"mainwindow.ui"))

class CacheStorage:
    def __init__(self,cache_dir):
        self.cache_dir=cache_dir
        self.data={}
        self.load_cache()
    
    def load_cache(self):
        try:
            with open(os.path.join(self.cache_dir,"cache.json")) as f:
                self.data=json.loads(f.read().replace("\'","\""))
        except:
            return

    def save_cache(self,data):
        data=str(data)
        with open(os.path.join(self.cache_dir,"cache.json"),"w") as f:
            f.write(data)

    def exists(self):
        return os.path.exists(os.path.join(self.cache_dir,"cache.json"))
    
cache=CacheStorage(os.path.join(ROOT,"index"))
window.ls.setColumnCount(5)
window.ls.setEditTriggers(QTableWidget.NoEditTriggers)
window.ls.setHorizontalHeaderLabels(["Select","Name","Description","Versions","Status"])
window.ls.verticalHeader().setVisible(False)

def download(name,version,system):
    ext="zip" if system == "Windows" else "tar.gz"
    s=name+"/"+version+"/"+name+"-"+system+"."+ext
    with open(os.path.join(ROOT,"downloads/"+name+"-"+version+"-"+system+"."+ext),"wb") as f:
        f.write(requests.get("https://download.mrnaif.tk/repos/"+s).content)
    extract(os.path.join(ROOT,"downloads/"+name+"-"+version+"-"+system+"."+ext),os.path.join(ROOT,"repos/"+name))
    install(name)

def run(name):
    parser.read_file(open(os.path.join(ROOT,"repos/"+name+"/config.cfg")))
    e=parser.get("exec","main",fallback="")
    n=parser.get("app","friendlyname",fallback=name)
    c=parser.get("app","company",fallback="Unknown company")
    process=subprocess.Popen(PYTHON.replace("python.exe","pythonw.exe")+" \""+os.path.join(ROOT,"repos/"+name+"/"+e)+"\"",stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    out,err=process.communicate()
    info(n+" from company "+c+" executed succesfully! See output in details.","Exec info",details="Ran:\n"+n+" from company "+c+"\nOutput:\n"+out+"\nErrors:\n"+err)

def install(name):
    parser.read_file(open(os.path.join(ROOT,"repos/"+name+"/config.cfg")))
    reqs=parser.get("install","requirements",fallback="")
    for i in reqs.split():
        subprocess.getstatusoutput(PIP+" install -U "+i)

def update_data(w):
    if cache.exists():
        cache.load_cache()
        data=cache.data
    try:
        data=requests.get("https://api.mrnaif.tk/repos").json()["data"]
        cache.save_cache(data)
    except:
        print(sys.exc_info())
        pass
    try:
        data
    except:
        data=[]
    update_rows(w,data)
    
def update_rows(w,data):
    repos=get_installed_repos()
    w.setRowCount(len(data))
    for i in range(0,len(data)):
        chkBoxItem = QTableWidgetItem(str(i+1))
        chkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        chkBoxItem.setCheckState(QtCore.Qt.Unchecked)
        w.setItem(i,0,chkBoxItem)
        w.setItem(i,1, QTableWidgetItem(data[i]["name"]))
        w.setItem(i,2, QTableWidgetItem(data[i]["description"]))
        w.setItem(i,3, QTableWidgetItem(str(data[i]["versions"])))
        if data[i]["name"] not in repos:
            w.setItem(i,4, QTableWidgetItem("Not installed"))
        else:
            w.setItem(i,4, QTableWidgetItem("Installed"))

def get_installed_repos():
    return os.listdir(os.path.join(ROOT,"repos"))

update_data(window.ls)

icon = QIcon(os.path.join(ROOT,"qt.png"))
app.setWindowIcon(icon)
window.show()

def info(text,title,info=None,details=None):
    msg = QMessageBox(window)
    msg.setIcon(QMessageBox.Information)
    msg.setText(text)
    msg.setWindowTitle(title)
    if info:
        msg.setInformativeText(info)
    if details:
        msg.setDetailedText(details)
    msg.exec_()

def download_bunch(w):
    repos=get_installed_repos()
    for i in range(w.rowCount()):
        if w.item(i,0).checkState() == QtCore.Qt.Checked:
            name=w.item(i,1).text()
            version=eval(w.item(i,3).text())[-1]
            system=platform.system()
            if name not in repos:
                download(name,version,system)
    update_data(window.ls)

def run_bunch(w):
    repos=get_installed_repos()
    for i in range(w.rowCount()):
        if w.item(i,0).checkState() == QtCore.Qt.Checked:
            name=w.item(i,1).text()
            if name in repos:
                run(name)

window.actionabout.triggered.connect(lambda:info("Python hub v1.0 © Naif Studios","About Python hub","Python hub allows you to install and use lots of Python apps in one click."))
window.actionRun.triggered.connect(lambda:run_bunch(window.ls))
window.actionDownload.triggered.connect(lambda:download_bunch(window.ls))
app.exec_()
