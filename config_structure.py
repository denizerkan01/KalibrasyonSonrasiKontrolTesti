import time
from pywinauto.keyboard import send_keys

def open_low_rate(dlg):

    dlg.child_window(title="Data Select", control_type="Button").click_input()
    dlg.child_window(title="Configure...", auto_id="btLowRateConfigure", control_type="Pane").click_input()
    dlg.child_window(title="Defaults", control_type="Pane").click_input()
    dlg.child_window(title="Save", control_type="Pane", found_index=0).click_input()
    time.sleep(5)
    send_keys("%{F4}")
    dlg.child_window(title="Save", control_type="Pane", found_index=0).click_input()


def open_data_select(dlg, checkbox_states):

    dlg.child_window(title="Data Select", control_type="Button").click_input()
    
    for name, desired in checkbox_states:
        checkbox = dlg.child_window(title=name, control_type="CheckBox")
        state = checkbox.get_toggle_state()
        if state != desired:
            checkbox.click_input()

    dlg.child_window(title="Save", control_type="Pane", found_index=0).click_input()


def config_structure_data_select(dlg, checkbox_states):
    open_data_select(dlg, checkbox_states)

def config_structure_kalibrasyon_kontrol(dlg, checkbox_states):
    open_data_select(dlg, checkbox_states)

def config_structure_reset(dlg, checkbox_states):
    open_data_select(dlg, checkbox_states)

def config_structure_acc_norm_gyro_acilis(dlg, checkbox_states):
    open_data_select(dlg, checkbox_states)

def config_structure_acc_dondurme(dlg, checkbox_states):
    open_data_select(dlg, checkbox_states)

def config_structure_euler(dlg, checkbox_states):
    open_data_select(dlg, checkbox_states)

def config_structure_gyroz(dlg, checkbox_states):
    open_data_select(dlg, checkbox_states)

def config_structure_anten_rtk(dlg, checkbox_states):
    open_data_select(dlg, checkbox_states)
    time.sleep(2)
    open_low_rate(dlg)

def config_structure_magn(dlg, checkbox_states):
    open_data_select(dlg, checkbox_states)
