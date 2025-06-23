/*!
 * Color mode toggler for Bootstrap's docs (https://getbootstrap.com/)
 * Copyright 2011-2024 The Bootstrap Authors
 * Licensed under the Creative Commons Attribution 3.0 Unported License.
 *
 * Updated to fit own purposes.
 */

(() => {
  "use strict";

  const getStoredTheme = () => localStorage.getItem("theme");
  const setStoredTheme = (/** @type{String} */ theme) =>
    localStorage.setItem("theme", theme);

  const getPreferredTheme = () => {
    const storedTheme = getStoredTheme();
    if (!storedTheme) {
      return "auto";
    }

    return storedTheme;
  };

  const setTheme = (/** @type{String} */ theme) => {
    if (theme === "auto") {
      document.documentElement.setAttribute(
        "data-bs-theme",
        window.matchMedia("(prefers-color-scheme: dark)").matches
          ? "dark"
          : "light",
      );
    } else {
      document.documentElement.setAttribute("data-bs-theme", theme);
    }
  };

  setTheme(getPreferredTheme());

  const showActiveTheme = (/** @type{String} */ theme) => {
    const themeSelect = document.getElementById("theme-select");

    if (!themeSelect) {
      return;
    }

    switch (theme) {
      case "light":
        //@ts-ignore
        themeSelect.value = "light";
        break;
      case "dark":
        //@ts-ignore
        themeSelect.value = "dark";
        break;
      default:
        //@ts-ignore
        themeSelect.value = "auto";
        break;
    }
  };

  window
    .matchMedia("(prefers-color-scheme: dark)")
    .addEventListener("change", () => {
      const storedTheme = getStoredTheme();
      if (storedTheme !== "light" && storedTheme !== "dark") {
        setTheme(getPreferredTheme());
      }
    });

  window.addEventListener("DOMContentLoaded", () => {
    showActiveTheme(getPreferredTheme());

    const themeSelect = document.getElementById("theme-select");

    if (!themeSelect) {
      return;
    }

    themeSelect.addEventListener("change", () => {
      //@ts-ignore
      var theme = themeSelect.value;
      setStoredTheme(theme);
      setTheme(theme);
      showActiveTheme(theme);
    });
  });
})();
