/*!
 * Color mode toggler for Bootstrap's docs (https://getbootstrap.com/)
 * Copyright 2011-2024 The Bootstrap Authors
 * Licensed under the Creative Commons Attribution 3.0 Unported License.
 *
 * Updated to fit own purposes.
 */

const getStoredTheme = () => localStorage.getItem("theme");
/**
 * Sets the stored theme
 * @param {string} theme
 */
const setStoredTheme = (theme) => localStorage.setItem("theme", theme);

const getPreferredTheme = () => {
    const storedTheme = getStoredTheme();
    if (!storedTheme) {
        return "auto";
    }

    return storedTheme;
};

/**
 * @param {string} theme
 */
const showActiveTheme = (theme) => {
    const modeMenu = document.getElementById("theme-select");

    if (!modeMenu) {
        return;
    }

    switch (theme) {
        case "light":
            //@ts-ignore
            modeMenu.value = "light";
            break;
        case "dark":
            //@ts-ignore
            modeMenu.value = "dark";
            break;
        default:
            //@ts-ignore
            modeMenu.value = "auto";
            break;
    }
};

/**
 * @param {string} theme
 */
export const setTheme = (theme) => {
    setStoredTheme(theme);
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
    showActiveTheme(theme);
};

setTheme(getPreferredTheme());

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
        setTheme(theme);
    });
});
