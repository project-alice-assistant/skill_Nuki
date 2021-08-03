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

					let button = document.createElement('i')
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
					tile.querySelector('.nuki_button').classList.add('far')
					tile.querySelector('.nuki_button').classList.add('fa-circle')
					tile.querySelector('.nuki_button').classList.remove('fas')
					tile.querySelector('.nuki_button').classList.remove('fa-circle-notch')
				} else {
					tile.querySelector('.nuki_button').classList.add('fas')
					tile.querySelector('.nuki_button').classList.add('fa-circle-notch')
					tile.querySelector('.nuki_button').classList.remove('far')
					tile.querySelector('.nuki_button').classList.remove('fa-circle')
				}
			}
		})
	}
}
