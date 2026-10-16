import time
import os
import pyperclip
from pywinauto.keyboard import send_keys

def _parse_and_compare(lines, key_name, ref_matrix):

    for raw_line in lines:
        line = raw_line.strip()

        if line.startswith(key_name):

            parts = line.split("=")
            if len(parts) < 2:
                return False

            rhs = parts[1].strip()

            rhs = rhs.replace("[", "").replace("]", "")

            try:
                parsed_vec = [float(tok.strip()) for tok in rhs.split(",") if tok.strip()]
            except ValueError:
                parsed_vec = []

            if not parsed_vec:
                return False
            
            return parsed_vec != [float(v) for v in ref_matrix]

    return False

def _parse_and_compare_str(lines, key_name, expected_value):

    for raw_line in lines:
        line = raw_line.strip()

        if line.startswith(key_name):

            parts = line.split("=")
            if len(parts) < 2:
                return False

            rhs = parts[1].strip()

            rhs = rhs.replace('"', "").strip()

            return rhs == expected_value

    return False

def check_calibration_factors(file_path, device_sn, hw_num, firmware_version, device_name, ref_matrix_acc, ref_matrix_gyro):    
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError as e:
        raise IOError(f"check_calibration_factors: Cannot open file: {file_path}") from e

    device_sn_match = _parse_and_compare_str(lines, "DeviceSN", device_sn)
    hw_match = _parse_and_compare_str(lines, "HardwareVersion", hw_num)
    firmware_version_match = _parse_and_compare_str(lines, "FirmwareVersion", firmware_version)
    device_name_match = _parse_and_compare_str(lines, "DeviceName", device_name)

    acc_is_calibrated = _parse_and_compare(lines, "MiscCalibAccFac", ref_matrix_acc)
    gyro_is_calibrated = _parse_and_compare(lines, "MiscCalibGyroFac", ref_matrix_gyro)

    calib_ctrl_success = (
        device_sn_match
        and hw_match
        and firmware_version_match
        and device_name_match
        and acc_is_calibrated
        and gyro_is_calibrated
    )

    return {
        "device_sn_match": device_sn_match,
        "hw_match": hw_match,
        "firmware_version_match": firmware_version_match,
        "device_name_match": device_name_match,
        "acc_is_calibrated": acc_is_calibrated,
        "gyro_is_calibrated": gyro_is_calibrated,
        "calib_ctrl_success": calib_ctrl_success,
    }

def KalibrasyonKontrolTesti(dlg, base_path, device_sn, hw_num, firmware_version, device_name, ref_matrix_acc, ref_matrix_gyro,  kalibrasyon_kontrol_folder):

    time.sleep(5)
    dlg.child_window(title="Settings", control_type="Button").click_input()
    time.sleep(5)
    send_keys("^+h")
    dlg.child_window(title="Copy to Clipboard", control_type="Pane").click_input()
    time.sleep(5)
    send_keys("%{F4}")

    target_folder = os.path.join(base_path, device_sn, kalibrasyon_kontrol_folder)

    config_path = os.path.join(target_folder, "config.txt")
    clipboard_content = pyperclip.paste()

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(clipboard_content)

    results = check_calibration_factors(config_path, device_sn, hw_num, firmware_version, device_name, ref_matrix_acc, ref_matrix_gyro)

    return results