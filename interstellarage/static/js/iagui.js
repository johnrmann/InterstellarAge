// Define constants.
var TOPBAR_HEIGHT = 50;
var TOPBAR_BACK_BUTTON_WIDTH = 100;
var PLANET_INFO_WIDTH = 300;
var ORDERS_WIDTH = 300;
var ORDER_LABEL_HEIGHT = 40;
var FLEET_ICON_HEIGHT = 90;
var COLONY_LABEL_HEIGHT = 20;
var FONT_SIZE = 12;
var FONT_LARGE_SIZE = 24;

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
    var oldFill = "white";
    if (context.fillStyle) {
        oldFill = context.fillStyle;
    }

    // Draw the background.
    context.fillStyle = this.color;
    context.fillRect(this.x, this.y, this.width, this.height);

    // Prepare to draw the text.
    var textWidth = context.measureText(this.content).width;
    var textHeight = FONT_SIZE;
    var midpointX = this.x + (this.width / 2);
    var midpointY = this.y + (this.height / 2);
    var drawX = midpointX - (textWidth / 2);
    var drawY = midpointY - (textHeight / 2);

    // Draw the text.
    context.rect(drawX, drawY, textWidth, textHeight);
    context.fillStyle = this.textColor;
    context.fillText(this.content, drawX, drawY + textHeight);

    // Reset context values.
    context.fillStyle = oldFill;
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
};

/**************************************************************************************************
                                       IAGUIDraggable
**************************************************************************************************/

function IAGUIDraggable(x, y, width, height, color, content, textColor, textSize, whenReleased, info) {
    this.x = x;
    this.y = y;
    this.width = width;
    this.height = height;

    this._dragX = x;
    this._dragY = y;

    this.color = color;
    this.content = content;
    this.textColor = textColor;
    this.textSize = textSize;

    this.whenReleased = whenReleased;

    this.info = info;
}

IAGUIDraggable.prototype.pointInside = function(clickX, clickY) {
    var x1 = this._dragX;
    var y1 = this._dragY;
    var x2 = x1 + this.width;
    var y2 = y1 + this.height;

    var cond1 = x1 <= clickX;
    var cond2 = clickX <= x2;
    var cond3 = y1 <= clickY;
    var cond4 = clickY <= y2;

    return cond1 && cond2 && cond3 && cond4;
};

IAGUIDraggable.prototype.draw = function(context) {
    var oldFill = "white";
    if (context.fillStyle) {
        oldFill = context.fillStyle;
    }

    var x = this._dragX;
    var y = this._dragY;

    // Draw the background.
    context.fillStyle = this.color;
    context.fillRect(x, y, this.width, this.height);

    // Prepare to draw the text.
    var textWidth = context.measureText(this.content).width;
    var textHeight = FONT_SIZE;
    var midpointX = x + (this.width / 2);
    var midpointY = y + (this.height / 2);
    var drawX = midpointX - (textWidth / 2);
    var drawY = midpointY - (textHeight / 2);

    // Set the font.
    context.font = this.textSize+"px Arial";

    // Draw the text.
    context.rect(drawX, drawY, textWidth, textHeight);
    context.fillStyle = this.textColor;
    context.fillText(this.content, drawX, drawY + textHeight);

    // Reset context values.
    context.fillStyle = oldFill;
};

IAGUIDraggable.prototype.letGo = function() {
    this._dragX = this.x;
    this._dragY = this.y;
};

/**************************************************************************************************
                                       IAGUILabel
**************************************************************************************************/

function IAGUILabel(x, y, content, textColor, textSize) {
    this.x = x;
    this.y = y;
    this.content = content;
    this.textColor = textColor;
    this.textSize = textSize;
}

IAGUILabel.prototype.draw = function(context) {
    var oldFill = "white";
    if (context.fillStyle) {
        oldFill = context.fillStyle;
    }

    // Draw the text.
    context.font = this.textSize+"px Arial";
    context.fillStyle = this.textColor;
    context.fillText(this.content, this.x, this.y + this.textSize);

    // Reset context values.
    context.fillStyle = oldFill;
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

    // Set font size
    this.context.font = FONT_SIZE+"px Arial";
    this.dragContext.font = FONT_SIZE+"px Arial";
    this.tooltipContext.font = FONT_SIZE+"px Arial";

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
    this._mouseDownIn = null;
    this._dragging = null;

    this._topbarElems = [];
    this._planetViewElems = [];
}

IAGUI.prototype.clear = function () {
    this._buttons = [];
    this._mouseDownIn = null;
    this._dragging = null;
};

IAGUI.prototype.labelForTurn = function (turnNumber) {
    var faction = this.faction;
    var year = Math.floor(turnNumber / 4) + 2100;
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

    this._topbarElems = [];

    // Draw the current turn label.
    var turnLabelText = this.labelForTurn(this.turnNumber);
    var turnLabel = this._createLabel({
        right : 200,
        top : 10,
        textColor : this.textColor,
        textSize : FONT_LARGE_SIZE,
        content : turnLabelText
    });

    // Draw the money label.
    var moneyLabelText = "$"+this.money;
    var moneyLabel = this._createLabel({
        right: 400,
        top : 10,
        textColor : this.textColor,
        textSize : FONT_LARGE_SIZE,
        content : moneyLabelText
    });
    
    var factionLabelText;
    
    if (this.faction === 0) {
        factionLabelText = "ISCA";                                     
    }
    else if (this.faction === 1) {
        factionLabelText = "GalaxyCorp";                                      
    }
    else if (this.faction === 2) {
        factionLabelText = "FSR";                                      
    }
    else if (this.faction === 3) {
        factionLabelText = "Merc";                                      
    }
    var factionLabel = this._createLabel({
        right: 600,
        top : 10,
        textColor : this.textColor,
        textSize : FONT_LARGE_SIZE,
        content : factionLabelText
    });

    // Draw the back button.
    if (backLabel !== null && backLabel !== "") {
        var backButton = this._createButton({
            left : 0,
            top : 0,
            width : TOPBAR_BACK_BUTTON_WIDTH,
            height : TOPBAR_HEIGHT,
            content : backLabel,
            toRun : backFunction,
            textColor : this.textColor,
            color : this.uiColor
        });
        this._topbarElems.push(backButton);
    }

    // Draw the orders button.


    this._topbarElems.push(turnLabel);
    this._topbarElems.push(moneyLabel);
    this._topbarElems.push(factionLabel);
};

IAGUI.prototype.closeTopbar = function () {
    this.showingTopbar = false;
};

IAGUI.prototype.setPlanetInfo = function (planet, releasedCallback) {
    // Declare variables
    var a = 0;
    var curY = TOPBAR_HEIGHT;
    var label;
    var button;
    var draggable;
    var turnNumber = 1;

    // Delete existing labels.
    this._planetViewElems = [];

    // We're showing the planet info.
    this.showingPlanetInfo = true;

    // Add the planet name label.
    label = this._createLabel({
        right : PLANET_INFO_WIDTH - 5,
        top : TOPBAR_HEIGHT + 5,
        content : planet.name,
        textColor : this.textColor,
        textSize : FONT_LARGE_SIZE
    });
    this._planetViewElems.push(label);
    curY += FONT_LARGE_SIZE + 5;

    // Add the fleet icons.
    for (a = 0; a < planet.fleets.length; a++) {
        draggable = this._createDraggable({
            right : PLANET_INFO_WIDTH - 5 - (FLEET_ICON_HEIGHT + 5) * a,
            top : curY,
            content : "Fleet "+(a+1)+": "+planet.fleets[a]+" Ships",
            textColor : "white",
            color : "gray",
            textSize : FONT_SIZE,
            width : FLEET_ICON_HEIGHT,
            height : FLEET_ICON_HEIGHT,
            whenReleased : releasedCallback,
            info : {fleetNumber : a}
        });
        this._planetViewElems.push(draggable);
    }
    curY += FLEET_ICON_HEIGHT + 5;

    // Prepare colony drawing
    var labelAttrs = {
        right : PLANET_INFO_WIDTH - 15,
        top : curY,
        content : null,
        textColor : this.textColor,
        textSize : FONT_SIZE     
    };

    // Draw ground colonies header.
    labelAttrs.content = "Cities:";
    label = this._createLabel(labelAttrs);
    this._planetViewElems.push(label);

    // Draw the ground colony labels.
    curY += COLONY_LABEL_HEIGHT;
    for (a = 0; a < planet.groundColonies.length; a++) {
        labelAttrs.content = planet.groundColonies[a];
        labelAttrs.top = curY;
        label = this._createLabel(labelAttrs);
        this._planetViewElems.push(label);

        curY += (COLONY_LABEL_HEIGHT + 5);
    }

    // Draw space colonies.
    labelAttrs.content = "Space Stations:";
    labelAttrs.top = curY;
    label = this._createLabel(labelAttrs);
    this._planetViewElems.push(label);

    // Draw the space colony labels.
    curY += COLONY_LABEL_HEIGHT;
    for (a = 0; a < planet.spaceColonies.length; a++) {
        labelAttrs.content = planet.spaceColonies[a];
        labelAttrs.top = curY;
        label = this._createLabel(labelAttrs);
        this._planetViewElems.push(label);

        curY += (COLONY_LABEL_HEIGHT + 5);
    }

    // Add the FTL dropzone.
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
        this._createButton(buttonAttrs);

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
        this._createButton(buttonAttrs);

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
        this._createButton(buttonAttrs);

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
        this._createButton(buttonAttrs); // TODO add

        // Create the label for this colonize order and draw it.
        var label = "Found COLONY on/in orbit of PLANET.";

        // Increment count.
        b++;
    }
};

IAGUI.prototype.draw = function () {
    var sWidth = window.innerWidth;
    var sHeight = window.innerHeight;

    var a = 0;

    this.context.fillStyle = this.uiColor;

    // Clear everything.
    this.context.clearRect(0, 0, sWidth, sHeight);

    // Draw the topbar if such a thing is to be drawn.
    if (this.showingTopbar) {
        // Draw background.
        this.context.fillRect(0, 0, sWidth, TOPBAR_HEIGHT);
        
        // Draw the topbar elements
        for (a = 0; a < this._topbarElems.length; a++) {
            this._topbarElems[a].draw(this.context);
        }
    }

    if (this.showingPlanetInfo) {
        // Draw background.
        this.context.fillRect(sWidth - PLANET_INFO_WIDTH, TOPBAR_HEIGHT, sWidth, sHeight);

        // Draw the planet infos!
        for (a = 0; a < this._planetViewElems.length; a++) {
            var elem = this._planetViewElems[a];

            if (elem instanceof IAGUIDraggable) {
                elem.draw(this.dragContext);
            }
            else {
                elem.draw(this.context);
            }
        }
    }

    if (this.showingOrders) {
        // Draw background.
        this.context.fillRect(0, TOPBAR_HEIGHT, ORDERS_WIDTH, sHeight);
    }
};

IAGUI.prototype._createButton = function(attrs) {
    var x = 0;
    var y = 0;
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
    return button;
};

IAGUI.prototype._createLabel = function(attrs) {
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
    var label = new IAGUILabel(x, y, attrs.content, attrs.textColor, attrs.textSize);
    return label;
};

IAGUI.prototype._createDraggable = function(attrs) {
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

    // Create the new draggable.
    var draggable = new IAGUIDraggable(
        x, y, attrs.width, attrs.height,
        attrs.color, attrs.content, attrs.textColor, attrs.textSize,
        attrs.whenReleased,
        attrs.info
    );
    return draggable;
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

    var x = event.clientX;
    var y = event.clientY;

    // CASE: y value within range of topbar
    if (y <= TOPBAR_HEIGHT) {
        return true;
    }

    // If we're showing the planet info, look for a click inside one of the draggables.
    if (this.showingPlanetInfo) {
        for (a = 0; a < this._planetViewElems.length; a++) {
            var elem = this._planetViewElems[a];
            if (elem instanceof IAGUIDraggable && elem.pointInside(x, y)) {
                this._dragging = elem;
                return true;
            }
        }
    }

    // If we're showing the topbar, look for a click inside the buttons.
    if (this.showingTopbar) {
        for (a = 0; a < this._topbarElems.length; a++) {
            var elem = this._topbarElems[a];
            if (elem instanceof IAGUIButton && elem.pointInside(x, y)) {
                elem.toRun();
                return true;
            }
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

    var x = event.clientX;
    var y = event.clientY;

    // Are we dragging something?
    if (this._dragging !== null) {
        this._dragging.whenReleased(x, y, this._dragging.info);
        this._dragging.letGo();
        this._dragging = null;
    }

    // Loop through buttons.
    for (a = 0; a < this._buttons.length; a++) {
        var button = this._buttons[a];

        // If we release the mouse inside the same button, run that button's function.
        if (inside && button === this._mouseDownIn && button.toRun !== null) {
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
IAGUI.prototype.onmousemove = function (event) {
    var x = event.clientX;
    var y = event.clientY;

    var sWidth = window.innerWidth;
    var sHeight = window.innerHeight;

    if (this._dragging !== null && this._dragging instanceof IAGUIDraggable) {
        this._dragging._dragX = x;
        this._dragging._dragY = y;
        this.dragContext.clearRect(0, 0, sWidth, sHeight);
        this._dragging.draw(this.dragContext);
        return true;
    }
};


IAGUI.prototype.drawTooltip = function (x, y, tooltip) {
    // TODO
    this.tooltipContext.clearRect(0, 0, window.innerWidth, window.innerHeight);
    this.tooltipContext.fillStyle = this.textColor;
    this.tooltipContext.fillText(tooltip, x, y);
};
