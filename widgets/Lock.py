from core.webui.model.Widget import Widget
from core.webui.model.WidgetSizes import WidgetSizes


class Lock(Widget):

	DEFAULT_SIZE = WidgetSizes.w_wide

	def getLocks(self) -> dict:
		return {device.uid: device.toDict() for device in self.skillInstance.myDevices.values()}


	def toggleLock(self, uid: str):
		# noinspection PyUnresolvedReferences
		self.skillInstance.toggleLock(uid=uid)
