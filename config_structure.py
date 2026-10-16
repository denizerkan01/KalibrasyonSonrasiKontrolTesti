import time
from pywinauto.keyboard import send_keys


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
