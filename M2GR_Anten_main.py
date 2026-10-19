import os
import sys
import time
import serial.tools.list_ports

from types import SimpleNamespace
from pywinauto.keyboard import send_keys
from pywinauto.application import Application
import general_functions as fnc

def launch_arview(path):
    app = Application(backend="uia").start(path)
    dlg = app.window(auto_id="FormMain", control_type="Window")
    dlg.wait("visible ready", timeout=60)
    return dlg

def find_limit_file(pn_dvc, file_path):

    limit_file_path = os.path.join(file_path, "Limit Dosyaları")
    limit_file_path = os.path.join(limit_file_path, f"{pn_dvc}_limitdegerleri_v00.txt")
    m2gr_limitdegerleri_v00 = {}

    with open(limit_file_path, "r", encoding="utf-8") as file:
        exec(file.read(), {}, m2gr_limitdegerleri_v00) 

    return m2gr_limitdegerleri_v00

def M2GR_Anten_main(dlg, pn_dvc, base_path):

    limit_data = find_limit_file(pn_dvc, base_path)
    limits = SimpleNamespace(**limit_data)

    print("Anten takınız")

    anten_input = input("Sisteme anten takıldı mı?(y/n)")

    if anten_input == 'y':
        print("yes")
    else:
        print(":()")
    
    dlg = launch_arview(limits.arview_path) 
        
    ports = list(serial.tools.list_ports.comports())
        
    target_standard = fnc.find_port("Standard", ports)
    
    if not fnc.try_connect(dlg, target_standard, "Standard"):
        sys.exit("!!! Can't Connect to the Device !!!")