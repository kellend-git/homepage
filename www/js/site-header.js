(() => {
  function trackHomepageSection(header) {
    const primaryNav = header.querySelector(".site-primary-nav");
    const workNav = header.querySelector(".site-work-nav");
    const sections = [...primaryNav.querySelectorAll(".site-primary-links a")].map((link) => ({
      link,
      section: document.getElementById(link.hash.slice(1)),
    }));
    let active;
    let frame = 0;

    const update = () => {
      frame = 0;
      // Measure from the primary row so appearing and disappearing never move the threshold.
      const readingLine = primaryNav.getBoundingClientRect().bottom + workNav.offsetHeight + 20;
      const next = sections.find(({ section }) => {
        const { top, bottom } = section.getBoundingClientRect();
        return top <= readingLine && bottom > readingLine;
      });
      if (next === active) return;

      active?.link.removeAttribute("aria-current");
      next?.link.setAttribute("aria-current", "location");
      active = next;

      const showWork = active?.section.id === "work";
      if (!showWork && workNav.contains(document.activeElement)) {
        (active?.link ?? sections[0].link).focus({ preventScroll: true });
      }
      workNav.inert = !showWork;
      header.classList.toggle("site-work-visible", showWork);
    };
    const scheduleUpdate = () => {
      if (!frame) frame = requestAnimationFrame(update);
    };

    window.addEventListener("scroll", scheduleUpdate, { passive: true });
    window.addEventListener("resize", scheduleUpdate);
    window.addEventListener("pageshow", scheduleUpdate);
    scheduleUpdate();
  }

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

    const homeHeader = document.querySelector(".site-home-header");
    if (homeHeader) trackHomepageSection(homeHeader);

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
