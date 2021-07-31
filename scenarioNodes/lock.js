module.exports = function(RED) {
	function lock(config) {
		RED.nodes.createNode(this, config);
	}

	RED.nodes.registerType('lock', lock);
}