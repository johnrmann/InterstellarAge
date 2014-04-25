/**
 * InterstellarAge
 * orders.js
 *
 * Requires:
 *      Definition of global variable "gameId"
 *      jQuery
 */

/**
 * This global object contains variables and methods to facilitate (1) the
 * issuing of orders (2) the submission of orders.
 *
 * Private Attributes:
 *      move (list): A list of objects that compose an order to move a fleet
 *                   from one planet to another planet in the same system.
 *
 *      hyperspace (list):
 *
 *      colonize (list):
 *
 *      build (list):
 *
 *      idCount (int): Incremented every time a new order is created, thus
 *                     giving each order a unique ID.
 *
 *      submitted (boolean): Set to "true" while we are waiting for the submit
 *                           AJAX request to be completed.
 */
var orders = {
    move : [],
    hyperspace : [],
    colonize : [],
    build : [],

    create : {
        moveOrder : null,
        hyperspaceOrder : null,
        buildOrder : null,
        upgradeOrder : null
    },

    deleteOrder : null,
    submit : null,
    reset : null,

    idCount : 0,
    submitted : false
};

/**
 * Called when the user wants to move a fleet stationed in slot "fleetNumber"
 * at planet with unique ID "fromPlanet" to a planet with unique ID "toPlanet"
 * in the same system as "fromPlanet".
 */
orders.create.moveOrder = function (fromPlanet, toPlanet, fleetNumber) {
    orders.move.push({
        unique : orders.idCount,
        from_planet : fromPlanet,
        to_planet : toPlanet,
        fleet_number : fleetNumber
    });

    orders.idCount += 1;
};

/**
 * Called when the user wants to move a fleet stationed in slot "fleetNumber"
 * at planet with unique ID "fromPlanet" to (1) a planet in another system with
 * unique ID "toPlanet" or (2) an undiscovered system with unique ID "toSystem"
 */
orders.create.hyperspaceOrder = function (fromPlanet, toPlanet, toSystem,
                                          fleetNumber) {
    if (toPlanet === -1) {
        orders.hyperspace.push({
            unique : orders.idCount,
            from_planet : fromPlanet,
            to_system : toSystem,
            fleet_number : fleetNumber
        });
    }

    else if (toSystem === -1) {
        orders.hyperspace.push({
            unique : orders.idCount,
            from_planet : fromPlanet,
            to_planet : toPlanet,
            fleet_number : fleetNumber
        });
    }

    orders.idCount += 1;
};

orders.create.upgradePlanetOrder = function (planet, upgradeType, colonyName) {
    orders.colonize.push({
        unique : orders.idCount,
        planet : planet,
        upgrade_type : upgradeType,
        new_colony_name : colonyName
    });

    orders.idCount += 1;
};

orders.create.buildOrder = function (atPlanet, fleetNumber, ships) {
    orders.build.push({
        unique : orders.idCount,
        at_planet : atPlanet,
        fleet_number : fleetNumberm
        ships : ships
    });

    orders.idCount += 1;
};

orders.deleteOrder = function (unique) {
    var a = 0;

    var moveLen = orders.move.length;
    var hyperspaceLen = orders.hyperspace.length;
    var buildLen = orders.build.length;
    var colonizeLen = orders.colonize.length;
};

/**
 * Sends the orders to the server with an AJAX request. Assumes that the
 * user has confirmed that his/her orders are final.
 */
orders.submit = function () {
    // Can't submit orders twice.
    if (orders.submitted) {
        return;
    }
    orders.submitted = true;

    // Use AJAX to send the orders to the server.
    $.ajax({
        type : 'POST',
        url : '/game/submitorders',
        data : {
            'game' : gameId,
            'move' : orders.move,
            'hyperspace' : orders.hyperspace,
            'build' : orders.build,
            'colonize' : orders.colonize
        },
        success : function(fromServer) {
            console.log(fromServer);
            orders.reset();
        }
    });
};

orders.reset = function () {
    orders.submitted = false;
    orders.idCount = 0;

    orders.move = [];
    orders.hyperspace = [];
    orders.build = [];
    orders.colonize = [];
};