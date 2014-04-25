/*
 * Requires:
 * 		- THREE.js
 *		- jquery
 *      - orders.js
 */

var galaxyMap = {
	camera : null,
	scene : null,
	renderer : null,
	onSystemClick : null,
	onKeyboard : null
};

var systemView = {
	scene : null,
	camera : null,
	renderer: null
};

var projector;
var targetList = [];
var mouse = {
	x : 0,
	y : 0
};

var systems;

/**************************************************************************************************
                                       GALAXY MAP FUNCTIONS
**************************************************************************************************/

function galaxyMapSetup () {
	var aspectRatio = (window.innerWidth / window.innerHeight);

	galaxyMap.scene = new THREE.Scene();
	galaxyMap.camera = new THREE.PerspectiveCamera(75, aspectRatio, 0.1, 1000);

	galaxyMap.renderer = new THREE.WebGLRenderer();
	galaxyMap.renderer.setSize(window.innerWidth, window.innerHeight);
	document.body.appendChild(galaxyMap.renderer.domElement);

	galaxyMap.camera.position.y = 60;
	galaxyMap.camera.rotation.x = (Math.PI / 2) * -1;

	galaxyMap.onSystemClick = createSystemView;

	// The projector performs world/screen calculations.
	projector = new THREE.Projector();
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

		var sphere = new THREE.SphereGeometry(1, 20, 20);
		var mat = new THREE.MeshBasicMaterial( {color: 0xffff00 });
		var mesh = new THREE.Mesh(sphere, mat);

		galaxyMap.scene.add(mesh);
		mesh.position = new THREE.Vector3(x * 2, y * 2, z * 2);
		mesh.userData = system;
	}
}

/*
 * Args:
 *		onSystemClick (system -> void): A function whose sole parameter is a system object. This
 *			function is called whenever the user clicks on a solar system.
 */
function showGalaxyMap (onSystemClick) {
	galaxyMap.onSystemClick = onSystemClick;
	document.body.appendChild(galaxyMap.renderer.domElement);
}

/*
 * Called when the user enters the System View -- we hide the galaxy map.
 */
function hideGalaxyMap () {

}

/*
 * Called when the user clicks the mouse while in the Galaxy Map. If the user clicked on a system,
 * then he/she is taken to the System View for that system (if the planets in that system have been
 * discovered).
 */
function galaxyMapClick (event) {
	// Update the mouse position.
	mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
	mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

	// Find intersections by casting a ray from the origin to the mouse position.
	var vector = new THREE.Vector3(mouse.x, mouse.y, 1);
	projector.unprojectVector(vector, galaxyMap.camera);
	var pos = galaxyMap.camera.position;
	var ray = new THREE.Raycaster(pos, vector.sub(pos).normalize());

	// This is an array of all objects in the scene that the ray intersected.
	var intersects = ray.intersectObjects(targetList);
	var clicked = intersects[0];

	// Click the system.
	galaxyMap.onSystemClick(clicked.userData);
}

/*
 * Called when the server confirms that we have discovered new systems in the galaxy. This function
 * creates new star meshes for said systems and adds them to the Galaxy Map scene.
 */
function updateGalaxyMap (newSystems) {

}

var galaxyMapRender = function () {
	requestAnimationFrame(galaxyMapRender);
	galaxyMap.renderer.render(galaxyMap.scene, galaxyMap.camera);
};

/**************************************************************************************************
                                       SYSTEM VIEW FUNCTIONS
**************************************************************************************************/

function createSystemView (system) {
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
}

// TODO
function systemViewPlanetClicked (event) {
	// Update the mouse position.
	mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
	mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
}

/**************************************************************************************************
                                       SCENE SETUP
**************************************************************************************************/

createGalaxyMap([
	{
		name : "Solar System",
		x : 0,
		y : 0,
		z : 0
	},

	{
		name : "Proxima Centauri",
		x : 4,
		y : 0,
		z : 0
	}
]);
galaxyMapRender();