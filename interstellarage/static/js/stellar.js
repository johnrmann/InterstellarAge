// Define constants.
var WORLD_SPACES_PER_AU = 10;

function Planet (planetInfo) {
    // Assign information from planetInfo.
    this.unique = planetInfo.unique;
    this.name = planetInfo.name;
    this.type = planetInfo.type;
    this.moons = [];
    for (var a = 0; a < planetInfo.moons.length; a++) {
        var moon = new Planet(planetInfo.moons[a]);
        this.moons.push(moon);
    }
    this.spaceColonies = [];
    this.groundColonies = [];
    this.owner = planetInfo.owner;

    // Assign astronomy data.
    this.size = planetInfo.size;
    this.orbitPeriod = planetInfo.orbit_period;
    this.orbitDistance = planetInfo.orbit_distance;

    // Calculate a random orbit position.
    this.orbitOffset = Math.random() * 2 * Math.PI;

    // Uh...
    this.parentSize = 0.0;
}

/**
 * Calculates the cartesian (x, y) position of the Planet on a given turn number.
 *
 * Arguments:
 *
 * Returns:
 */
Planet.prototype.position = function (turnNumber, theta) {
    var orbits;
    turnNumber -= 1;

    orbits = turnNumber * this.orbitPeriod;
    orbits += this.orbitOffset;

    var x = Math.sin(orbits + theta);
    var y = Math.cos(orbits + theta);

    var r = (this.orbitDistance * WORLD_SPACES_PER_AU) + this.parentSize;

    return [x * r, y * r];
};

function spectralClassColor (spectralClass) {
    if (spectralClass === "O") {
        return 0x9bb0ff;
    }

    else if (spectralClass === "B") {
        return 0xaabfff;
    }

    else if (spectralClass === "A") {
        return 0xcad8ff;
    }

    else if (spectralClass === "F") {
        return 0xfbf8ff;
    }

    else if (spectralClass === "G") {
        return 0xfff4e8;
    }

    else if (spectralClass === "K") {
        return 0xffddb4;
    }

    else if (spectralClass === "M") {
        return 0xffbd6f;
    }

    else if (spectralClass === "L") {
        return 0xf84235;
    }

    else if (spectralClass === "T") {
        return 0xba3059;
    }

    else if (spectralClass === "Y") {
        return 0x605170;
    }

    console.log("Unknown spectral class "+spectralClass);
    return 0xffffff;
}