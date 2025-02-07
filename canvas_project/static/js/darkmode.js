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
    const setStoredTheme = (theme) => localStorage.setItem("theme", theme);

    const getPreferredTheme = () => {
        const storedTheme = getStoredTheme();
        if (!storedTheme) {
            return "auto";
        }

        return storedTheme;
    };

    const setTheme = (theme) => {
        if (theme === "auto") {
            document.documentElement.setAttribute(
                "data-bs-theme",
                window.matchMedia("(prefers-color-scheme: dark)").matches
                    ? "dark"
                    : "light"
            );
        } else {
            document.documentElement.setAttribute("data-bs-theme", theme);
        }
    };

    setTheme(getPreferredTheme());

    const showActiveTheme = (theme) => {
        const themeSwitcher = document.getElementById("mode-toggle");

        if (!themeSwitcher) {
            return;
        }

        switch (theme) {
            case "light":
                themeSwitcher.innerHTML =
                    "<i class='bi bi-brightness-high'></i> light";
                break;
            case "dark":
                themeSwitcher.innerHTML =
                    "<i class='bi bi-moon-stars'></i> dark";
                break;
            default:
                themeSwitcher.innerHTML =
                    "<i class='bi bi-circle-half'></i> auto";
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

        const toggle = document.getElementById("mode-toggle");

        if (!toggle) {
            return;
        }

        toggle.addEventListener("click", () => {
            var theme;
            switch (getStoredTheme()) {
                case "light":
                    theme = "dark";
                    break;
                case "dark":
                    theme = "auto";
                    break;
                default:
                    theme = "light";
                    break;
            }

            setStoredTheme(theme);
            setTheme(theme);
            showActiveTheme(theme);
        });
    });
})();
