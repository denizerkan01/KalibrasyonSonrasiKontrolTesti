import time
import numpy as np
import general_functions as fnc
import Reset_Testi as Reset_Testi
import Role as Role
from pywinauto.keyboard import send_keys
from pywinauto import mouse

def check_gyroz(pn_dvc, sensor_data):

    result = {
                "reset_success": False, 
                "YawDiff": 0.0,      
                "GyroZSucess": False, 
            }

    check_time_0 = Reset_Testi.check_reset_test(pn_dvc, sensor_data)
    
    if not check_time_0.get("reset_success", False):
        return result
        
    result["reset_success"] = True

    euler_data = np.degrees(sensor_data.eulerZ)

    first_euler = euler_data[0]
    last_euler = euler_data[-1]

    diff_first_last = abs(last_euler - first_euler)

    result["YawDiff"] = diff_first_last

    if diff_first_last > 0.3:
        result["GyroZSucess"] = False
    else:
        result["GyroZSucess"] = True

    return result

def GyroZTesti(dlg, device_sn, base_path, sub_folder, sleep_time_gyroz, pn_dvc, checkbox_states_target_meas_gyroz_testi, magn_config_0, checkbox_states_target_meas_gyroz_testi_ahrs_1, magn_config_1):

    if pn_dvc == "M2GR051433A":

        fnc.target_meas(dlg, checkbox_states_target_meas_gyroz_testi)

    elif pn_dvc == "S3A097190":

        dlg.child_window(title="Settings", control_type="Button").click_input()

        r = dlg.rectangle()
        mouse.scroll(coords=(r.mid_point().x, r.mid_point().y), wheel_dist=-5)  

        dlg.child_window(title="Magnetometer Calibration", control_type="ListItem").double_click_input()


        item = dlg.child_window(title="Magnetometer Calibration", control_type="ListItem")
        value = item.children()[1]        
        value.click_input()

        send_keys("^a{DEL}")

        config_0 = "[" + ",".join(str(x) for x in magn_config_0) + "]"

        send_keys(config_0, with_spaces=True)
        time.sleep(3)

        dlg.child_window(title="OK", auto_id="buttonOK", control_type="Pane").click_input()
        dlg.child_window(title="Save", auto_id="buttonSave", control_type="Pane").click_input()

        time.sleep(3)
        send_keys("%{F4}")

        time.sleep(2)

        dlg.child_window(title="Console", control_type="Button").click_input()
        
        time.sleep(3)
        
        dlg.child_window(title="Reset", control_type="Pane").click_input()

        
    time.sleep(1)
    print("Sistemi 1. Konuma Getirin")
    time.sleep(3)

    fnc.navigate_to_folder(dlg, device_sn, base_path, sub_folder)
    
    Role.Role()
                
    log_gyro_z_folder = fnc.auto_start(dlg, device_sn, base_path, sub_folder, sleep_time_gyroz)

    try:
        sensor_data_gyro_z = fnc.parse_log(log_gyro_z_folder)
    except (FileNotFoundError, ValueError) as e:
        return None
    
    result_gyroz = check_gyroz(pn_dvc, sensor_data_gyro_z)

    if pn_dvc == "M2GR051433A":
    
            fnc.target_meas(dlg, checkbox_states_target_meas_gyroz_testi_ahrs_1)

    elif pn_dvc == "S3A097190":
    
            dlg.child_window(title="Settings", control_type="Button").click_input()
    
            r = dlg.rectangle()
            mouse.scroll(coords=(r.mid_point().x, r.mid_point().y), wheel_dist=-5)  
    
            dlg.child_window(title="Magnetometer Calibration", control_type="ListItem").double_click_input()
    
    
            item = dlg.child_window(title="Magnetometer Calibration", control_type="ListItem")
            value = item.children()[1]        
            value.click_input()
    
            send_keys("^a{DEL}")
    
            config_0 = "[" + ",".join(str(x) for x in magn_config_1) + "]"
    
            send_keys(config_0, with_spaces=True)
            time.sleep(3)
    
            dlg.child_window(title="OK", auto_id="buttonOK", control_type="Pane").click_input()
            dlg.child_window(title="Save", auto_id="buttonSave", control_type="Pane").click_input()
    
            time.sleep(3)
            send_keys("%{F4}")
    
            time.sleep(2)
    
            dlg.child_window(title="Console", control_type="Button").click_input()
            
            time.sleep(3)
            
            dlg.child_window(title="Reset", control_type="Pane").click_input()



    return result_gyroz