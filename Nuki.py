import requests

from core.ProjectAliceExceptions import SkillStartingFailed
from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler


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
	def handleLock(self, session: DialogSession, **_kwargs):
		if not self._connected:
			self.logWarning('Cannot handle smart locks if API not connected')

		action = session.slotValue('actionType')
		lockName = session.slotValue('lockName')

		if lockName == 'all':
			for lockName, lock in self._smartLocks.items():
				response = requests.get(
					url=f'{self.API_URL}smartlock/{lock["smartlockId"]}',
					headers=self.HEADERS
				)

				if response.status_code != 200:
					self.logWarning(f'Smart lock with name **{lockName}** not found, skipping')
					continue

		else:
			if lockName not in self._smartLocks:
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk('smartLockNotFound', replace=[lockName]))
