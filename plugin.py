# Basic Python Plugin Example
#
# Author: nlovrens
#
"""
<plugin key="PC321_TY_tuya_local" name="PC321-TY Plugin Tuya(local)" author="nlovrens" version="1.0.0" externallink="https://github.com/nlovrens/PC321_TY_tuya_local/">
	<description>
		<h2>PC321-TY Plugin Tuya(local)</h2><br/>
		
		<h3>Features</h3>
		<ul style="list-style-type:square">
			<li>Displays current from all three phases and total current</li>
			<li>Displays voltage from all three phases</li>
			<li>Displays power (real-time and consumed) from all three phases and total power</li>
			<li>Displays power frequency</li>
			<li>Displays power clamp device temperature</li>
		</ul>
		<h3>Devices</h3>
		<ul style="list-style-type:square">
			<li>Current 3 Phase - Current from L1, L2 and L3</li>
			<li>Total Current - Total current from all phases</li>
			<li>Total Power - Total actual and consumed power from all phases</li>
			<li>Voltage L1 - Voltage of L1</li>
			<li>Voltage L2 - Voltage of L2</li>
			<li>Voltage L3 - Voltage of L3</li>
			<li>Power L1 - Actual and consumed power from L1</li>
			<li>Power L2 - Actual and consumed power from L2</li>
			<li>Power L3 - Actual and consumed power from L3</li>
			<li>Frequency - Power frequency</li>
			<li>Power Clamp Temp - Power clamp internal temperature</li>
		</ul>
		<h3>Configuration</h3>
		<ul style="list-style-type:square">
			<li>Enter your apiRegion, apiKey, apiSecret and deviceID.</li>
			<li>A deviceID can be found on your IOT account of Tuya.</li>
			<li>On start, plugin will connect to Tuya cloud to get local device key. After that all the data is pulled from the device locally.</li>
		</ul>	
	</description>
	<params>
		<param field="Mode1" label="apiRegion" width="150px" required="true" default="EU">
			<options>
				<option label="EU" value="eu" default="true" />
				<option label="US" value="us"/>
				<option label="CN" value="cn"/>
			</options>
		</param>
		<param field="Username" label="apiKey" width="300px" required="true" default=""/>
		<param field="Password" label="apiSecret" width="300px" required="true" default="" password="true"/>
		<param field="Mode2" label="DeviceID" width="300px" required="true" />
		<param field="Mode4" label="DeviceIP" width="300px" required="true" />
		<param field="Mode6" label="Debug" width="150px">
			<options>
				<option label="None" value="0"  default="true" />
				<option label="Python Only" value="2"/>
				<option label="Basic Debugging" value="62"/>
				<option label="Basic+Messages" value="126"/>
				<option label="Queue" value="128"/>
				<option label="Connections Only" value="16"/>
				<option label="Connections+Queue" value="144"/>
				<option label="All" value="-1"/>
			</options>
		</param>
	</params>
</plugin>
"""
import DomoticzEx as Domoticz
import tinytuya
import time
import threading
import queue


class BasePlugin:
	enabled = False
	def __init__(self):
		self.messageQueue = queue.Queue()
		self.TuyaThread = threading.Thread(name="TuyaThread", target=BasePlugin.handleMessage, args=(self,))
		return

	def handleMessage(self):
		try:
			while True:
				try:
					Message = self.messageQueue.get(block=False)
					if Message is None:
						Domoticz.Status("Exiting message handler")
						tuya.set_socketPersistent(False)
						time.sleep(2)
						self.messageQueue.task_done()
						break
				except queue.Empty:
					# See if any data is available
					data = tuya.receive()
					Domoticz.Debug('PC321-TY Payload: %r' % data)
					if data is not None:
						key_mgmt(data)
					Domoticz.Debug(" > Send Tuya Heartbeat Ping < ")
					payload = tuya.generate_payload(tinytuya.HEART_BEAT)
					tuya.send(payload)
					#self.messageQueue.task_done()
		except Exception as err:
			Domoticz.Error("handleMessage: "+str(err))
			
			
	
	def onStart(self):
		Domoticz.Heartbeat(30)
		global last_currA, last_currB, last_currC, last_curr
		global last_powerA, last_powerB, last_powerC, last_power
		global last_voltA, last_voltB, last_voltC
		global last_temp
		global last_freq
		global isConnected
		global localkey
		last_currA = 0
		last_currB = 0
		last_currC = 0
		last_curr = 0
		last_power = 0
		last_voltA = 0
		last_voltB = 0
		last_voltC = 0
		last_powerA = 0
		last_powerB = 0
		last_powerC = 0
		last_temp = 0
		last_freq = 0
		Domoticz.Status("PC321-TY plugin started")
		
		if Parameters["Mode6"] != "0":
			Domoticz.Debugging(int(Parameters["Mode6"]))
			#DumpConfigToLog()
		
		if createDevice('current', 1):
			Domoticz.Unit(Name='Current 3 Phase', DeviceID='current', Unit=1, Type=89, Subtype=1, Used=1).Create()
		if createDevice('currentAll', 2):
			Domoticz.Unit(Name='Total Current', DeviceID='currentAll', Unit=2, Type=243, Subtype=23, Used=1).Create()
		if createDevice('powerAll', 3):
			Domoticz.Unit(Name='Total Power', DeviceID='powerAll', Unit=3, Type=243, Subtype=29, Options={"EnergyMeterMode" : "1"}, Used=1).Create()
		if createDevice('voltageL1', 4):
			Domoticz.Unit(Name='Voltage L1', DeviceID='voltageL1', Unit=4, Type=243, Subtype=8, Used=1).Create()
		if createDevice('voltageL2', 5):
			Domoticz.Unit(Name='Voltage L2', DeviceID='voltageL2', Unit=5, Type=243, Subtype=8, Used=1).Create()
		if createDevice('voltageL3', 6):
			Domoticz.Unit(Name='Voltage L3', DeviceID='voltageL3', Unit=6, Type=243, Subtype=8, Used=1).Create()
		if createDevice('powerL1', 7):
			Domoticz.Unit(Name='Power L1', DeviceID='powerL1', Unit=7, Type=243, Subtype=29, Options={"EnergyMeterMode" : "0"}, Used=1).Create()
		if createDevice('powerL2', 8):
			Domoticz.Unit(Name='Power L2', DeviceID='powerL2', Unit=8, Type=243, Subtype=29, Options={"EnergyMeterMode" : "0"}, Used=1).Create()
		if createDevice('powerL3', 9):
			Domoticz.Unit(Name='Power L3', DeviceID='powerL3', Unit=9, Type=243, Subtype=29, Options={"EnergyMeterMode" : "0"}, Used=1).Create()
		if createDevice('temp', 10):
			Domoticz.Unit(Name='Power Clamp Temp', DeviceID='temp', Unit=10, Type=80, Subtype=5, Used=1).Create()	
		if createDevice('freq', 11):
			options = {}
			options['Custom'] = '1;Hz'
			Domoticz.Unit(Name='Frequency', DeviceID='freq', Unit=11, Type=243, Subtype=31, Options=options, Used=1).Create()
			
		localkey = get_key()
		if localkey != "":
			isConnected = self.localConnect()

						
	def localConnect(self):
		global tuya
		if localkey != "":
			Domoticz.Status("Connecting to device...")
			tuya = tinytuya.OutletDevice(Parameters['Mode2'], Parameters['Mode4'], localkey)
			tuya.set_version(3.3)
			tuya.set_socketPersistent(True)
			payload = tuya.generate_payload(tinytuya.DP_QUERY)
			tuya.send(payload)
			status = tuya.status()
			if status.get('Error') is not None:
				Domoticz.Error("PC321-TY Error: " + str(status.get('Error')))
				connected = False
			else:
				Domoticz.Debug('PC321-TY Status: %r' % status)
				if status is not None:
					Domoticz.Status("Connected successfully")
					connected = True
					key_mgmt(status)
					self.TuyaThread.start()
		return connected

		
	def onStop(self):
		Domoticz.Log("onStop called")
		# Not needed in an actual plugin
		for thread in threading.enumerate():
			if (thread.name != threading.current_thread().name):
				Domoticz.Log("'"+thread.name+"' is running, it must be shutdown otherwise Domoticz will abort on plugin exit.")
		
		if (threading.active_count() > 1):
			# signal queue thread to exit
			self.messageQueue.put(None)
			Domoticz.Log("Clearing message queue...")
			self.messageQueue.join()

		# Wait until queue thread has exited
		Domoticz.Log("Threads still active: "+str(threading.active_count())+", should be 1.")
		while (threading.active_count() > 1):
			for thread in threading.enumerate():
				if (thread.name != threading.current_thread().name):
					Domoticz.Log("'"+thread.name+"' is still running, waiting otherwise Domoticz will abort on plugin exit.")
			time.sleep(1.0)

	def onConnect(self, Connection, Status, Description):
		Domoticz.Log("onConnect called")

	def onMessage(self, Connection, Data):
		Domoticz.Log("onMessage called")

	def onCommand(self, DeviceID, Unit, Command, Level, Color):
		Domoticz.Log("onCommand called for Device " + str(DeviceID) + " Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

	def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
		Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

	def onDisconnect(self, Connection):
		Domoticz.Log("onDisconnect called")

	def onHeartbeat(self):
		global isConnected
		Domoticz.Debug("onHeartbeat called")
		if isConnected == False:
			isConnected = self.localConnect()

global _plugin
_plugin = BasePlugin()

def onStart():
	global _plugin
	_plugin.onStart()

def onStop():
	global _plugin
	_plugin.onStop()

def onConnect(Connection, Status, Description):
	global _plugin
	_plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
	global _plugin
	_plugin.onMessage(Connection, Data)

def onCommand(DeviceID, Unit, Command, Level, Color):
	global _plugin
	_plugin.onCommand(DeviceID, Unit, Command, Level, Color)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
	global _plugin
	_plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
	global _plugin
	_plugin.onDisconnect(Connection)

def onHeartbeat():
	global _plugin
	_plugin.onHeartbeat()


def get_key():
	localkey = ""
	try:
		Domoticz.Status('Connecting to Tuya cloud...')
		c = tinytuya.Cloud(
			apiRegion=Parameters['Mode1'], 
			apiKey=Parameters['Username'], 
			apiSecret=Parameters['Password'], 
			apiDeviceID=Parameters['Mode2'])
		devices = c.getdevices()
		i = 0
		for dev in devices:
			if devices[i]['id'] == Parameters['Mode2']:
				Domoticz.Status('Got PC321-TY local key: ' + devices[i]['key'])
				localkey = devices[i]['key']
			i=i+1
	except:
		Domoticz.Error('Error connecting to Tuya cloud, check credentials')
	return localkey


def key_mgmt(dic):
	dic = dic.get('dps','')
	global currA, currB, currC, curr
	global last_currA, last_currB, last_currC, last_curr
	global powerA, powerB, powerC, power
	global last_powerA, last_powerB, last_powerC, last_power
	global voltA, voltB, voltC
	global last_voltA, last_voltB, last_voltC
	global energyA, energyB, energyC, energy
	global temp, last_temp
	global freq, last_freq
	
	if dic.get('101') is not None:
		voltageA = dic.get('101', '0')
		voltA = float(voltageA) / 10
		voltA = round(voltA, 0)
	if dic.get('102') is not None:
		currentA = dic.get('102', '0')
		currA = float(currentA) / 1000
		currA = round(currA, 1)
	if dic.get('103') is not None:
		activepowerA = dic.get('103', '0')
		powerA = float(activepowerA)
	if dic.get('104') is not None:
		powerfactorA = dic.get('104', '0')
	if dic.get('106') is not None:
		energyAstr = dic.get('106', '0')
		energyA = float(energyAstr) * 10
	if dic.get('111') is not None:
		voltageB = dic.get('111', '0')
		voltB = float(voltageB) / 10
		voltB = round(voltB, 0)
	if dic.get('112') is not None:
		currentB = dic.get('112', '0')
		currB = float(currentB) / 1000
		currB = round(currB, 1)
	if dic.get('113') is not None:
		activepowerB = dic.get('113', '0')
		powerB = float(activepowerB)
	if dic.get('114') is not None:
		powerfactorB = dic.get('114', '0')
	if dic.get('116') is not None:
		energyBstr = dic.get('116', '0')
		energyB = float(energyBstr) * 10
	if dic.get('121') is not None:
		voltageC = dic.get('121', '0')
		voltC = float(voltageC) / 10
		voltC = round(voltC, 0)	
	if dic.get('122') is not None:
		currentC = dic.get('122', '0')
		currC = float(currentC) / 1000
		currC = round(currC, 1)
	if dic.get('123') is not None:
		activepowerC = dic.get('123', '0')
		powerC = float(activepowerC)
	if dic.get('124') is not None:
		powerfactorC = dic.get('124', '0')
	if dic.get('126') is not None:
		energyCstr = dic.get('126', '0')
		energyC = float(energyCstr) * 10
	if dic.get('131') is not None:
		energystr = dic.get('131', '0')
		energy = float(energystr) * 10
	if dic.get('132') is not None:	
		current = dic.get('132', '0')
		curr = float(current) / 1000
		curr = round(curr, 1)
	if dic.get('133') is not None:	
		powerstr = dic.get('133', '0')
		power = float(powerstr)
	if dic.get('135') is not None:	
		frequency = dic.get('135', '0')
		freq = float(frequency)
	if dic.get('136') is not None:	
		temperature = dic.get('136', '0')
		temp = float(temperature) / 10
	if dic.get('137') is not None:	
		status = dic.get('137', '0')
	if dic.get('138') is not None:	
		voltage_phase_seq = dic.get('138', '0')
		
	if voltA != last_voltA:
		UpdateDevice("voltageL1", 4, str(voltA))
		last_voltA = voltA
	if currA != last_currA or currB != last_currB or currC != last_currC:
		UpdateDevice("current", 1, str(currA)+';'+str(currB)+';'+str(currC)+';')
		last_currA = currA
		last_currB = currB
		last_currC = currC
	if powerA != last_powerA:
		UpdateDevice("powerL1", 7, str(powerA)+';'+str(energyA)+';')
		last_powerA = powerA
	if voltB != last_voltB:
		UpdateDevice("voltageL2", 5, str(voltB))
		last_voltB = voltB
	if powerB != last_powerB:
		UpdateDevice("powerL2", 8, str(powerB)+';'+str(energyB)+';')
		last_powerB = powerB
	if voltC != last_voltC:
		UpdateDevice("voltageL3", 6, str(voltC))
		last_voltC = voltC
	if powerC != last_powerC:
		UpdateDevice("powerL3", 9, str(powerC)+';'+str(energyC)+';')
		last_powerC = powerC
	if curr != last_curr:
		UpdateDevice("currentAll", 2, str(curr))
		last_curr = curr
	if power != last_power:
		UpdateDevice("powerAll", 3, str(power)+';'+str(energy)+';')
		last_power = power
	if temp != last_temp:
		UpdateDevice("temp", 10, str(temp))
		last_temp = temp
	if freq != last_freq:
		UpdateDevice("freq", 11, str(freq))
		last_freq = freq
	return


def createDevice(ID, Unit):
	if ID in Devices:
		if Unit in Devices[ID].Units:
			value = False
		else:
			value = True
	else:
		value = True
	return value
	
def UpdateDevice(ID, Unit, sValue):
	if ID in Devices:
		if str(Devices[ID].Units[Unit].sValue) != str(sValue):
			Devices[ID].Units[Unit].sValue = str(sValue)
			if type(sValue) == int or type(sValue) == float:
				Devices[ID].Units[Unit].LastLevel = sValue
			elif type(sValue) == dict:
				Devices[ID].Units[Unit].Color = json.dumps(sValue)
			Devices[ID].Units[Unit].nValue = 0
			Devices[ID].TimedOut = 0
			Devices[ID].Units[Unit].Update(Log=True)

			Domoticz.Debug('Update device value:' + str(ID) + ' Unit: ' + str(Unit) + ' sValue: ' +  str(sValue))
	return

# Generic helper functions
def DumpConfigToLog():
	for x in Parameters:
		if Parameters[x] != "":
			Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
	Domoticz.Debug("Device count: " + str(len(Devices)))
	for DeviceName in Devices:
		Device = Devices[DeviceName]
		Domoticz.Debug("Device ID:       '" + str(Device.DeviceID) + "'")
		Domoticz.Debug("--->Unit Count:      '" + str(len(Device.Units)) + "'")
		for UnitNo in Device.Units:
			Unit = Device.Units[UnitNo]
			Domoticz.Debug("--->Unit:           " + str(UnitNo))
			Domoticz.Debug("--->Unit Name:     '" + Unit.Name + "'")
			Domoticz.Debug("--->Unit nValue:    " + str(Unit.nValue))
			Domoticz.Debug("--->Unit sValue:   '" + Unit.sValue + "'")
			Domoticz.Debug("--->Unit LastLevel: " + str(Unit.LastLevel))
	return
