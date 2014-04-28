/*
 * Requires:
 *      - THREE.js
 *      - jquery
 *      - orders.js
 */

var lerp = function (v1, v2, t) {
    return (1 - t)*v1 + (t * v2);       
};

THREE.Vector3.prototype.lerp = function (pos, t) {
    return new THREE.Vector3(
        lerp(this.x, pos.x, t),
        lerp(this.y, pos.y, t),
        lerp(this.z, pos.z, t)
    );
};

var aspectRatio = (window.innerWidth / window.innerHeight);

var projector;
var objects = [];
var mouse = {
    x : 0,
    y : 0
};

var currentView = null;
var iagui = null;

/**
 * A "View" refers to a set of objects that would be displayed. Example views include the
 * Galaxy Map and the various solar systems.
 */
function View () {
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(50, aspectRatio, 0.1, 1000);
    this.renderer = new THREE.WebGLRenderer();

    this.visible = false;
}

/**
 * Displays the view in the HTML page.
 */
View.prototype.show = function () {
    currentView = this;
    this.visible = true;

    this.renderer.setSize(window.innerWidth, window.innerHeight);
    var d = document.getElementById("3d");
    d.appendChild(this.renderer.domElement);

    var that = this;
    document.onclick = function (event) {
        that.onclick(event);  
    };
    document.onmousemove = function(event) {
        that.mousehover(event);
    };
};

/**
 * Hides the view from the HTML page.
 */
View.prototype.hide = function () {
    if (this.visible) {
        this.visible = false;
        var d = document.getElementById("3d");
        d.removeChild(this.renderer.domElement);
    }
};

/**
 * Sets the position of this view's camera.
 */
View.prototype.setCameraPosition = function (x, y, z) {
    this.camera.position.x = x;
    this.camera.position.y = y;
    this.camera.position.z = z;
};

this.cameraPositionLerp = function (position2, time) {
    var position1 = this.camera.position.clone();

    var t = 0;

    while (t < 1) {
        t += FPS * time;
        this.camera.position = this.camera.position.lerp(position1, position2, t);
    }

    this.camera.position = position2;
};

View.prototype.setCameraRotation = function (x, y, z) {
    x /= 180;
    y /= 180;
    z /= 180;

    x *= Math.PI;
    y *= Math.PI;
    z *= Math.PI;

    this.camera.rotation.x = x;
    this.camera.rotation.y = y;
    this.camera.rotation.z = z;
};

/**
 * Redraws the view.
 */
View.prototype.render = function () {
    this.renderer.render(this.scene, this.camera);
    iagui.draw();
};

View.prototype.mouseMesh = function(event) {
    // Update the mouse position.
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

    // Find intersections by casting a ray from the origin to the mouse position.
    var vector = new THREE.Vector3(mouse.x, mouse.y, 0.5);
    projector.unprojectVector(vector, this.camera);
    var pos = this.camera.position;
    var ray = new THREE.Raycaster(pos, vector.sub(pos).normalize());

    // This is an array of all objects in the scene that the ray intersected.
    var intersects = ray.intersectObjects(this.scene.children);

    // Click the system.
    if (intersects.length !== 0) {
        return intersects[0].object;
    }

    else {
        return null;
    }
};

/**
 * Called when the view is clicked. If the mouse click position was within the GUI, we let
 * the IAGUI handle the click. If not, we project a ray from the mouse position to the game
 * world and look for an intersected object. If there is a match, then we call the View's
 * "onMeshClick" method with the mesh's object's userData.
 */
View.prototype.onclick = function (event) {
    // Click the system.
    clicked = this.mouseMesh(event);
    if (clicked === null) {
        return;
    }
    this.onMeshClick(clicked.userData);
};

View.prototype.onmousedown = function(event) {
    // See if we clicked on the gui.
    if (iagui.onmousedown(event)) {
        return;
    }
};

View.prototype.onmouseup = function(event) {

};

View.prototype.mousehover = function (event) {
    above = this.mouseMesh(event);

    if (above === null) {
        return;
    }

    else {
        this.onMeshHover(event.clientX, event.clientY, above.userData);
    }
};

var galaxyMap = null;
var systemView = null;

var systems;

/**************************************************************************************************
                                    GALAXY MAP DISPLAY FUNCTIONS
**************************************************************************************************/

function galaxyMapSetup () {
    galaxyMap.setCameraPosition(0, 50, 0);
    galaxyMap.setCameraRotation(-90, 0, 0);

    galaxyMap.onMeshClick = createSystemView;
    galaxyMap.onMeshHover = galaxyMapHover;
    objects = [];

    galaxyMap.show();
    systemView.hide();
}

function createGalaxyMap (startSystems) {
    var a = 0;
    var len = startSystems.length;

    galaxyMapSetup();

    for (a = 0; a < len; a++) {
        var system = startSystems[a];

        var x = system.x;
        var y = system.z;
        var z = system.y;

        var sphere = new THREE.SphereGeometry(system.star_size / 2, 20, 20);
        var mat = new THREE.MeshBasicMaterial( {
            color: spectralClassColor(system.star_spectral_class)
        });
        var mesh = new THREE.Mesh(sphere, mat);

        galaxyMap.scene.add(mesh);
        objects.push(mesh);
        mesh.position = new THREE.Vector3(x * 3, y * 3, z * 3);
        mesh.userData = system;
    }
}

/**
 * Takes in a Galaxy Map position (a 3D vector measured in lightyears) and outputs a Vector3 of
 * that position in the 3D game board space.
 */
function galaxyMapWorldToGrid (pos) {
    var x = pos.x;
    var y = pos.y;
    var z = pos.z;

    return new THREE.Vector3(x / 2.0, y / 2.0, z / 2.0);
}

var galaxyMapRender = function () {
    requestAnimationFrame(galaxyMapRender);
    galaxyMap.render();
};

/**************************************************************************************************
                                 GALAXY MAP INTERACTION FUNCTIONS
**************************************************************************************************/

/*
 * Called when the server confirms that we have discovered new systems in the galaxy. This function
 * creates new star meshes for said systems and adds them to the Galaxy Map scene.
 */
function updateGalaxyMap (newSystems) {

}

/**
 * Called when the User presses and holds a key while in the Galaxy Map view. Moves the camera
 * according to the keys pressed.
 */
function galaxyMapKeyboard (keyCode) {
    var goForward = (keyCode === document.keyCodes.upArrow || keyCode === document.keyCodes.w);
    var goLeft = (keyCode === document.keyCodes.leftArrow || keyCode === document.keyCodes.a);
    var goBackward = (keyCode === document.keyCodes.downArrow || keyCode === document.keyCodes.s);
    var goRight = (keyCode === document.keyCodes.rightArrow || keyCode === document.keyCodes.d);

    galaxyMapMove(goForward, goLeft, goBackward, goRight);
}

/**
 * Called when the user has the mouse in the top/bottom/right/left 10% of the screen. Moves the
 * galaxy map camera in that direction.
 */
function galaxyMapMouseHover (x, y) {
    var sWidth = window.innerWidth;
    var sHeight = window.innerHeight;

    var topPart = ((y / sHeight) >= 0.1);
    var leftPart = ((x / sWidth) <= 0.1);
    var bottomPart = ((y / sHeight) >= 0.9);
    var rightPart = ((x / sWidth) <= 0.1);

    galaxyMapMove(topPart, leftPart, bottomPart, rightPart);
}

/**
 * Moves the camera according to the given boolean directions.
 *
 * Parameters:
 *      goForward (boolean):
 *
 *      goLeft (boolean):
 *
 *      goBackward (boolean):
 *
 *      goRight (boolean):
 *
 * Returns:
 *      Nothing.
 */
function galaxyMapMove (goForward, goLeft, goBackward, goRight) {
    if (goForward) {
        // TODO
    }

    else if (goLeft) {
        // TODO
    }

    else if (goBackward) {
        // TODO
    }

    else if (goRight) {
        // TODO
    }
}

function galaxyMapHover (x, y, above) {
    // Draw the tooltip on the star.
    var starName = above.name;
    iagui.drawTooltip(x, y, starName);
}

/**************************************************************************************************
                                       SYSTEM VIEW FUNCTIONS
**************************************************************************************************/

// Global variables
var systemViewTheta = 0.0;
var systemViewPlanets = [];

function systemViewSetup () {
    systemView.setCameraPosition(0, 50, 0);
    systemView.setCameraRotation(-90, 0, 0);

    objects = [];
    systemViewPlanets = [];
}

/**
 * Given a dictionary that represents a solar system, this function creates a scene based on said
 * dictionary.
 */
function createSystemView (system) {
    // Declare iteration/loop variables.
    var a = 0;
    var len = system.planets.length;

    // Create the mesh for the system's star.
    var starSize = system.star_size * 5;
    var starSphere = new THREE.SphereGeometry(starSize, 20, 20);
    var starMat = new THREE.MeshBasicMaterial( {
        color: spectralClassColor(system.star_spectral_class)
    });
    var starMesh = new THREE.Mesh(starSphere, starMat);

    systemViewSetup();

    // Add the mesh to the scene.
    systemView.scene = new THREE.Scene();
    systemView.scene.add(starMesh);
    starMesh.position = new THREE.Vector3(0, 0, 0);

    // Setup star render pass.
    // TODO

    for (a = 0; a < len; a++) {
        var planet = new Planet(system.planets[a]);
        planet.parentSize = starSize;

        // Calculate the initial cartesian position of this planet.
        var pos = planet.position(0, systemViewTheta);
        var x = pos[0];
        var y = pos[1];

        var size = Math.log(Math.E * planet.size) + 0.5 * (1 - planet.size);
        var planetSphere = new THREE.SphereGeometry(size, 20, 20);
        var planetMat = new THREE.MeshBasicMaterial( {
            color: 0x0000ff
        });
        var planetMesh = new THREE.Mesh(planetSphere, planetMat);

        objects.push(planetMesh);
        systemViewPlanets.push(planetMesh);

        systemView.scene.add(planetMesh);

        planetMesh.position = new THREE.Vector3(x, 0, y);
        planetMesh.userData = planet;
    }

    // Swap out the views.
    galaxyMap.hide();
    systemView.show();
    animateSystemView();
}

/**
 * Called every frame of the system view. Adjusts planet orbit, star luminoscity, and other
 * details that make the game come alive.
 */
var systemViewRender = function () {
    var a = 0;

    systemViewTheta += 0.002;

    for (a = 0; a < systemViewPlanets.length; a++) {
        var planetMesh = systemViewPlanets[a];
        var planetObj = systemViewPlanets[a].userData;

        var pos = planetObj.position(0, systemViewTheta);
        var x = pos[0];
        var y = pos[1];

        planetMesh.position.x = x;
        planetMesh.position.z = y;
    }

    systemView.render();
};

function animateSystemView () {
    requestAnimationFrame(animateSystemView);
    systemViewRender();
}

/**************************************************************************************************
                                  MANAGE PLANET FUNCTIONS
**************************************************************************************************/

function showManagePlanet (planet) {

}

/**************************************************************************************************
                                       SCENE SETUP
**************************************************************************************************/

$(document).ready(function () {
    // Setup the projector.
    projector = new THREE.Projector();

    // Create the views.
    galaxyMap = new View();
    systemView = new View();

    // Update aspect ratio.
    $(window).resize(function () {
        aspectRatio = (window.innerWidth / window.innerHeight);
    });

    // Get the canvas that we will draw the GUI on.
    var canvas = document.getElementById('iagui');
    var dragCanvas = document.getElementById('drag');
    var tooltipCanvas = document.getElementById('tooltip');
    iagui = new IAGUI(canvas, dragCanvas, tooltipCanvas, 0); // TODO faction is always ISCA

    $.ajax({
        type : 'POST',
        url : '/game/galaxy/entire',
        data : {
            'game' : gameId
        },
        success: function(fromServer) {
            var j = JSON.parse(fromServer);
            systems = j.galaxy;
            createGalaxyMap(j.galaxy);
            galaxyMapRender();
        }
    });
});
