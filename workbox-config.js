module.exports = {
	globDirectory: 'assets/',
	globPatterns: [
		'**/*.{json,png,jpg,js,css}'
	],
	swDest: 'assets/sw.js',
	ignoreURLParametersMatching: [
		/^utm_/,
		/^fbclid$/
	]
};