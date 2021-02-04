import React, { useEffect } from "react";
import { useLocation } from "react-router-dom";
import { recaptchaKey } from "../variables";

/**
 * Load scripts dynamically as needed by a component
 *
 * @param {string} id the id of the script element that
 *                    will load the desired script.
 * @param {string} url the url for the script to be loaded.
 * @param {function} callback a callback function to be run after
 *                            the script has been loaded
 */
const loadScriptByURL = (id, url, callback) => {
    const isScriptExist = document.getElementById(id);

    if (!isScriptExist) {
    var script = document.createElement("script");
    script.type = "text/javascript";
    script.src = url;
    script.id = id;
    script.onload = function () {
        if (callback) callback();
    };
    document.body.appendChild(script);
    }

    if (isScriptExist && callback) callback();
}

/**
 * Provides the url search parmeters for the current page
 * in a component using react-router.
 *
 * @returns {object} an object consisting of the url search params
 */
const useQuery = () => {
  return new URLSearchParams(useLocation().search);
}


export {
    loadScriptByURL,
    useQuery
}

