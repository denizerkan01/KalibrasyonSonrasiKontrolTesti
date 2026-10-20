import os
import sys
import time
import pyperclip
import serial.tools.list_ports

from pywinauto.keyboard import send_keys
from types import SimpleNamespace
from pywinauto.application import Application

import numpy as np
import general_functions as fnc
import Reset_Testi as Reset_Testi
import Role as Role
import config_structure as config_structure
import Magn_Sonuc as Magn_Sonuc

base_path = os.path.dirname(os.path.abspath(__file__))
path_arview = r"C:\Program Files\ArView\ArView.exe"

def check_magn_norm(pn_dvc, sensor_data, Min_Magn_X_Value, Max_Magn_X_Value, Min_Magn_Y_Value, Max_Magn_Y_Value, Min_Magn_Z_Value, Max_Magn_Z_Value):
    result = {
        "reset_success": False,       
        "MagnX_Success": False,
        "MagnY_Success": False,
        "MagnZ_Success": False,
        "MagnSuccess": False, 
        "Mean_MagnX": 0.0,
        "Mean_MagnY": 0.0,
        "Mean_MagnZ": 0.0,
            }

    check_time_0 = Reset_Testi.check_reset_test(pn_dvc, sensor_data)
        
    if not check_time_0.get("reset_success", False):
        print("Reset Testi: BAŞARISIZ!!! Magn Norm Testi Yapılamaz!")
        return result
            
    result["reset_success"] = True

    magnX = sensor_data.magnX
    magnY = sensor_data.magnY
    magnZ = sensor_data.magnZ

    result["Mean_MagnX"] = np.mean(magnX)
    result["Mean_MagnY"] = np.mean(magnY)
    result["Mean_MagnZ"] = np.mean(magnZ)
    

    if (Min_Magn_X_Value <= np.mean(magnX)  <= Max_Magn_X_Value):
        result["MagnX_Success"]= True
    else:
        result["MagnX_Success"]= False

    if (Min_Magn_Y_Value <= np.mean(magnY)  <= Max_Magn_Y_Value):
        result["MagnY_Success"]= True
    else:
        result["MagnY_Success"]= False

    if (Min_Magn_Z_Value <= np.mean(magnZ)  <= Max_Magn_Z_Value):
        result["MagnZ_Success"]= True
    else:
        result["MagnZ_Success"]= False

    result["MagnSuccess"] = result["MagnX_Success"] and result["MagnY_Success"] and result["MagnZ_Success"]
        

    return result

def Magn_Testi(dlg, pn_dvc, device_sn, base_path, sub_folder, sleep_time, Min_Magn_X_Value, Max_Magn_X_Value, Min_Magn_Y_Value, Max_Magn_Y_Value, Min_Magn_Z_Value, Max_Magn_Z_Value):

    fnc.navigate_to_folder(dlg, device_sn, base_path, sub_folder)
        
    time.sleep(1)
    print("Sistemi 1. Konuma Getirin")
    time.sleep(3)
    
    Role.Role()
    
    log_magn_folder = fnc.auto_start(dlg, device_sn, base_path, sub_folder, sleep_time)

    try:
        sensor_data_magn_norm = fnc.parse_log(log_magn_folder)
    except (FileNotFoundError, ValueError) as e:
        #print(f"Parse edilemedi: {e}")
        return None

    result_magn_norm = check_magn_norm(pn_dvc, sensor_data_magn_norm, Min_Magn_X_Value, Max_Magn_X_Value, Min_Magn_Y_Value, Max_Magn_Y_Value, Min_Magn_Z_Value, Max_Magn_Z_Value)

    return result_magn_norm

def find_limit_file(pn_dvc, file_path):

    limit_file_path = os.path.join(file_path, "Limit Dosyaları")
    limit_file_path = os.path.join(limit_file_path, f"{pn_dvc}_limitdegerleri_v00.txt")
    s3a_limitdegerleri_v00 = {}

    with open(limit_file_path, "r", encoding="utf-8") as file:
        exec(file.read(), {}, s3a_limitdegerleri_v00) 

    return s3a_limitdegerleri_v00

def find_limit_file_m2_gr(pn_dvc, file_path):

    limit_file_path_m2_gr = os.path.join(file_path, "Limit Dosyaları")
    limit_file_path_m2_gr = os.path.join(limit_file_path_m2_gr, f"{pn_dvc}_limitdegerleri_v00.txt")
    m2_gr_limitdegerleri_v00 = {}

    with open(limit_file_path_m2_gr, "r", encoding="utf-8") as file:
        exec(file.read(), {}, m2_gr_limitdegerleri_v00) 

    return m2_gr_limitdegerleri_v00

def launch_arview(path):
    app = Application(backend="uia").start(path)
    dlg = app.window(auto_id="FormMain", control_type="Window")
    dlg.wait("visible ready", timeout=60)
    return dlg

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

def Magn_main():

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

    uretim_folder_path = os.path.join(base_path, r"UretimSonrasiTesti")

    if pn_dvc == "M2GR051433A":
        example_folder_path = os.path.join(uretim_folder_path, r"M2GR")
        example_folder = os.path.join(example_folder_path, r"example_folder")
        sn_folder = os.path.join(example_folder_path, device_sn)
    
    elif pn_dvc == "S3A097190":
        example_folder_path = os.path.join(uretim_folder_path, r"S3A")
        example_folder = os.path.join(example_folder_path, r"example_folder")
        sn_folder = os.path.join(example_folder_path, device_sn)

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

    config_structure.config_structure_magn(dlg, limits.checkbox_states_magn)

    print("***Magn Testi Başladı***")

    magn_result = Magn_Testi(dlg, pn_dvc, device_sn, example_folder_path, limits.magn_norm_folder, limits.sleep_time_magn, limits.Min_Magn_X_Value, limits.Max_Magn_X_Value, limits.Min_Magn_Y_Value, limits.Max_Magn_Y_Value, limits.Min_Magn_Z_Value, limits.Max_Magn_Z_Value)
    print(magn_result)
    time.sleep(3)

    #dlg.child_window(title="Disconnect", control_type="Button").click_input()
    #time.sleep(1)
    #send_keys("%{F4}")

    if magn_result["MagnSuccess"] == True:
        print("Sisteme Config Atılıyor")

        time.sleep(2)
        dlg.child_window(title="Settings", control_type="Button").click_input()
        time.sleep(1)

    #dlg.print_control_identifiers(filename="tree.txt")

        dlg.child_window(title="Configure from File", control_type="Pane").click_input()

        limit_file_path = os.path.join(base_path, "Limit Dosyaları")

        send_keys("^l")            
        time.sleep(0.3)
        send_keys("^a{DEL}")       
        send_keys(limit_file_path, with_spaces=True)
        time.sleep(1)
        send_keys("{ENTER}")

        item = dlg.child_window(title="S310A-Config V1.0.txt", control_type="ListItem")
        item.click_input() 
        send_keys("{ENTER}")
        time.sleep(20)

        send_keys("{ENTER}")

        dlg.child_window(title="Save", control_type="Pane").click_input()
        time.sleep(5)
        send_keys("%{F4}")

        dlg.child_window(title="Settings", control_type="Button").click_input()
        time.sleep(5)
        send_keys("^+h")
        dlg.child_window(title="Copy to Clipboard", control_type="Pane").click_input()
        time.sleep(5)
        send_keys("%{F4}")

        config_file_path = os.path.join(base_path, "Config")

        config_path = os.path.join(config_file_path, f"{device_sn}.txt")

        clipboard_content = pyperclip.paste()
    
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(clipboard_content)




    else:
        print("Magn Testi: BAŞARISIZ")

    time.sleep(2)
    dlg.child_window(title="Disconnect", control_type="Button").click_input()
    time.sleep(1)
    send_keys("%{F4}")

    Magn_Sonuc.Magn_Sonuc(pn_dvc, device_sn, base_path, magn_result)


    

if __name__ == "__main__":
    Magn_main()
