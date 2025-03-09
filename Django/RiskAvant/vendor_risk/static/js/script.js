document.addEventListener("DOMContentLoaded", function () {
    const sections = document.querySelectorAll(".section");
    const navLinks = document.querySelectorAll(".sidebar .nav-link");

    function activateSection() {
        let scrollPosition = window.scrollY + 100; // Adjust for navbar height

        sections.forEach((section) => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            const sectionId = section.getAttribute("id");

            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                navLinks.forEach((link) => link.classList.remove("active"));

                // Select the correct nav link based on href
                const activeLink = document.querySelector(`.sidebar a[href="#${sectionId}"]`);
                if (activeLink) {
                    activeLink.classList.add("active");
                }
            }
        });
    }

    window.addEventListener("scroll", activateSection);

    // Smooth scrolling for navigation
    navLinks.forEach((link) => {
        link.addEventListener("click", function (event) {
            event.preventDefault();
            const targetId = this.getAttribute("href").substring(1);
            const targetSection = document.getElementById(targetId);

            if (targetSection) {
                window.scrollTo({
                    top: targetSection.offsetTop - 60, // Adjust for navbar height
                    behavior: "smooth",
                });
            }
        });
    });

    // Call once to set initial active section
    activateSection();
});
