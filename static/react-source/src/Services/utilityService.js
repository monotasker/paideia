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

/**
 * React HOC that provides recaptcha integration to the wrapped component
 *
 * The wrapped component is provided with a `submitAction` prop.
 * Any call to a server action wrapped with submitAction() will be
 * protected by recaptcha v3 and will receive the extra `token` argument
 * to pass on to the server call.
 *
 *
 * @component
 * @param {JSX.Element} Component the component to be decorated
 * @param {object} props this component's properties
 * @param {string} props.rkey a valid recaptcha v. 3 site key
 * @param {function} props.actionName a function making a server request that
 *                                    will be protected by recaptcha
 * @returns {JSX.Element} A react component with an extra `submitAction`
 *                        prop
 */
const withRecaptcha = Component => ({rkey=recaptchaKey,
                                     actionName=null,
                                     ...throughProps}) => {
  useEffect(() => {
    loadScriptByURL("recaptcha-key",
        `https://www.google.com/recaptcha/api.js?render=${rkey}`, function () {
            console.log("Recaptcha Script loaded!");
        }
    );
  }, []);

  const submitAction = (event, myAction) => {
    event.preventDefault();
    window.grecaptcha.ready(() => {
        window.grecaptcha.execute(rkey, { action: actionName })
        .then(token => { myAction(token); });
    });
  }

  return (
    <Component submitAction={submitAction} {...throughProps} />
  )
}

export {
    loadScriptByURL,
    useQuery,
    withRecaptcha
}

