#  Copyright (c) 2021
#
#  This file, Smartlock.py, is part of Project Alice.
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
#  Last modified: 2021.08.01 at 19:52:27 CEST

import sqlite3
from pathlib import Path
from typing import Dict, Union

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


	def getDeviceIcon(self) -> Path:
		if self.getParam('state') == 1:
			state = 'locked'
		else:
			state = 'unlocked'

		return Path(f'{self.Commons.rootDir()}/skills/{self.skillName}/devices/img/{state}.png')


	def onUIClick(self) -> dict:
		if self.getParam('state') == 1:
			action = 'unlock'
		else:
			action = 'lock'

		self.skillInstance.sendAPIRequest(nukiId=self.getConfig('smartlockId'), action=action)
		return super().onUIClick()
