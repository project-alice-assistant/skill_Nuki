import requests

from core.ProjectAliceExceptions import SkillStartingFailed
from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler, KnownUser


class Nuki(AliceSkill):
	"""
	Author: Psychokiller1888
	Description: Connect your nuki smart locks to alice!
	"""

	API_URL = 'https://api.nuki.io/'
	HEADERS = dict()

	def __init__(self):
		super().__init__()
		self._connected = False
		self._smartLocks = dict()


	def onStart(self):
		super().onStart()
		if not self.connectAPI():
			raise SkillStartingFailed(skillName=self.name, error='Please provide a valid Nuki developper API token in the skill settings')

		self._connected = True
		self.getSmartLocks()


	def connectAPI(self) -> bool:
		apiToken = self.getConfig('apiToken')
		if not apiToken:
			return False

		self.HEADERS = {
				'Accept': 'application/json',
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
		if not self._connected:
			self.logWarning('Cannot retrieve smart locks if API not connected')
			return

		response = requests.get(
			url=f'{self.API_URL}smartlock',
			headers=self.HEADERS
		)

		if response.status_code != 200:
			self.logWarning("Couldn't retrieve smart locks")
			return

		for lock in response.json():
			self._smartLocks[lock.name] = lock

		self.logInfo(f'Retrieved {len(response.json())} Nuki devices')


	@IntentHandler('HandleLock')
	@KnownUser
	def handleLock(self, session: DialogSession, **_kwargs):
		if not self._connected:
			self.logWarning('Cannot handle smart locks if API not connected')

		action = session.slotValue('actionType')
		lockName = session.slotValue('lockName')
		location = session.slotRawValue('location')

		deviceType = self.DeviceManager.getDeviceType(self._name, 'SmartLock')
		if lockName == 'all':
			devices = self.DeviceManager.getDevicesByType(deviceType=deviceType)
		elif not location and not lockName:
			devices = self.DeviceManager.getDevicesByLocation(locationId=session.locationId, deviceType=deviceType)
		elif location and not lockName:
			loc = self.LocationManager.getLocationByName(name=location)
			if not loc:
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk(text='unknownLocation'))
				return
			devices = self.DeviceManager.getDevicesByLocation(locationId=loc.id, deviceType=deviceType)
		else:
			if lockName not in self._smartLocks:
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk(text='unknownDevice', replace=lockName))
				return
			devices = [self._smartLocks[lockName]]

		for device in devices:
			nukiId = device.getConfig('smartlockId', None)
			if not nukiId:
				continue

			response = requests.get(
				url=f'{self.API_URL}smartlock/{nukiId}/action/{action}',
				headers=self.HEADERS
			)

			if response.status_code != 204:
				self.logWarning(f'Failed "{action}" on smartlock **{lockName}**, error code {response.status_code}')
				continue

		self.endDialog(sessionId=session.sessionId, text=self.randomTalk('doneClose') if action == 'close' else self.randomTalk(text='doneOpen'))
