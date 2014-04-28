// Define constants.
var TOPBAR_HEIGHT = 50;
var TOPBAR_BACK_BUTTON_WIDTH = 100;
var PLANET_INFO_WIDTH = 300;
var ORDERS_WIDTH = 300;
var ORDER_LABEL_HEIGHT = 40;

/**************************************************************************************************
                                         IAGUIButton
**************************************************************************************************/

function IAGUIButton(x, y, width, height, color, content, textColor, toRun) {
    this.x = x;
    this.y = y;
    this.width = width;
    this.height = height;

    this.color = color;
    this.content = content;
    this.textColor = textColor;

    this.toRun = toRun;
}

IAGUIButton.prototype.draw = function(context) {

};

IAGUIButton.prototype.pointInside = function(clickX, clickY) {
    var x1 = this.x;
    var y1 = this.y;
    var x2 = this.x + this.width;
    var y2 = this.y + this.height;

    var cond1 = x1 <= clickX;
    var cond2 = clickX <= x2;
    var cond3 = y1 <= clickY;
    var cond4 = clickY <= y2;

    return cond1 && cond2 && cond3 && cond4;
}

/**************************************************************************************************
                                       IAGUIDraggable
**************************************************************************************************/

function IAGUIDraggable(x, y, width, height, color, content, textColor, whenReleased) {

}

/**************************************************************************************************
                                       IAGUILabel
**************************************************************************************************/

function IAGUILabel(x, y, content, textColor) {
    this.x = x;
    this.y = y;
    this.content = content;
    this.textColor = textColor;
}

IAGUILabel.prototype.draw = function(context) {

};

/**************************************************************************************************
                                           IAGUI
**************************************************************************************************/

/**
 * TODO
 */
function IAGUI(canvas, dragCanvas, tooltipCanvas, faction) {
    this.faction = faction;

    this.canvas = canvas;
    this.dragCanvas = dragCanvas;
    this.tooltipCanvas = tooltipCanvas;
    this.context = this.canvas.getContext('2d');
    this.dragContext = this.dragCanvas.getContext('2d');
    this.tooltipContext = this.tooltipCanvas.getContext('2d');

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

    // Private variables.
    this._buttons = [];
    this._draggables = [];
    this._labels = [];
    this._mouseDownIn = null;
    this._dragging = null;
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
    this.showingTopbar = false;
};

IAGUI.prototype.setPlanetInfo = function (planet) {
    this.showingPlanetInfo = true;

    // Draw the fleet icons.
};

IAGUI.prototype.closePlanetInfo = function () {
    this.showingPlanetInfo = false;
};

IAGUI.prototype.showOrders = function () {
    // Screen width and height.
    var sWidth = window.innerWidth;
    var sHeight = window.innerHeight;

    var a = 0; // iteration
    var b = 0; // counting

    // For every order, draw the summary of the order followed by a red "X" button to indicate
    // that the user can cancel the order.
    var buttonAttrs = {
        x : -1,
        y : -1,
        width : ORDER_LABEL_HEIGHT,
        height : ORDER_LABEL_HEIGHT,
        color : "red",
        textColor : "white",
        content : "X",
        toRun : null
    };

    // Move orders
    for (a = 0; a < orders.move.length; a++) {
        // Add the button to the orders sidebar.
        buttonAttrs.x = ORDERS_WIDTH - ORDER_LABEL_HEIGHT;
        buttonAttrs.y = TOPBAR_HEIGHT + (b * ORDER_LABEL_HEIGHT);
        this._addButton(buttonAttrs);

        // Create the label for this move order and draw it.
        var label = "Move Fleet 1 from PLANET to PLANET.";

        // Increment count.
        b++;
    }

    // Hyperspace orders
    for (a = 0; a < orders.move.length; a++) {
        // Add the button to the orders sidebar.
        buttonAttrs.x = ORDERS_WIDTH - ORDER_LABEL_HEIGHT;
        buttonAttrs.y = TOPBAR_HEIGHT + (b * ORDER_LABEL_HEIGHT);
        this._addButton(buttonAttrs);

        // Create the label for this hyperspace order and draw it.
        var label = "Compute FTL jump from PLANET to DEST.";

        // Increment count.
        b++;
    }

    // Build orders
    for (a = 0; a < orders.build.length; a++) {
        // Add the button to the orders sidebar.
        buttonAttrs.x = ORDERS_WIDTH - ORDER_LABEL_HEIGHT;
        buttonAttrs.y = TOPBAR_HEIGHT + (b * ORDER_LABEL_HEIGHT);
        this._addButton(buttonAttrs);

        // Create the label for this build order and draw it.
        var label = "Build N fleets at PLANET.";

        // Increment count.
        b++;
    }

    // Colonize orders
    for (a = 0; a < orders.colonize.length; a++) {
        // Add the button to the orders sidebar.
        buttonAttrs.x = ORDERS_WIDTH - ORDER_LABEL_HEIGHT;
        buttonAttrs.y = TOPBAR_HEIGHT + (b * ORDER_LABEL_HEIGHT);
        this._addButton(buttonAttrs);

        // Create the label for this colonize order and draw it.
        var label = "Found COLONY on/in orbit of PLANET.";

        // Increment count.
        b++;
    }
};

IAGUI.prototype.draw = function () {
    var sWidth = window.innerWidth;
    var sHeight = window.innerHeight;

    this.context.fillStyle = this.uiColor;

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
        // Draw background.
        this.context.fillRect(0, TOPBAR_HEIGHT, ORDERS_WIDTH, sHeight);
    }
};

IAGUI.prototype._addButton = function(attrs) {
    var x;
    var y;
    var width = attrs.width;
    var height = attrs.height;

    var sWidth = window.innerWidth;
    var sHeight = window.innerHeight;

    // Assign x-coordinate.
    if (attrs.left) {
        x = attrs.left;
    }
    else {
        x = sWidth - attrs.right;
    }

    // Assign y-coordinate.
    if (attrs.top) {
        y = attrs.top;
    }
    else {
        y = sHeight - attrs.bottom;
    }

    // Create the button
    var button = new IAGUIButton(x, y, width, height, attrs.color, attrs.content,
                                 attrs.textColor);
    this._buttons.push(button);
};

IAGUI._addLabel = function(attrs) {
    var x;
    var y;

    var sWidth = window.innerWidth;
    var sHeight = window.innerHeight;

    // Assign x-coordinate.
    if (attrs.left) {
        x = attrs.left;
    }
    else {
        x = sWidth - attrs.right;
    }

    // Assign y-coordinate.
    if (attrs.top) {
        y = attrs.top;
    }
    else {
        y = sHeight - attrs.bottom;
    }

    // Create the new label.
    var label = new IAGUILabel(x, y, content, textColor);
    this._labels.push(label);
}

IAGUI.prototype._clearButtons = function() {
    this._buttons = [];
};

/**
 * Args:
 *
 * Returns:
 *      "true" if the click was on the GUI, indicating to the 3D view that it is not to attempt
 *      clicking on meshes. "false" if the click was outside the GUI, indicating to the 3D view
 *      that it can look for mesh clicks.
 */
IAGUI.prototype.onmousedown = function (event) {
    var a = 0; // iteration

    var x;
    var y; // TODO

    // CASE: y value within range of topbar
    if (y <= TOPBAR_HEIGHT) {
        return true;
    }

    for (a = 0; a < this._buttons.length; a++) {
        var button = this._buttons[a];

        if (button.pointInside(x, y)) {
            this._mouseDownIn = button;
            return true;
        }
    }

    // No GUI found.
    return false;
};

/**
 * Args:
 *
 * Returns:
 *      "true" if the click was on the GUI, indicating to the 3D view that it is not to attempt
 *      clicking on meshes. "false" if the click was outside the GUI, indicating to the 3D view
 *      that it can look for mesh clicks.
 */
IAGUI.prototype.onmouseup = function (event) {
    var a = 0; // iteration

    var x;
    var y;

    // Loop through buttons.
    for (a = 0; a < this._buttons.length; a++) {
        var button = this._buttons[a];

        if (inside && button === this._mouseDownIn) {
            this._mouseDownIn = null;
            button.toRun();
            return true;
        }

        else if (inside && button !== this._mouseDownIn) {
            this._mouseDownIn = null;
            return true;
        }
    }

    // Uh...
    return true;
};

/**
 * Args:
 *
 * Returns:
 *      "true" if the click was on the GUI, indicating to the 3D view that it is not to attempt
 *      clicking on meshes. "false" if the click was outside the GUI, indicating to the 3D view
 *      that it can look for mesh clicks.
 */
IAGUI.prototype.onmousemove = function (event) {

};


IAGUI.prototype.drawTooltip = function (x, y, tooltip) {
    // TODO
    tooltipContext.clearRect(0, 0, window.innerWidth, window.innerHeight);
    tooltipContext.fillStyle = this.textColor;
    tooltipContext.fillText(tooltip, x, y);
};