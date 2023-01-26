# Domoticz PC321-TY Plugin Tuya (LAN access)

 - Read power clamp data from PC321-TY 3 phase power clamp. 
 - This plugin is for wifi version only, it is not compatible with PC321-Z-TY, which is a zigbee version.
 - Domoticz version must be at least 2022.1
 
 ## Installation
  - This plugin requires Python library tinytuya `sudo pip3 install tinytuya`
  - From the Domoticz plugins directory run `git clone https://github.com/nlovrens/PC321_TY_tuya_local.git`
  - Restart Domoticz
  
  ## Configuration
  - You will need to register and add a device to Tuya IoT Cloud [https://iot.tuya.com/]
  - After adding your device to Tuya Cloud, you can obtain access ID, access Secret and device ID.
  - Go to Domoticz Hardware Setup and add new `PC321-TY Plugin Tuya(local)` hardware
  - Device IP can be obtained from your local router/modem DHCP lease
  
  ### Update
  - Go in 'plugins/PC321_TY_tuya_local' directory
  - Run cmd 'git pull'
  
  ### How it works
  - On startup, plugin will connect to Tuya Cloud to obtain local device Key, which is needed to access the device on LAN.
  - After that, plugin establishes persistent connection to power clamp on LAN and power clamp pushes updated data as it changes.
