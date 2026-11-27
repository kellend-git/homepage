(() => {
  const root = document.documentElement;
  const systemTheme = window.matchMedia("(prefers-color-scheme: dark)");
  const savedTheme = () => {
    try {
      return localStorage.getItem("theme");
    } catch {
      return null;
    }
  };

  root.dataset.theme = savedTheme() || (systemTheme.matches ? "dark" : "light");
  document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.querySelector(".site-theme-toggle");
    const themeColor = document.querySelector('meta[name="theme-color"]');
    const applyTheme = (theme) => {
      const dark = theme === "dark";
      root.dataset.theme = theme;
      toggle.setAttribute("aria-checked", String(dark));
      toggle.setAttribute("aria-label", `Color theme: ${dark ? "Dark" : "Light"}. Switch to ${dark ? "light" : "dark"} mode`);
      themeColor?.setAttribute("content", dark ? "#07111f" : "#075cd6");
    };

    applyTheme(root.dataset.theme);
    toggle.addEventListener("click", () => {
      const theme = root.dataset.theme === "dark" ? "light" : "dark";
      applyTheme(theme);
      try { localStorage.setItem("theme", theme); } catch {}
    });
    systemTheme.addEventListener("change", (event) => {
      if (!savedTheme()) applyTheme(event.matches ? "dark" : "light");
    });

    const menu = document.querySelector(".site-resume-details");
    document.addEventListener("click", (event) => {
      if (menu.open && !menu.contains(event.target)) menu.open = false;
    });
    menu.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && menu.open) {
        menu.open = false;
        menu.querySelector("summary").focus();
      }
    });

    const printableDetails = [...document.querySelectorAll("#selected-work details")];
    let closedBeforePrint = [];
    window.addEventListener("beforeprint", () => {
      closedBeforePrint = printableDetails.filter((item) => !item.open);
      closedBeforePrint.forEach((item) => { item.open = true; });
    });
    window.addEventListener("afterprint", () => {
      closedBeforePrint.forEach((item) => { item.open = false; });
    });
  });
})();
