import { returnStatusCheck } from '../Services/authService';

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
 * @param {string} authentication   token supplied by HOC like useRecaptcha
 *    when it wraps the calling function
 * @param {Object} param2  an object holding the other named parameters,
 *    i.e. the ones not being passed through from a HOC
 * @param {string}  param2.formId   the id of the submitting form
 * @param {Object}  param2.fieldSet object with form field names as keys
 *    values are [corresponding state object, corresponding state setter]
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

const sendFormRequest = (token,
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
    let requestArgs = {};
    Object.keys(fieldSet).forEach(key => {
      let myval = document.getElementById(formId).elements[key].value;
      if ( !fieldSet[key][0] && !!myval ) {
        fieldSet[key][1](myval);
        requestArgs[key] = myval;
      } else {
        requestArgs[key] = fieldSet[key][0]
      }
    })
    if ( extraArgs.includes("token") ) {
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

export {
    sendFormRequest
}