import React, { useEffect } from "react";
import { useLocation } from "react-router-dom";
import { recaptchaKey, DEBUGGING } from "../variables";

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

const doApiCall = async (payload, apiFunction,
                         format="none", method="POST") => {
  // DEBUGGING && console.log(`method: ${method}`);
  let callObject = {method: method,
                    cache: "no-cache",
                    mode: "same-origin"
                   }
  switch (format) {
      case "JSON":
        callObject['headers'] = {'Content-Type': 'application/json'};
        callObject['body'] = JSON.stringify(payload);
        break;
      case "form":
        let formdata = new FormData();
        for (const [key, value] of Object.entries(payload)) {
            formdata.append(key, value);
        }
        callObject['body'] = formdata;
        break;
      default:
        break;
  }
  // DEBUGGING && console.log(callObject);
  let response = await fetch(`/paideia/api/${apiFunction}`, callObject);
  let mydata;
  try {
    mydata = await response.json();
  } catch(err) {
    mydata = {status: "internal server error",
              reason: `Unknown error in function ${apiFunction}`,
              error: err.message}.json()
  }
  mydata.status_code = response.status;
  return mydata;
}

function returnStatusCheck(mydata, history, action, reducer,
                           otherActions={}) {
  DEBUGGING && console.log(mydata);
  switch (mydata.status_code) {
    case 200:
      DEBUGGING && console.log("check succeeded!!!");
      action(mydata);
      break;

    case 400:
      // console.log('400: Bad request');
      if ( mydata.reason === 'Missing request data' ) {
        if ( otherActions.hasOwnProperty("missingRequestDataAction") ) {
                otherActions.missingRequestDataAction(mydata);
        } else if ( otherActions.hasOwnProperty("badRequestDataAction") ) {
                otherActions.badRequestDataAction(mydata);
        }
      } else if ( otherActions.hasOwnProperty("badRequestDataAction") ) {
        otherActions.badRequestDataAction(mydata);
      }
      break;

    case 401:

      if ( mydata.reason === "Not logged in" ) {
        if ( otherActions.hasOwnProperty("notLoggedInAction")) {
          otherActions.notLoggedInAction(mydata);
        } else {
          reducer({type: 'deactivateUser', payload: null});
          history.push(`login`);
        }
      } else if ( mydata.reason === "Insufficient privileges" ) {
        // console.log('401: Insufficient privileges');
        if ( otherActions.hasOwnProperty("insufficientPrivilegesAction") ) {
          otherActions.insufficientPrivilegesAction(mydata);
        }
      } else if ( mydata.reason === "Login failed" ) {
        otherActions.loginFailedAction(mydata);
      } else if ( mydata.reason === "Recaptcha failed" ) {
        otherActions.recaptchaFailedAction(mydata);
      } else if ( mydata.reason === "Action blocked") {
        otherActions.actionBlockedAction(mydata);
      }
      break;

    case 403:
      if ( otherActions.hasOwnProperty("insufficientPrivilegesAction") ) {
        otherActions.insufficientPrivilegesAction(mydata);
      }
      break;

    case 404:
      if ( otherActions.hasOwnProperty("noRecordAction") ) {
        otherActions.noRecordAction(mydata);
      }
      break;

    case 409:
      if ( otherActions.hasOwnProperty("dataConflictAction") ) {
        otherActions.dataConflictAction(mydata);
      }
      break;

    case 500:
      if ( otherActions.hasOwnProperty("serverErrorAction") ) {
        otherActions.serverErrorAction(mydata);
      }
      break;

    default:
      console.log('Uncaught problem in returnStatusCheck:');
      // console.log(mydata);
      break;
  }
}

/**
 * Filters an object to retain only the keys included in the provided list.
 *
 * @param {Object}  obj   The initial object to be filtered
 * @param {Array}   keys  An array of strings listing the keys to be retained
 *                        in the new object
 * @returns {Object} A new object consisting of the keys/values whose keys
 *                   were in the provided array
 */
const filterObjectByKeys = (obj, keys) => {
  const keyValuePairs = Object.entries(obj);
  const filteredPairs = keyValuePairs.filter(
    ([key, value]) => keys.includes(key)
  );
  return Object.fromEntries(filteredPairs);
}

/**
 * Filters an object to remove the keys included in the provided list.
 *
 * @param {Object}  obj   The initial object to be filtered
 * @param {Array}   keys  An array of strings listing the keys to be removed
 *                        from the new object
 * @returns {Object} A new object consisting of the keys/values whose keys
 *                   were NOT in the provided array
 */
const filterObjectExcludeKeys = (obj, keys) => {
  const keyValuePairs = Object.entries(obj);
  const filteredPairs = keyValuePairs.filter(
    ([key, value]) => !keys.includes(key)
  );
  return Object.fromEntries(filteredPairs);
}

/**
 * Determines whether a string's characters are a single number.
 *
 * @param {string} str The string to be tested to determine whether it is a
 *                     numeric sequence of characters
 * @returns {boolean} Returns true if the provided string is a number,
 *                    but false if it is not
 */
function isNumericString(str) {
  if (typeof str != "string") return false // we only process strings!
  return !isNaN(str) && // use type coercion to parse the _entirety_ of the string (`parseFloat` alone does not do this)...
         !isNaN(parseFloat(str)) // ...and ensure strings of whitespace fail
}


/**
 * Determines whether a string's characters represent a single integer.value.
 *
 * @param {string} str The string to be tested to determine whether it is a
 *                     numeric sequence of characters that form a single
 *                     integer value
 * @returns {boolean} Returns true if the provided string is an integer,
 *                    but false if it is not
 */
function isIntegerString(str) {
  if ( isNumericString(str) ) {
    return parseInt(str).toString()===str;
  } else {
    return false;
  }
}

/**
 * Determines whether a string is alphanumeric and the specified length.
 *
 * If no max and min specified, defaults to a maximum of 48 characters and
 * a minimum of 1.
 *
 * @param {string} str The string to be tested to determine whether it is an
 *                     alphanumeric sequence of characters of the specified
 *                     length.
 * @param {integer} max The maximum length of a valid string
 * @param {integer} min The minimum length of a valid string
 * @returns {boolean} Returns true if the provided string is alphanumeric and
 *                    the correct length, but false if it is not
 */
function isAlphanumericString(str, max=48, min=1) {
  let myreturn = false;
  const len = str.length;
  if ( len >= min && len <= max ) {
    let code;
    for (let i = 0; i < len; i++) {
      code = str.charCodeAt(i);
      if (!(code > 47 && code < 58) && // numeric (0-9)
          !(code > 64 && code < 91) && // upper alpha (A-Z)
          !(code > 96 && code < 123)) { // lower alpha (a-z)
        myreturn = false;
      } else {
        myreturn = true;
      }
    }
  }
  return myreturn;
}

export {
    loadScriptByURL,
    useQuery,
    doApiCall,
    returnStatusCheck,
    filterObjectByKeys,
    filterObjectExcludeKeys,
    isNumericString,
    isIntegerString,
    isAlphanumericString
}