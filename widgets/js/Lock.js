class Nuki_Lock extends Widget {

	constructor(uid, widgetId) {
		super(uid, widgetId)
		this.refresh()
		this.interval = setInterval(()=>this.refresh(), 5000)
	}

	stop() {
		clearInterval(this.interval)
	}

	refresh() {
		let self = this
		// noinspection JSUnresolvedVariable
		this.mySkill.getLocks().then(response => response.json()).then(data => {
			for (const [uid, smartlock] of Object.entries(data.data)) {
				let tile = self.myDiv.querySelector(`div[data-uid="smartlock_${uid}"]`)
				if (!tile) {
					tile = document.createElement('div')
					tile.classList.add('nuki_tile')
					tile.dataset.uid = `smartlock_${uid}`

					let lockName = document.createElement('div')
					lockName.classList.add('nuki_name')

					let content = document.createTextNode(smartlock['deviceConfigs']['displayName'])
					lockName.appendChild(content)

					let button = document.createElement('div')
					button.classList.add('nuki_button')

					tile.appendChild(lockName)
					tile.appendChild(button)

					tile.addEventListener('click', function() {
						self.mySkill.toggleLock({'uid': uid})
					})

					self.myDiv.querySelector('#nuki_container').appendChild(tile)
				}

				if (smartlock['deviceParams']['batteryCritical']) {
					tile.querySelector('.nuki_name').classList.remove('text')
					tile.querySelector('.nuki_name').classList.add('red')
				} else {
					tile.querySelector('.nuki_name').classList.remove('red')
					tile.querySelector('.nuki_name').classList.add('text')
				}

				if (smartlock['deviceParams']['state'] === 1) {
					tile.querySelector('.nuki_button').style.backgroundImage = `url("http://${this.aliceSettings['aliceIp']}:${this.aliceSettings['apiPort']}/api/v1.0.1/widgets/resources/img/Nuki/closed.png")`
				} else {
					if (smartlock['deviceParams']['doorState'] === 3) {
						tile.querySelector('.nuki_button').style.backgroundImage = `url("http://${this.aliceSettings['aliceIp']}:${this.aliceSettings['apiPort']}/api/v1.0.1/widgets/resources/img/Nuki/door_open.png")`
					} else {
						tile.querySelector('.nuki_button').style.backgroundImage = `url("http://${this.aliceSettings['aliceIp']}:${this.aliceSettings['apiPort']}/api/v1.0.1/widgets/resources/img/Nuki/open.png")`
					}
				}
			}
		})
	}
}
