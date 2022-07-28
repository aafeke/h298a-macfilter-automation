from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from os import getcwd
from sys import argv, exit
from time import sleep

# TODO: Reduce the log verbosity of Selenium.

# Expected arguments:
# [ <block> | <unblock> ] <device_1> <device_2> ... <device_n>   


args = argv[1:]

if(len(args) == 0 or ( args[0] != "block" and args[0] != "unblock" ) ):
    # Arg check       
    print("Bad operation argument.\n Press any key to exit.")
    input()
    exit()



# -- Global Variables --

# Edit your attriutes here.
path =  getcwd() + "/msedgedriver.exe"
addr = "http://192.168.1.1"

opt = webdriver.EdgeOptions()
opt.add_argument('headless') # Comment this line out to debug.

driver = webdriver.ChromiumEdge(executable_path=path, options=opt)
driver.get(addr)

driver.implicitly_wait(5) # Based on the login bottleneck.

global_stall_time = 1.5   # Required after each filter action.
                          # This should be incremented depending on
                          # the signal quality thus server response time
                          # TLDR increase it by 0.5 in case of error.

map ={
    "comp-wifi": ["7D", "1"],
    "comp2-wifi": ["A9", "14"]
} 
# First element of the list is last 2 chars of the 
# target device's MAC address. Second element represents
# device's entry order in the "MAC Filter" tab, starting from 0.
# The number is also used to identify device's own 
# HTML elements for configuration, so we need that.

flag_operation = "" # block/unblock

credential_username = "admin"
credential_pass = "pass"

# -- End of Global Variables --


def filter(device):
    # By looking at the operation flag,
    # block or unblock the matching device in the global map.
    # Blocking is made by setting MAC's last 2 chars to 'FF'
    # Thus, unblocking is actually restoring the MAC's last 2 chars.
    # Hacky way, since H298A doesn't provide an on/off switch for each entry.
    # Note: you have to be using "White listing MAC filter"
    # otherwise it would work the other way around.

    if device not in map:
        print("\n[Error]: Device not found in the map!")
        return

    action = ActionChains(driver)

    element_device = driver.find_element(By.ID,
        str( "instName_MACFilter:" + map.get(device)[1] )
        )

    action.click(element_device)
    action.perform()

    hex_field_5 = driver.find_element(By.ID,
        str( "sub_SrcMacAddr5:" + map.get(device)[1] )
        )

    btn_apply = driver.find_element(By.ID,
        str( "Btn_apply_MACFilter:" + map.get(device)[1] )
        )

    hex_field_5.send_keys(Keys.CONTROL + "a")
    hex_field_5.send_keys(Keys.DELETE)

    if flag_operation == "block":
        hex_field_5.send_keys("FF")
    else:
        hex_field_5.send_keys( map.get(device)[0] )
    
    action.click(btn_apply)
    action.perform()

    sleep(global_stall_time)

    print(f"\n[Success]: Device {device} was {flag_operation}ed")

    return

def login():
    field_username = driver.find_element(By.ID, "Frm_Username")
    field_pass = driver.find_element(By.ID, "Frm_Password")

    field_username.send_keys(credential_username)
    field_pass.send_keys(credential_pass)

    driver.find_element(By.ID, "LoginId").click()

    return

def navigate_to_mac_filter():
    action = ActionChains(driver)

    tab_wan = driver.find_element(By.ID, "mmInternet")
    action.click(tab_wan)
    action.perform()

    menu_security = driver.find_element(By.ID, "smSecurity")
    action.click(menu_security)
    action.perform()

    tab_filter_crit = driver.find_element(By.ID, "ssmSecFilter")
    action.click(tab_filter_crit)
    action.perform()

    collapse_mac_filter = driver.find_element(By.ID, "MACFilterBar")
    action.click(collapse_mac_filter)
    action.perform()
    
    return

def main():

    global flag_operation, args

    flag_operation = args[0]
    args = args[1:]

    login()
    navigate_to_mac_filter()

    for device in args:
        filter(device)
    
    driver.close()
    input("Press any key to exit.")
    exit()


if __name__ == "__main__":
    main()
