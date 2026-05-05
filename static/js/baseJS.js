const purpleIcon = document.getElementById("purpleIcon");
const purpleX = document.getElementById("purpleX");
const hamburger = document.querySelector(".hamburger");
const menuContainer = document.querySelector(".menuContainer");
const menuLinks = document.querySelectorAll(".menuLink");

hamburger.addEventListener("click", toggleMenu);

function toggleMenu() {
	
	if (menuContainer.classList.contains("open")) {
		menuContainer.classList.remove("open");
		purpleX.style.display = "none";
		purpleIcon.style.display = "block";
	
	} else {
		menuContainer.classList.add("open");
		purpleX.style.display = "block";
		purpleIcon.style.display = "none";
	}
}

menuLinks.forEach(
	function(menuLink) {
		menuLink.addEventListener("click", toggleMenu);
	}
)