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

const doApiCall = async (payload, apiFunction,
                         format="none", method="POST") => {
  console.log(`method: ${method}`);
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
  console.log(callObject);
  let response = await fetch(`/paideia/api/${apiFunction}`, callObject);
  let mydata;
  try {
    mydata = await response.json();
  } catch(err) {
    mydata = {status: "internal server error",
              reason: "Unknown error in function do_password_reset",
              error: err.message}
  }
  mydata.status_code = response.status;
  return mydata;
}

function returnStatusCheck(mydata, history, action, reducer,
                           otherActions={}) {
  if ( mydata.status_code === 200 ) {
    action(mydata);
  } else if ( mydata.status_code === 400 ) {
    console.log('400: Bad request');
    if ( otherActions.hasOwnProperty("badRequestAction") ) {
      otherActions.badRequestAction(mydata);
    }
  } else if ( mydata.status_code === 401 ) {
    if ( mydata.reason === "Not logged in" ) {
      console.log('401: Not logged in');
      if ( otherActions.hasOwnProperty("unauthorizedAction")) {
        otherActions.unauthorizedAction(mydata);
      } else {
        reducer({type: 'deactivateUser', payload: null});
        history.push(`login`);
      }
    } else if ( mydata.reason === "Insufficient privileges" ) {
      console.log('401: Insufficient privileges');
      if ( otherActions.hasOwnProperty("insufficientPrivilegesAction") ) {
        otherActions.insufficientPrivilegesAction(mydata);
      }
    } else if ( mydata.reason === "Login failed" ) {
      console.log('401: Login failed');
      otherActions.unauthorizedAction(mydata);
    } else if ( mydata.reason === "Action blocked") {
      console.log('401: Action blocked');
      otherActions.actionBlockedAction(mydata);
    }
  } else if ( mydata.status_code === 404 ) {
    console.log('404: No such record');
    if ( otherActions.hasOwnProperty("noRecordAction") ) {
      otherActions.noRecordAction(mydata);
    }
  } else if ( mydata.status_code === 409 ) {
    console.log('409: Conflict');
    if ( otherActions.hasOwnProperty("dataConflictAction") ) {
      console.log('taking conflict action');
      otherActions.dataConflictAction(mydata);
    }
  } else if ( mydata.status_code === 500 ) {
    console.log('500: Internal server error');
    if ( otherActions.hasOwnProperty("serverErrorAction") ) {
      otherActions.serverErrorAction(mydata);
    }
  } else {
    console.log('Uncaught problem in returnStatusCheck:');
    console.log(mydata);
  }
}

export {
    loadScriptByURL,
    useQuery,
    doApiCall,
    returnStatusCheck
}