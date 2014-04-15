var scene;
var camera;
var renderer;

var systems;

function setup () {
	var aspectRatio = (window.innerHeight / window.innerWidth);

	scene = new THREE.Scene();
	camera = new THREE.PerspectiveCamera(75, aspectRatio, 0.1, 1000);

	renderer = new THREE.WebGLRenderer();
	renderer.setSize(window.innerWidth, window.innerHeight);
	document.body.appendChild(renderer.domElement);

	camera.position.z = 5;
}

function createGalaxyMap (startSystems) {
	var a = 0;
	var len = startSystems.length;

	setup();

	for (a = 0; a < len; a++) {
		var system = startSystems[a];

		var x = system.x;
		var y = system.z;
		var z = system.y;

		var sphere = new THREE.SphereGeometry(1, 7, 7);
		var mat = new THREE.MeshBasicMaterial( {color: 0xffff00 });
		var mesh = new THREE.Mesh(sphere, mat);

		scene.add(mesh);
		mesh.position = new THREE.Vector3(x, y, z);
	}
}

function updateGalaxyMap (newSystems) {

}

var render = function () {
	requestAnimationFrame(render);
	renderer.render(scene, camera);
};

createGalaxyMap([
	{
		x : 0,
		y : 0,
		z : 0
	}
]);
render();