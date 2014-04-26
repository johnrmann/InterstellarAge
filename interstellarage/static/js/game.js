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
var targetList = [];
var mouse = {
    x : 0,
    y : 0
};

var currentView = null;

function View () {
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(75, aspectRatio, 0.1, 1000);
    this.renderer = new THREE.WebGLRenderer();

    this.onMeshClick = null;

    // Methods
    this.show = null;
    this.hide = null;
    this.setCameraPosition = null;
    this.cameraPositionLerp = null;
    this.setCameraRotation = null;

    // Events
    this.onclick = null;
}

View.prototype.show = function () {
    currentView = this;

    this.renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(this.renderer.domElement);

    this.renderer.domElement.onclick = this.onclick;
};

View.prototype.hide = function () {

};

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

View.prototype.onclick = function (event) {
    // Update the mouse position.
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

    // Find intersections by casting a ray from the origin to the mouse position.
    var vector = new THREE.Vector3(mouse.x, mouse.y, 1);
    projector.unprojectVector(vector, this.camera);
    var pos = this.camera.position;
    var ray = new THREE.Raycaster(pos, vector.sub(pos).normalize());

    // This is an array of all objects in the scene that the ray intersected.
    var intersects = ray.intersectObjects(targetList);
    var clicked = intersects[0];

    // Click the system.
    this.onMeshClick(clicked.userData);
};

var galaxyMap = new View();
var systemView = new View();

var systems;

/**************************************************************************************************
                                    GALAXY MAP DISPLAY FUNCTIONS
**************************************************************************************************/

function galaxyMapSetup () {
    galaxyMap.setCameraPosition(0, 40, 0);
    galaxyMap.setCameraRotation(-90, 0, 0);

    galaxyMap.onMeshClick = createSystemView;

    galaxyMap.show();
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

        var size = system.size;

        var sphere = new THREE.SphereGeometry(size, 20, 20);
        var mat = new THREE.MeshBasicMaterial( {color: 0xffff00 });
        var mesh = new THREE.Mesh(sphere, mat);

        galaxyMap.scene.add(mesh);
        mesh.position = new THREE.Vector3(x * 2, y * 2, z * 2);
        mesh.userData = system;
    }
}

function galaxyMapWorldToGrid (pos) {
    var x = pos.x;
    var y = pos.y;
    var z = pos.z;

    return new THREE.Vector3(x / 2.0, y / 2.0, z / 2.0);
}

var galaxyMapRender = function () {
    requestAnimationFrame(galaxyMapRender);
    galaxyMap.renderer.render(galaxyMap.scene, galaxyMap.camera);
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

function galaxyMapKeyboard (keyCode) {
    var goForward = (keyCode === document.keyCodes.upArrow || keyCode === document.keyCodes.w);
    var goLeft = (keyCode === document.keyCodes.leftArrow || keyCode === document.keyCodes.a);
    var goBackward = (keyCode === document.keyCodes.downArrow || keyCode === document.keyCodes.s);
    var goRight = (keyCode === document.keyCodes.rightArrow || keyCode === document.keyCodes.d);
}

function galaxyMapMouseHover () {

}

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

/**************************************************************************************************
                                       SYSTEM VIEW FUNCTIONS
**************************************************************************************************/

function createSystemView (system) {
    console.log("creating system");
    var a = 0;
    var len = system.planets.length;

    // Create the mesh for the system's star.
    var starSphere = new THREE.SphereGeometry(1, 20, 20);
    var mat = new THREE.MeshBasicMaterial( {color: 0xffff00 });
    var starMesh = new THREE.Mesh(sphere, mat);

    // Add the mesh to the scene.
    systemView.scene.add(starMesh);
    starMesh.position = new THREE.Vector3(0, 0, 0);

    for (a = 0; a < len; a++) {
        var planet = system.planets[a];
    }

    // Swap out the views.
    galaxyMap.hide();
    systemView.show();
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

    // Update aspect ratio.
    $(window).resize(function () {
        aspectRatio = (window.innerWidth / window.innerHeight);
    });

    $.ajax({
        type : 'POST',
        url : '/game/galaxy/entire',
        data : {
            'game' : gameId
        },
        success: function(fromServer) {
            var j = JSON.parse(fromServer);
            createGalaxyMap(j.galaxy);
            galaxyMapRender();
        }
    });
});
