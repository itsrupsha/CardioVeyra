
(function () {
  const key = "cardioveyra-theme";
  const root = document.documentElement;

  function apply(theme) {
    root.setAttribute("data-theme", theme);
    const buttons = document.querySelectorAll("[data-theme-toggle]");
    buttons.forEach(btn => {
      const dark = theme === "dark";
      btn.setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode");
      const icon = btn.querySelector(".theme-icon");
      const label = btn.querySelector(".theme-label");
      if (icon) icon.textContent = dark ? "☀" : "☾";
      if (label) label.textContent = dark ? "Light" : "Dark";
    });
  }

  const saved = localStorage.getItem(key);
  apply(saved || "dark");

  document.addEventListener("click", function (event) {
    const btn = event.target.closest("[data-theme-toggle]");
    if (!btn) return;
    const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    localStorage.setItem(key, next);
    apply(next);
  });
})();
