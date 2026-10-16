import time
import math
import general_functions as fnc
import Reset_Testi as Reset_Testi
import Role as Role
import numpy as np

def check_calibration_test(sensor_data, pn_dvc, min_best_acc_norm_value, max_best_acc_norm_value, min_ok_acc_norm_value, max_ok_acc_norm_value):

    result = {
        "reset_success": False,
        "accNorm": False,         
        "accNormValue": 0.0,      
        "accNormStatus": "fail",  
        "AccCalibrationSuccess": False,
        "GyroCalibrationSuccess": False,
        "CalibrationSuccess": False,
        "gyro_acilis_success": False,
        "acc_norm_gyro_success": False,
    }

    check_time_0 = Reset_Testi.check_reset_test(pn_dvc, sensor_data)

    if not check_time_0.get("reset_success", False):
        return result

    result["reset_success"] = True

    acc_Norm = math.sqrt(
            sensor_data.accX[0] ** 2 + 
            sensor_data.accY[0] ** 2 + 
            sensor_data.accZ[0] ** 2
        )

    result["accNormValue"] = acc_Norm

    if min_best_acc_norm_value <= acc_Norm <= max_best_acc_norm_value:
        result["accNorm"] = True
        result["accNormStatus"] = "best"
    elif min_ok_acc_norm_value <= acc_Norm <= max_ok_acc_norm_value:
        result["accNorm"] = True
        result["accNormStatus"] = "noted"
    else:
        result["accNorm"] = False
        result["accNormStatus"] = "fail"

    result["AccCalibrationSuccess"] = result["accNorm"]
    result["CalibrationSuccess"] = result["AccCalibrationSuccess"] and result["reset_success"]

    if pn_dvc == "M2GR051433A":
        print("M2GR051433A kullanılıyor")
        result["gyro_acilis_success"] = check_time_0["gyro_zero"]
        result["acc_norm_gyro_success"] = result["CalibrationSuccess"] and result["gyro_acilis_success"]

    elif pn_dvc == "S3A097190":
        print("S3A097190 sistemi kullanılıyor.")

        zero_rows_mat = np.where(sensor_data.time == 0)[0]
        time_05_rows_mat = np.where(sensor_data.time == 0.5)[0]

        if time_05_rows_mat == 0:
            return result

        zero_rows = zero_rows_mat[0]
        time_05_rows = time_05_rows_mat[0]

        mean_gyroX = np.mean(sensor_data.gyroX[zero_rows:time_05_rows+1])
        mean_gyroY = np.mean(sensor_data.gyroY[zero_rows:time_05_rows+1])
        mean_gyroZ = np.mean(sensor_data.gyroZ[zero_rows:time_05_rows+1])

        if mean_gyroX <= 0.05 and mean_gyroY <= 0.05 and mean_gyroZ <= 0.05:
            result["gyro_acilis_success"] = True
            result["GyroCalibrationSuccess"] = True
        else:
            return result

        result["acc_norm_gyro_success"] = result["CalibrationSuccess"] and result["gyro_acilis_success"]

    return result

def test_calibration(dlg, device_sn, base_path, acc_acilis_successfull_needed, acilis_acc_folder, max_ok_acc_norm_value, min_ok_acc_norm_value, max_best_acc_norm_value, min_best_acc_norm_value, sleep_time, pn_dvc):

    all_calibration_results = []
    all_accNormStatus_results = []
    successful_runs = 0

    while successful_runs < acc_acilis_successfull_needed:

        time.sleep(5)
        current_attempt = successful_runs + 1
            
        Role.Role()
        
        log_acc_acilis = fnc.auto_start(dlg, device_sn, base_path, acilis_acc_folder, sleep_time)
    
        try:
            sensor_data_acc_acilis = fnc.parse_log(log_acc_acilis)
        except (FileNotFoundError, ValueError) as e:                       
            return None

        results_acc_acilis = Reset_Testi.check_reset_test(pn_dvc,sensor_data_acc_acilis)

        if results_acc_acilis is False:                                                                           
            continue   
        
        results_calib_test = check_calibration_test(sensor_data_acc_acilis, pn_dvc, min_best_acc_norm_value, max_best_acc_norm_value, min_ok_acc_norm_value, max_ok_acc_norm_value)
        
        if not results_calib_test.get("CalibrationSuccess", False):                    
            continue      
        else:
            all_calibration_results.append(results_calib_test)
            all_accNormStatus_results.append(results_calib_test["accNormStatus"])
            successful_runs += 1

    stored_values = [res.get("accNormValue", 0.0) for res in all_calibration_results]
         
    if stored_values:
        max_val = max(stored_values)
        min_val = min(stored_values)

    CalibrationSuccess = all(item['CalibrationSuccess'] for item in all_calibration_results)
    AccCalibrationSuccess = all(item['AccCalibrationSuccess'] for item in all_calibration_results)


    if pn_dvc == "M2GR051433A":
        gyro_acilis_success = all(item['gyro_acilis_success'] for item in all_calibration_results)
    elif pn_dvc == "S3A097190":
        GyroCalibrationSuccess = all(item['GyroCalibrationSuccess'] for item in all_calibration_results)

    if pn_dvc == "M2GR051433A":


        return {
        "CalibrationSuccess": CalibrationSuccess,                                           
        "gyro_acilis_success": gyro_acilis_success,
        "AccCalibrationSuccess": AccCalibrationSuccess,
        "all_calibration_results": all_calibration_results,
        "all_accNormStatus_results": all_accNormStatus_results,
        "max_acc_norm": max_val,
        "min_acc_norm": min_val,
        "stored_values": stored_values,
    }

    elif pn_dvc == "S3A097190":
        return {
            "CalibrationSuccess": CalibrationSuccess,
            "GyroCalibrationSuccess": GyroCalibrationSuccess,
            "gyro_acilis_success": GyroCalibrationSuccess, 
            "AccCalibrationSuccess": AccCalibrationSuccess,
            "all_calibration_results": all_calibration_results,
            "all_accNormStatus_results": all_accNormStatus_results,
            "max_acc_norm": max_val,
            "min_acc_norm": min_val,
            "stored_values": stored_values,
        }


def AccNormGyroAcilisTesti(dlg, device_sn, base_path, acc_acilis_folder, acc_acilis_successfull_needed, max_ok_acc_norm_value, min_ok_acc_norm_value, max_best_acc_norm_value, min_best_acc_norm_value, sleep_time, pn_dvc):
    
    acilis_folder_acc = fnc.navigate_to_folder(dlg, device_sn, base_path, acc_acilis_folder)
    return test_calibration(dlg, device_sn, base_path, acc_acilis_successfull_needed, acilis_folder_acc, max_ok_acc_norm_value, min_ok_acc_norm_value, max_best_acc_norm_value, min_best_acc_norm_value, sleep_time, pn_dvc)