import React, {useState} from 'react';
import { returnStatusCheck } from '../Services/utilityService';

/**
 * Abstracted function to handle the server request on submission of a form
 *
 * This is designed to
 *    - check for autocompleted form data that wasn't picked up in state
 *        variables, inserting it where necessary
 *    - add to the request any expected extra arguments from HOCs
 *    - check the return status of the request and fire the appropriate callback
 *    - signal back to the calling component when the request is finished
 *
 * @param {Event} event   passed through from the form submission
 * @param {string} token    supplied by HOC like useRecaptcha
 *    when it wraps the calling function
 * @param {Object} param2  an object holding the other named parameters,
 *    i.e. the ones not being passed through from a HOC
 * @param {string}  param2.formId   the id of the submitting form
 * @param {Object}  param2.fieldSet object with form field names as keys
 *    values are the corresponding state objects
 *    note that these names must also be the argument names for the
 *    requestAction function call
 * @param {Function}  param2.requestAction  the function being called to make
 *    the server request
 * @param {list}  param2.extraArgs  list of names (strings) of extra arguments
 *    to pass through to the requestAction, usually supplied by HOC
 * @param {string}  param2.history  history object to be used by
 *    returnStatusCheck for some automatic redirections
 * @param {string}  param2.dispatch dispatch function for the user context, to
 *    be used by returnStatusCheck for some automatic login/logout
 * @param {string}  param2.formId
 * @param {string}  param2.formId  optional object holding callbacks to fire in
 *    case of various response status conditions. The keys may be:
 *      serverErrorAction, badRequestAction,
 *      dataConflictAction, unauthorizedAction
 *    values are functions to serve as callbacks in case of matching
 *    response status
 */
const sendFormRequest = (token, setFields,
                       {formId,
                        fieldSet,
                        requestAction,
                        extraArgs,
                        history,
                        dispatch,
                        successCallback,
                        otherCallbacks={},
                        setInProgressAction
                       }
                      ) => {
    setInProgressAction(true);
    // handle autocompleted form fields that aren't picked up by React state
    // console.log('formId===========');
    // console.log(formId);
    let requestArgs = {};
    Object.keys(fieldSet).forEach(key => {
      // console.log('key');
      // console.log(key);
      let mycontrol = document.getElementById(formId).elements[key]
      let myval = !!mycontrol ? mycontrol.value : undefined;

      if ( !fieldSet[key] && !!myval ) {
        setFields(myval, fieldSet[key]);
        requestArgs[key] = myval;
      } else {
        requestArgs[key] = fieldSet[key]
      }
    })
    if ( !!extraArgs && extraArgs.includes("token") ) {
      requestArgs.token = token;
    }

    requestAction(requestArgs)
    .then( respdata => {
        setInProgressAction(false);
        returnStatusCheck(respdata, history,
          (mydata) => {
            successCallback(mydata);
          },
          dispatch,
          otherCallbacks)
    })
}

/**
 * React custom hook to provide logic and state variables for handling
 * form field values in state, validating those values client-side,
 * and responding to response statuses after a form is submitted
 *
 * required args:
 *    formFields (obj)  An object whose keys are form field names and whose
 *      values (if set) are either (a) strings giving names of standard
 *      validators, or (b) custom validator functions
 *      NEW!!! value may also be an array of [validator, initial field value]
 *
 * provides formFieldValues object with two setter functions to hold values
 * for form fields with the supplied names. (These names should also be
 * the same as the back-end db table fields.)
 *
 * The setter setFormFieldValue updates a single field value and
 * does some validation in the process (like removing "missing" flag
 * if you're supplying missing value). The setFormFieldValuesDirectly
 * setter allows for direct updating of the whole formFieldValues
 * object in state.
 *
 * provides flags object with setter function. This has keys:
 *   missingRequestData (array)
 *   badRequestData (array)
 *   notLoggedIn (bool)
 *   insufficientPrivileges (bool)
 *   loginFailed (bool)
 *   recaptchaFailed (bool)
 *   actionBlocked (bool)
 *   noRecord (bool)
 *   dataConflict (bool)
 *   serverError (bool)
 *   success (bool)
 *
 * provides an object with default callback functions on each server
 * response code. The keys for this object are:
 *    missingRequestDataAction
 *    badRequestDataAction
 *    notLoggedInAction
 *    insufficientPrivilegesAction
 *    loginFailedAction
 *    recaptchaFailedAction
 *    actionBlockedAction
 *    noRecordAction
 *    dataConflictAction
 *    serverErrorAction
 *    successAction
 */
const useFormManagement = (formFields) => {
    const [ showErrorDetails, setShowErrorDetails ] = useState(false);
    const [ flags, setFlags ] = useState({missingRequestData: [],
                                          badRequestData: [],
                                          notLoggedIn: false,
                                          insufficientPrivileges: false,
                                          loginFailed: false,
                                          recaptchaFailed: false,
                                          actionBlocked: false,
                                          noRecord: false,
                                          dataConflict: false,
                                          serverError: false,
                                          success: false
                                          });
    const fieldList = Object.keys(formFields);

    const [formFieldValues, setFormFieldValuesDirectly
          ] = useState(fieldList.reduce(
            (obj, item) => {
              return {...obj, [item]: !!Array.isArray(formFields[item]) ? formFields[item][1] : null }
            }, {})
            );
    // console.log('formFieldValues is');
    // console.log(formFieldValues);

    // const _findMissingAndBadValues

    // const setAllFormFieldValues = (vals) => {
    //   setFormFieldValuesDirectly(vals);
    // }

    const setFormFieldValue = (val, fieldName) => {
      setFormFieldValuesDirectly({...formFieldValues, [fieldName]: val});
      let newFlags = { ...flags };

      console.log(`setting field ${fieldName}: ${val}`);

      // unflag missing field values if we're now entering them
      var myMissing = [...newFlags.missingRequestData ];
      const missingIndex = myMissing.indexOf(fieldName);
      // console.log(`missingIndex ${missingIndex}`);
      if (missingIndex > -1) {
        myMissing.splice(missingIndex, 1);
        newFlags.missingRequestData = myMissing;
      }

      // may be value, or may be first in array if value is array
      const validator = !!Array.isArray(formFields[fieldName]) ?
        formFields[fieldName][0] : formFields[fieldName];
      // validate email fields
      if ( validator==="email" ) {
        let myBad = [ ...newFlags.badRequestData ];
        const emailIndex = myBad.indexOf(fieldName);
        const re = /^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$/i;
        // console.log('passed email test?');
        // console.log(re.test(String(val).toLowerCase()));
        if ( !re.test(String(val).toLowerCase()) ) {
          if (emailIndex === -1) { myBad.push(fieldName); }
        } else {
          if (emailIndex > -1) { myBad.splice(emailIndex, 1); }
        }
        newFlags.badRequestData = myBad;
      }

      // validate password fields
      if ( validator==="password" ) {
        let myBad = [ ...newFlags.badRequestData ];
        const passwordIndex = myBad.indexOf(fieldName);
        const re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d!\"#\$%&'\(\)\*\+,-\.\/:;<=>\?@\[\]\\\^_`\{\|\}~]{8,20}$/;
        // console.log('passed password test?');
        // console.log(re.test(val));
        if ( !re.test(val) ) {
          if (passwordIndex === -1) { myBad.push(fieldName); }
        } else {
          if (passwordIndex > -1) { myBad.splice(passwordIndex, 1); }
        }
        newFlags.badRequestData = myBad;
      }


      // if custom validator function is passed, execute
      if ( !!validator && typeof validator==="function" ) {
        let myBad = [ ...newFlags.badRequestData ];
        if ( !validator(val) ) {
          myBad.push(fieldName);
        } else {
          const index = myBad.indexOf(fieldName);
          if (index > -1) { myBad.splice(index, 1); }
        }
        newFlags.badRequestData = myBad;
      }
      setFlags(newFlags);
      // console.log('missingRequestData is');
      // console.log(flags.missingRequestData);
      // console.log('badRequestData is');
      // console.log(flags.badRequestData);
    }

    const myCallbacks = {
        missingRequestDataAction: (data) => {
          setFlags({...flags,
                    missingRequestData: Object.keys(data.error),
                    notLoggedIn: false,
                    insufficientPrivileges: false,
                    loginFailed: false,
                    recaptchaFailed: false,
                    actionBlocked: false,
                    noRecord: false,
                    dataConflict: false,
                    serverError: false,
                    success: false
                   });
        },
        badRequestDataAction: (data) => {
          setFlags({...flags, badRequestData: Object.keys(data.error),
                    notLoggedIn: false,
                    insufficientPrivileges: false,
                    loginFailed: false,
                    recaptchaFailed: false,
                    actionBlocked: false,
                    noRecord: false,
                    dataConflict: false,
                    serverError: false,
                    success: false
          });
        },
        notLoggedInAction: () => { setFlags({...flags, notLoggedIn: true,
                                             badRequestData: [],
                                             missingRequestData: [],
                                             insufficientPrivileges: false,
                                             loginFailed: false,
                                             recaptchaFailed: false,
                                             actionBlocked: false,
                                             noRecord: false,
                                             dataConflict: false,
                                             serverError: false,
                                             success: false
          });
        },
        insufficientPrivilegesAction: () => {
          setFlags({...flags, insufficientPrivileges: true,
                    notLoggedIn: false,
                    badRequestData: [],
                    missingRequestData: [],
                    loginFailed: false,
                    recaptchaFailed: false,
                    actionBlocked: false,
                    noRecord: false,
                    dataConflict: false,
                    serverError: false,
                    success: false
          });
        },
        loginFailedAction: () => { setFlags({...flags, loginFailed: true,
                                             notLoggedIn: false,
                                             badRequestData: [],
                                             missingRequestData: [],
                                             insufficientPrivileges: false,
                                             recaptchaFailed: false,
                                             actionBlocked: false,
                                             noRecord: false,
                                             dataConflict: false,
                                             serverError: false,
                                             success: false
          });
        },
        recaptchaFailedAction: () => {
          setFlags({...flags, recaptchaFailed: true,
                    loginFailed: false,
                    notLoggedIn: false,
                    badRequestData: [],
                    missingRequestData: [],
                    insufficientPrivileges: false,
                    actionBlocked: false,
                    noRecord: false,
                    dataConflict: false,
                    serverError: false,
                    success: false
          });
        },
        actionBlockedAction: () => { setFlags({...flags, actionBlocked: true,
                                               recaptchaFailed: false,
                                               loginFailed: false,
                                               notLoggedIn: false,
                                               badRequestData: [],
                                               missingRequestData: [],
                                               insufficientPrivileges: false,
                                               noRecord: false,
                                               dataConflict: false,
                                               serverError: false,
                                               success: false
          });
        },
        noRecordAction: () => { setFlags({...flags, noRecord: true,
                                          recaptchaFailed: false,
                                          loginFailed: false,
                                          notLoggedIn: false,
                                          badRequestData: [],
                                          missingRequestData: [],
                                          insufficientPrivileges: false,
                                          actionBlocked: false,
                                          dataConflict: false,
                                          serverError: false,
                                          success: false
          });
        },
        dataConflictAction: () => { setFlags({...flags, dataConflict: true,
                                              recaptchaFailed: false,
                                              loginFailed: false,
                                              notLoggedIn: false,
                                              badRequestData: [],
                                              missingRequestData: [],
                                              insufficientPrivileges: false,
                                              actionBlocked: false,
                                              noRecord: false,
                                              serverError: false,
                                              success: false
          });
        },
        serverErrorAction: (data) => { setFlags({...flags,
                                             serverError: data.error,
                                             recaptchaFailed: false,
                                             loginFailed: false,
                                             notLoggedIn: false,
                                             badRequestData: [],
                                             missingRequestData: [],
                                             insufficientPrivileges: false,
                                             actionBlocked: false,
                                             noRecord: false,
                                             dataConflict: false,
                                             success: false
          });
        },
        successAction: () => {
          setFlags({missingRequestData: [],
                    badRequestData: [],
                    notLoggedIn: false,
                    insufficientPrivileges: false,
                    loginFailed: false,
                    recaptchaFailed: false,
                    actionBlocked: false,
                    noRecord: false,
                    dataConflict: false,
                    serverError: false,
                    success: true
                  });
        }
    }

    return {formFieldValues, setFormFieldValue, setFormFieldValuesDirectly,
            flags, setFlags, myCallbacks, showErrorDetails, setShowErrorDetails}
}

export {
    sendFormRequest,
    useFormManagement
}