// Define constants.
var TOPBAR_HEIGHT = 50;
var TOPBAR_BACK_BUTTON_WIDTH = 100;
var PLANET_INFO_WIDTH = 300;
var ORDERS_WIDTH = 300;

function IAGUI(faction) {
	this.faction = faction;

	this.canvas = document.getElementById('canvas');
	this.dragCanvas = document.getElementById('dragCanvas');
	this.context = this.canvas.getContext('2d');
	this.dragContext = this.dragCanvas.getContext('2d');

	// Display tracking variables.
	this.showingTopbar = false;
	this.showingPlanetInfo = false;
	this.showingOrders = false;
	this.draggingFleet = false;
	this.mouseDownPosition = null;

	// Topbar display variables
	this.money = -1;
	this.turnNumber = -1;
	this.backLabel = "";
	this.backFunction = null;

	// ISCA
	if (faction === 0) {
		this.uiColor = "blue";
		this.textColor = "white";
	}

	// GalaxyCorp
	else if (faction === 1) {
		this.uiColor = "green";
		this.textColor = "white";
	}

	// FSR
	else if (faction === 2) {
		this.uiColor = "white";
		this.textColor = "black";
	}

	// Mercs/privateers
	else if (faction === 3) {
		this.uiColor = "red";
		this.textColor = "white";
	}
}

IAGUI.prototype.labelForTurn = function (turnNumber) {
	var faction = this.faction;
	var year = Math.floor(turnNumber / 4);
	var months;
	var month;

	// The ISCA and Mercs use the standard calendar year.
	if (faction === 0 || faction === 3) {
		months = ["March", "June", "September", "December"];
		month = months[(turnNumber - 1) % 4];
		return month+" "+year;
	}

	// GalaxyCorp uses the fiscal year.
	else if (faction === 1) {
		months = ["Quarter 1", "Quarter 2", "Quarter 3", "Quarter 4"];
		month = months[(turnNumber - 1) % 4];
		return month+", Fiscal Year "+year;
	}

	// FSR uses a decimal calender with the moon landing as year zero
	else if (faction === 2) {
		year -= 1969;
		months = [".00", ".25", ".50", ".75"];
		month = months[(turnNumber - 1) % 4];
		return year+month;
	}
};

IAGUI.prototype.setTopbar = function (money, turnNumber, backLabel, backFunction) {
	this.money = money;
	this.turnNumber = turnNumber;

	this.showingTopbar = true;
};

IAGUI.prototype.closeTopbar = function () {

};

IAGUI.prototype.setPlanetInfo = function (planet) {

};

IAGUI.prototype.closePlanetInfo = function () {

};

IAGUI.prototype.draw = function () {
	var sWidth;
	var sHeight;

	if (this.showingTopbar) {
		// Draw background.
		this.context.fillRect(0, 0, sWidth, TOPBAR_HEIGHT);
	}

	if (this.showingPlanetInfo) {
		// Draw background.
		this.context.fillRect(sWidth - PLANET_INFO_WIDTH, TOPBAR_HEIGHT, sWidth, sHeight);

		// Draw the fleet icons on the drag canvas. The reason why we have a separate canvas for
		// this is so we don't have to redraw the entire canvas for when a user drags a fleet.
	}

	if (this.showingOrders) {

	}
};

/**
 * Args:
 *
 * Returns:
 *		"true" if the click was on the GUI, indicating to the 3D view that it is not to attempt
 *		clicking on meshes. "false" if the click was outside the GUI, indicating to the 3D view
 *		that it can look for mesh clicks.
 */
IAGUI.prototype.onmousedown = function (event) {

};

/**
 * Args:
 *
 * Returns:
 *		"true" if the click was on the GUI, indicating to the 3D view that it is not to attempt
 *		clicking on meshes. "false" if the click was outside the GUI, indicating to the 3D view
 *		that it can look for mesh clicks.
 */
IAGUI.prototype.onmouseup = function (event) {

};

/**
 * Args:
 *
 * Returns:
 *		"true" if the click was on the GUI, indicating to the 3D view that it is not to attempt
 *		clicking on meshes. "false" if the click was outside the GUI, indicating to the 3D view
 *		that it can look for mesh clicks.
 */
IAGUI.prototype.onmousemove = function (event) {

};