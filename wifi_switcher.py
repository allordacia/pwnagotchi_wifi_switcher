import os
import logging
import pwnagotchi
import pwnagotchi.plugins as plugins

CONFIG_PATH = "/boot/config.txt"


class external_wifi(plugins.Plugin):
    __author__ = "Allordacia"
    __version__ = "0.0.5"
    __license__ = "GPL3"
    __description__ = "Switch between external and internal wifi on the fly."

    def __init__(self):
        self.ready = False
        self.config = None
        self.extAnt = None

    def on_loaded(self):
        if 'use-external-wifi' not in self.options:
            self.options['use-external-wifi'] = False
        if 'external_iface' not in self.options:
            self.options['external_iface'] = 'wlan1'
        if 'internal_iface' not in self.options:
            self.options['internal_iface'] = 'mon0'
        if 'last_iface' not in self.options:
            self.options['last_iface'] = 'mon0'

        logging.info("[external_wifi] plugin loaded")
        self.extAnt = self.options['use-external-wifi']

    def on_config_changed(self, config):
        self.config = config
        self.ready = True
        
        logging.info(self.extAnt)
        
        # get a list of all the available wifi interfaces
        lst = os.listdir('/sys/class/net')
        logging.info(lst)

        # check if the value of self.options['external_iface'] exists in the lst
        if self.options['external_iface'] in lst:
            logging.info("External wifi interface found")
        else:
            logging.info("External wifi interface not found")
            self.options['use-external-wifi'] = False
            self.extAnt = False

        if os.path.exists("/root/brain.nn") and os.path.exists("/root/brain.json"):
            logging.info("Brain files found")
            os.system("sudo cp /root/brain.nn /root/brain.nn." + self.options['last_iface'])
            os.system("sudo cp /root/brain.json /root/brain.json." + self.options['last_iface'])
            os.system("sudo rm /root/brain.nn")
            os.system("sudo rm /root/brain.json")

        if self.extAnt:
            if os.path.exists("/root/brain.nn." + self.options['external_iface']) and os.path.exists("/root/brain.json." + self.options['external_iface']):
                os.system("sudo cp /root/brain.nn." + self.options['external_iface'] + " /root/brain.nn")
                os.system("sudo cp /root/brain.json." + self.options['external_iface'] + " /root/brain.json")
            else:
                logging.info("External brain files for this interface were not found. New ones will be created")

            self.options['last_iface'] = self.options['external_iface']
            self.update_config(True)
        else:
            if os.path.exists("/root/brain.nn." + self.options['internal_iface']) and os.path.exists("/root/brain.json." + self.options['internal_iface']):
                os.system("sudo cp /root/brain.nn." + self.options['internal_iface'] + " /root/brain.nn")
                os.system("sudo cp /root/brain.json." + self.options['internal_iface'] + " /root/brain.json")
            else:
                logging.info("Internal brain files not found")
                # delete the current brain files so new ones can be created
                os.system("sudo rm /root/brain.nn")
                os.system("sudo rm /root/brain.json")

            self.options['last_iface'] = self.options['internal_iface']    
            self.update_config(False)        

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
    
    # def switch_wifi_mode(self, enable_wifi=True):
    #     #  Create backups for /root/brain.nn and /root/brain.json files based on the enable_wifi flag
    #     if os.path.exists("/root/brain.nn") and os.path.exists("/root/brain.json"):
    #         if enable_wifi:
    #             if not os.path.exists("/root/brain.nn.external") and not os.path.exists("/root/brain.json.external"):
    #                 os.system("sudo cp /root/brain.nn /root/brain.nn.internal")
    #                 os.system("sudo cp /root/brain.json /root/brain.json.internal")
    #                 os.system("sudo rm /root/brain.nn")
    #                 os.system("sudo rm /root/brain.json")
    #             # check if the external brain files exist and copy them to the root directory
    #             else: 
    #                 os.system("sudo cp /root/brain.nn /root/brain.nn.internal")
    #                 os.system("sudo cp /root/brain.json /root/brain.json.internal")
    #                 os.system("sudo cp /root/brain.nn.external /root/brain.nn")
    #                 os.system("sudo cp /root/brain.json.external /root/brain.json")

    #         else:
    #             if not os.path.exists("/root/brain.nn.internal") and not os.path.exists("/root/brain.json.internal"):
    #                 os.system("sudo cp /root/brain.nn /root/brain.nn.external")
    #                 os.system("sudo cp /root/brain.json /root/brain.json.external")
    #                 os.system("sudo rm /root/brain.nn")
    #                 os.system("sudo rm /root/brain.json")
    #             # check if the x brain files exist and copy them to the root directory
    #             else: 
    #                 os.system("sudo cp /root/brain.nn /root/brain.nn.external")
    #                 os.system("sudo cp /root/brain.json /root/brain.json.external")
    #                 os.system("sudo cp /root/brain.nn.internal /root/brain.nn")
    #                 os.system("sudo cp /root/brain.json.internal /root/brain.json")    

    #     # Update the config file to enable/disable internal Wi-Fi and dwc2
    #     self.update_config(enable_wifi)   

    # switch_wifi_mode(extAnt)