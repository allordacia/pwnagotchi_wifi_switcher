import os
import logging
import pwnagotchi
import pwnagotchi.plugins as plugins

CONFIG_PATH = "/boot/config.txt"
extAnt = False

class external_wifi(plugins.Plugin):
    __author__ = "Allordacia"
    __version__ = "0.0.1"
    __license__ = "GPL3"
    __description__ = "Switch between external and internal wifi on the fly."

    def __init__(self):
        self.ready = False

    def on_loaded(self):
        if 'use-external-wifi' not in self.options:
            self.options['use-external-wifi'] = False
        if 'external_iface' not in self.options:
            self.options['external_iface'] = 'usb0'
        logging.info("[external_wifi] plugin loaded")
    
    def on_config_changed(self, config):
        self.config = config
        self.ready = True
        extAnt = self.options['use-external-wifi']
        logging.info(extAnt)
        
        # get a list of all the available wifi interfaces
        lst = os.listdir('/sys/class/net')
        logging.info(lst)

        # check if the value of self.options['external_iface'] exists in the lst
        if self.options['external_iface'] in lst:
            logging.info("External wifi interface found")
        else:
            logging.info("External wifi interface not found")
            self.options['use-external-wifi'] = False

    def update_config(self, enable_wifi=True):
        try:
            with open(CONFIG_PATH, 'r') as file:
                lines = file.readlines()

            # Modify the lines based on the enable_wifi flag
            new_lines = []
            for line in lines:
                if 'dtoverlay=disable-wifi' in line:
                    if enable_wifi:
                        # Uncomment the line to disable internal Wi-Fi (external adapter in use)
                        new_lines.append(line.lstrip('#').strip() + '\n')
                    else:
                        # Comment the line to enable internal Wi-Fi
                        if not line.lstrip().startswith('#'):  # Check if it's not already commented
                            new_lines.append('#' + line.strip() + '\n')
                        else:
                            # Ensure the line is only commented with one leading #
                            new_lines.append('#' + line.lstrip('#').strip() + '\n')

                elif 'dtoverlay=dwc2' in line:
                    if enable_wifi:
                        # Comment the line to disable dwc2 (since external Wi-Fi is used)
                        if not line.lstrip().startswith('#'):
                            new_lines.append('#' + line.strip() + '\n')
                        else:
                            # Ensure the line is commented with one leading #
                            new_lines.append('#' + line.lstrip('#').strip() + '\n')
                    else:
                        # Uncomment the line to enable dwc2 (since internal Wi-Fi is used)
                        new_lines.append(line.lstrip('#').strip() + '\n')
                else:
                    new_lines.append(line)

            # Write the modified config back to the file
            with open(CONFIG_PATH, 'w') as file:
                file.writelines(new_lines)

            logging.info("Config updated successfully.")
            
        except Exception as e:
            logging.info(f"Error modifying config file: {e}")
    
    def switch_wifi_mode(self, enable_wifi=True):
        #  Create backups for /root/brain.nn and /root/brain.json files based on the enable_wifi flag
        if os.path.exists("/root/brain.nn") and os.path.exists("/root/brain.json"):
            if enable_wifi:
                if not os.path.exists("/root/brain.nn.external") and not os.path.exists("/root/brain.json.external"):
                    os.system("sudo cp /root/brain.nn /root/brain.nn.internal")
                    os.system("sudo cp /root/brain.json /root/brain.json.internal")
                    os.system("sudo rm /root/brain.nn")
                    os.system("sudo rm /root/brain.json")
                # check if the external brain files exist and copy them to the root directory
                else: 
                    os.system("sudo cp /root/brain.nn /root/brain.nn.internal")
                    os.system("sudo cp /root/brain.json /root/brain.json.internal")
                    os.system("sudo cp /root/brain.nn.external /root/brain.nn")
                    os.system("sudo cp /root/brain.json.external /root/brain.json")

            else:
                if not os.path.exists("/root/brain.nn.internal") and not os.path.exists("/root/brain.json.internal"):
                    os.system("sudo cp /root/brain.nn /root/brain.nn.external")
                    os.system("sudo cp /root/brain.json /root/brain.json.external")
                    os.system("sudo rm /root/brain.nn")
                    os.system("sudo rm /root/brain.json")
                # check if the x brain files exist and copy them to the root directory
                else: 
                    os.system("sudo cp /root/brain.nn /root/brain.nn.external")
                    os.system("sudo cp /root/brain.json /root/brain.json.external")
                    os.system("sudo cp /root/brain.nn.internal /root/brain.nn")
                    os.system("sudo cp /root/brain.json.internal /root/brain.json")    

        # Update the config file to enable/disable internal Wi-Fi and dwc2
        self.update_config(enable_wifi)   

    switch_wifi_mode(extAnt)