import sqlite3
from typing import Dict, Union

from core.commons import constants
from core.device.model.Device import Device
from core.device.model.DeviceAbility import DeviceAbility


class Smartlock(Device):

	@classmethod
	def getDeviceTypeDefinition(cls) -> dict:
		return {
			'deviceTypeName'        : 'Smartlock',
			'perLocationLimit'      : 0,
			'totalDeviceLimit'      : 0,
			'allowLocationLinks'    : True,
			'allowHeartbeatOverride': False,
			'heartbeatRate'         : 5,
			'abilities'             : [DeviceAbility.NONE]
		}


	def __init__(self, data: Union[sqlite3.Row, Dict]):
		super().__init__(data)