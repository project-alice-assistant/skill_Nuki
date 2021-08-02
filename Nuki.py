#  Copyright (c) 2021
#
#  This file, Nuki.py, is part of Project Alice.
#
#  Project Alice is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>
#
#  Last modified: 2021.08.02 at 06:39:56 CEST

#  Copyright (c) 2021
#
#  This file, Nuki.py, is part of Project Alice.
#
#  Project Alice is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>
#
#  Last modified: 2021.08.01 at 20:12:44 CEST
import time
from typing import Any, Dict

import requests

from core.ProjectAliceExceptions import SkillStartingFailed
from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler, KnownUser


class Nuki(AliceSkill):
	"""
	Author: Psychokiller1888
	Description: Connect your Nuki smart locks to alice!
	"""

	API_URL = 'https://api.nuki.io/'
	HEADERS: Dict[str, str] = dict()

	def __init__(self):
		super().__init__()
		self._connected = False
		self._smartLocks = dict()


	def onStart(self):
		super().onStart()
		if not self.connectAPI():
			raise SkillStartingFailed(skillName=self.name, error='Please provide a valid Nuki developer API token in the skill settings')

		self._connected = True
		self.getSmartLocks()

		self.logInfo(f'Retrieved {len(self._smartLocks)} Nuki devices from Nuki web API')

		self.checkSmartlockDevices()
		self.ThreadManager.newThread(name='updateSmartLocks', target=self.runner)


	def runner(self):
		"""
		Updates the smartlocks every 5 seconds
		"""
		while True:
			time.sleep(5)
			self.getSmartLocks()

			for smartlockId, smartlock in self._smartLocks.items():
				for device in self._myDevices.values():
					if device.getConfig('smartlockId') != smartlockId:
						continue

					configs: Dict[str, Any] = smartlock.get('state', dict())
					device.updateConfigs(configs)
					break


	def checkSmartlockDevices(self):
		"""
		Check if we have all locks and not any non existing one
		:return:
		"""

		# Check if what's on the web we have locally
		for lockId, lock in self._smartLocks.items():
			found = False
			for device in self.myDevices.values():
				if device.getConfig('smartlockId') == lockId:
					found = True
					break

			if not found:
				self.logInfo(f'Found new smart lock with name **{lock["name"]}** on Nuki account')
				device = self.DeviceManager.addNewDevice(deviceType='SmartLock', skillName=self.name, displayName=lock['name'])
				configs: Dict[str, Any] = lock.get('state', dict())
				configs.setdefault('smartlockId', lock['smartlockId'])
				device.updateConfigs(configs)
				device.connected = True

		# Check if what we have locally is on the web
		for device in self.myDevices.values():
			lockId = device.getConfig('smartlockId')
			if lockId not in self._smartLocks:
				self.logInfo(f'Smart lock with id **{lockId}** not found on Nuki account, removing from Alice')
				self.DeviceManager.deleteDevice(deviceUid=device.uid)


	def connectAPI(self) -> bool:
		"""
		Tries to connect to the Nuki web api
		"""
		apiToken = self.getConfig('apiToken')
		if not apiToken:
			return False

		self.HEADERS = {
			'Accept'           : 'application/json',
				'Authorization': f'Bearer {self.getConfig("apiToken")}'
			}

		response = requests.get(
			url=f'{self.API_URL}account',
			headers=self.HEADERS
		)

		if response.status_code != 200:
			return False

		self.logInfo('Nuki API connected!')
		return True


	def getSmartLocks(self):
		"""
		Gets all the smart locks registered on the connected Nuki account
		"""
		if not self._connected:
			self.logWarning('Cannot retrieve smart locks if API not connected')
			return

		response = requests.get(
			url=f'{self.API_URL}smartlock',
			headers=self.HEADERS
		)

		if response.status_code != 200:
			self.logDebug("Couldn't retrieve smart locks")
			return

		self._smartLocks = response.json()


	@IntentHandler('HandleLock')
	@KnownUser
	def handleLock(self, session: DialogSession, **_kwargs):
		"""
		Handles lock and unlock voice commands
		"""
		if not self._connected:
			self.logWarning('Cannot handle smart locks if API not connected')

		action: str = session.slotValue('actionType')
		lockName: str = session.slotValue('lockName')
		location: str = session.slotRawValue('location')

		deviceType = self.DeviceManager.getDeviceType(self._name, 'SmartLock')
		if lockName == 'all':
			devices = self.DeviceManager.getDevicesByType(deviceType=deviceType, connectedOnly=False)
		elif not location and not lockName:
			devices = self.DeviceManager.getDevicesByLocation(locationId=session.locationId, deviceType=deviceType, connectedOnly=False)
		elif location and not lockName:
			loc = self.LocationManager.getLocationByName(name=location)
			if not loc:
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk(text='unknownLocation'))
				return
			devices = self.DeviceManager.getDevicesByLocation(locationId=loc.id, deviceType=deviceType, connectedOnly=False)
		else:
			lockId = 0
			for lock in self._smartLocks:
				if lock['name'].lower() == lockName.lower():
					lockId = lock['smartlockId']
					break

			if not lockId:
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk(text='unknownLock', replace=lockName))
				return

			devices = [self._smartLocks[lockId]]

		if not devices:
			self.endDialog(sessionId=session.sessionId, text=self.randomTalk(text='unknownLock'))
			return

		for device in devices:
			nukiId = device.getConfig('smartlockId', None)
			if not nukiId:
				continue

			self.sendAPIRequest(nukiId=nukiId, action=action)

		self.endDialog(sessionId=session.sessionId, text=self.randomTalk('doneClose') if action == 'lock' else self.randomTalk(text='doneOpen'))


	def sendAPIRequest(self, nukiId: int, action: str):
		response = requests.post(
			url=f'{self.API_URL}smartlock/{nukiId}/action/{action}',
			headers=self.HEADERS
		)

		if response.status_code != 204:
			self.logWarning(f'Failed "{action}" on smartlock id **{nukiId}**, error code {response.status_code}')
