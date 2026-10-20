import os
import shutil
import sys
import time
import pyperclip
import serial.tools.list_ports

from types import SimpleNamespace
from pywinauto.keyboard import send_keys
from pywinauto.application import Application

import general_functions as fnc
import M2GR_Anten_Testi as ant
import M2GR_RTK_Testi as rtk
import config_structure as config_structure
import Anten_Sonuc as Anten_Sonuc

base_path = os.path.dirname(os.path.abspath(__file__))
path_arview = r"C:\Program Files\ArView\ArView.exe"

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

def dvc_sn(device_folder):
    
    dlg = launch_arview(path_arview) 
    time.sleep(5)

    ports = list(serial.tools.list_ports.comports())
    
    target_standard = fnc.find_port("Standard", ports)

    if not fnc.try_connect(dlg, target_standard, "Standard"):
        print("GUI_INFO|custom|Sisteme bağlanılamamaktadır.")                                                      
        sys.exit("!!! Can't Connect to the Device !!!")

    dlg.child_window(title="Settings", control_type="Button").click_input()
    time.sleep(5)
    dlg.child_window(title="Copy to Clipboard", control_type="Pane").click_input()
    time.sleep(5)
    send_keys("%{F4}")
    dlg.child_window(title="Disconnect", control_type="Button").click_input()
    time.sleep(5)
    send_keys("%{F4}")

    devicesn_folder = os.path.join(base_path, device_folder)

    config_path = os.path.join(devicesn_folder, "config.txt")
    clipboard_content = pyperclip.paste()
    
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(clipboard_content)


    with open(config_path, 'r') as file:
        for line in file:
            if line.startswith('DeviceSN'):
                return line.split('=', 1)[1].strip().strip('"')
    return None

def dvc_pn(device_folder):
    dlg = launch_arview(path_arview) 
    time.sleep(5)

    ports = list(serial.tools.list_ports.comports())
    
    target_standard = fnc.find_port("Standard", ports)
    
    if not fnc.try_connect(dlg, target_standard, "Standard"):
        print("GUI_INFO|custom|Sisteme bağlanılamamaktadır.")                                                        
        sys.exit("!!! Can't Connect to the Device !!!")

    dlg.child_window(title="Settings", control_type="Button").click_input()
    time.sleep(5)
    dlg.child_window(title="Copy to Clipboard", control_type="Pane").click_input()
    time.sleep(5)
    send_keys("%{F4}")
    dlg.child_window(title="Disconnect", control_type="Button").click_input()
    time.sleep(5)
    send_keys("%{F4}")

    device_info_folder = os.path.join(base_path, device_folder)

    config_path = os.path.join(device_info_folder, "config.txt")
    clipboard_content = pyperclip.paste()
    
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(clipboard_content)

    with open(config_path, 'r') as file:
        for line in file:
            if line.startswith('DevicePN'):
                return line.split('=', 1)[1].strip().strip('"')
    return None


def M2GR_Anten_main():

    base_path = os.path.dirname(os.path.abspath(__file__))

    pn_dvc = input("Sistemin etiketinde bulunan Part Number (PN) giriniz:").strip()
    if not pn_dvc:
        sys.exit("PN boş bırakılamaz.")

    device_sn = input("Sistemin etiketinde bulunan Serial Number (SN) giriniz:").strip()
    if not device_sn or device_sn in (".", "..") or os.path.basename(device_sn) != device_sn:
        sys.exit("Geçerli bir cihaz SN değeri giriniz.")

    device_folder_name = "Device"
    
    sn_dvc = dvc_sn(device_folder_name)
    pn_dvc = dvc_pn(device_folder_name)
    print(f"GUI_DEVICE|pn_dvc|{pn_dvc}")
    print(f"GUI_DEVICE|sn_dvc|{sn_dvc}")
    
    if pn_dvc == pn_dvc:
        if device_sn == sn_dvc:
            print("SN ve PN doğru")                                                                                 
        elif device_sn != sn_dvc:                                                                    
            sys.exit("PN doğrudur. Sistemde yüklü olan ve etikette olan SN farklı")
    elif pn_dvc != pn_dvc:
        if device_sn == sn_dvc:                                                                     
            sys.exit("SN doğrudur. Sistemde yüklü olan ve etikette olan PN farklı")
        elif device_sn != sn_dvc:                                                                                  
            sys.exit("Sistemde yüklü olan ve etikette olan PN ve SN farklı")

    limit_data = find_limit_file(pn_dvc, base_path)
    limits = SimpleNamespace(**limit_data)

    print("Anten takınız")

    while True:
        anten_input = input("Sisteme anten takıldı mı?(y/n)").strip().lower()
        if anten_input in ("y", "n"):
            break
        print("Lütfen y (evet) veya n (hayır) giriniz.")

    if anten_input != "y":
        print("Anten takılmadığı için Anten/RTK testi başlatılmadı.")
        return

    m2gr_root = os.path.join(base_path, "UretimSonrasiTesti", "M2GR")
    example_folder = os.path.join(m2gr_root, "example_folder")
    device_folder = os.path.join(m2gr_root, device_sn)
    if not os.path.isdir(example_folder):
        sys.exit(f"Test şablon klasörü bulunamadı: {example_folder}")
    if not os.path.isdir(device_folder):
        shutil.copytree(example_folder, device_folder)
    
    dlg = launch_arview(limits.arview_path) 
        
    ports = list(serial.tools.list_ports.comports())
        
    target_standard = fnc.find_port("Standard", ports)
    if target_standard is None:
        sys.exit("Standard COM port bulunamadı.")

    if not fnc.try_connect(dlg, target_standard, "Standard"):
        print("GUI_CONNECTION|false")
        sys.exit("!!! Can't Connect to the Device !!!")
    print(f"GUI_PORT|standard|{target_standard}")
    print("GUI_CONNECTION|true")

    config_structure.config_structure_anten_rtk(dlg, limits.checkbox_states_anten_rtk)
    

    print("***Anten Testi Başladı***")
    antenna_result = ant.Anten_Testi(
        dlg,
        pn_dvc,
        device_sn,
        m2gr_root,
        limits.sleep_time_gps,
        limits.gps_testi_id,
        limits.gps_folder,
    )
    print("Anten Test Sonucu:", antenna_result)
    print("***Anten Testi TAMAMLANDI***")

    print("***RTK Testi Başladı***")
    rtk_result = rtk.M2GR_RTK_Testi(
        dlg,
        pn_dvc,
        device_sn,
        m2gr_root,
        getattr(limits, "rtk_folder", "RTK Testi"),
        limits.sleep_time_rtk,
        limits.low_rate_rtk_id,
    )
    print("RTK Test Sonucu:", rtk_result)
    print("***RTK Testi TAMAMLANDI***")

    time.sleep(1)
    send_keys("%{F4}")

    Anten_Sonuc.Anten_Sonuc(pn_dvc, device_sn, base_path, antenna_result, rtk_result)



if __name__ == "__main__":
    M2GR_Anten_main()
