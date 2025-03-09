document.addEventListener("DOMContentLoaded", function () {
    console.log("Admin Dashboard Loaded");
  
    // Sidebar Toggle Functionality
    const sidebar = document.querySelector(".sidebar");
    const mainContent = document.querySelector(".main-content");
    const topNav = document.querySelector(".top-nav");
    const toggleButton = document.createElement("button");
  
    toggleButton.textContent = "☰";
    toggleButton.classList.add("toggle-sidebar");
    document.body.appendChild(toggleButton);
  
    toggleButton.addEventListener("click", function () {
      sidebar.classList.toggle("collapsed");
      mainContent.classList.toggle("collapsed");
      topNav.classList.toggle("collapsed");
    });
  
    // Ensure sidebar doesn't overlap content on collapse
    function adjustLayout() {
      if (sidebar.classList.contains("collapsed")) {
        sidebar.style.width = "60px";
        mainContent.style.marginLeft = "60px";
        topNav.style.left = "60px";
        topNav.style.width = "calc(100% - 60px)";
      } else {
        sidebar.style.width = "250px";
        mainContent.style.marginLeft = "250px";
        topNav.style.left = "250px";
        topNav.style.width = "calc(100% - 250px)";
      }
    }
  
    toggleButton.addEventListener("click", adjustLayout);
  
    // Sidebar Navigation Active State
    let links = document.querySelectorAll(".sidebar .nav-link");
    links.forEach(link => {
      link.addEventListener("click", function () {
        links.forEach(l => l.classList.remove("active"));
        this.classList.add("active");
      });
    });
  
    // Alerts Auto-dismiss
    let alerts = document.querySelectorAll(".alerts li");
    alerts.forEach(alert => {
      setTimeout(() => {
        alert.style.opacity = "0";
        setTimeout(() => alert.remove(), 500);
      }, 5000);
    });
  
    // Interactive Table Row Clicks
    let rows = document.querySelectorAll("table tbody tr");
    rows.forEach(row => {
      row.addEventListener("click", function () {
        let actionLink = this.querySelector("td a");
        if (actionLink) {
          window.location.href = actionLink.href;
        }
      });
    });
  
    // Initial layout adjustment
    adjustLayout();
  });
  