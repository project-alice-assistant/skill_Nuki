from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler


class Nuki(AliceSkill):
	"""
	Author: Psychokiller1888
	Description: Connect your nuki smart locks to alice!
	"""


	@IntentHandler('MyIntentName')
	def testIntent(self, session: DialogSession, **_kwargs):
		pass


	@IntentHandler('MySecondIntentName')
	def secondTestIntent(self, session: DialogSession, **_kwargs):
		pass