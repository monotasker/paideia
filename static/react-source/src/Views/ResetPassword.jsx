import React, {
  useContext,
  useState
} from "react";
import {
  Alert,
  Button,
  Col,
  Collapse,
  Form,
  Row
} from "react-bootstrap";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { useHistory,
         Link
} from 'react-router-dom';

import { returnStatusCheck,
  startPasswordReset,
  doPasswordReset
} from '../Services/authService';
import { useQuery, withRecaptcha } from '../Services/utilityService';
import { UserContext } from '../UserContext/UserProvider';

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

const sendFormRequest = (event, token,
                       {formId,
                        fieldSet={},
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

    if ( "token" in Object.keys(requestArgs) ) {
      requestArgs.token = token;
    }

    requestAction()
    .then( respdata => {
        returnStatusCheck(respdata, history,
          (mydata) => {
            successCallback(mydata);
            setInProgressAction(false);
          },
          dispatch,
          otherCallbacks)
    })
}

const StartResetForm = ({submitAction}) => {
  const myhistory = useHistory();
  const { user, dispatch } = useContext(UserContext);
  const [ email, setEmail ] = useState();
  const [ missingEmail, setMissingEmail ] = useState(false);
  const [ resetFailed, setResetFailed ] = useState(false);
  const [ noSuchUser, setNoSuchUser ] = useState(false);
  const [ resetSucceeded, setResetSucceeded ] = useState(false);
  const [ requestInProgress, setRequestInProgress ] = useState(false);

  const serverErrorAction = (mydata) => {
    setRequestInProgress(false);
    setResetFailed(true);
  }

  const badRequestAction = (mydata) => {
    setRequestInProgress(false);
    if ( mydata.reason === "User does not exist" ) {
      setNoSuchUser(true);
    } else {
      setMissingEmail(true);
    }
  }

  const successAction = (mydata) => {
    setResetSucceeded(true);
    setRequestInProgress(false);
  }

  const submitPasswordResetRequest = (event) => {
    submitAction(event,
       sendFormRequest({formId: "start-pass-reset-form",
                      fieldSet: {email: [email, setEmail]},
                      requestAction: startPasswordReset,
                      extraArgs: ["token"],
                      history: myhistory,
                      dispatch: dispatch,
                      successCallback: successAction,
                      otherCallbacks: {serverErrorAction: serverErrorAction,
                                       badRequestAction: badRequestAction
                                      },
                      setInProgressAction: setRequestInProgress
                     })
    );
  }

  const setEmailValue = (val) => {
    if (!!val) {
      setMissingEmail(false);
      setEmail(val);
    }
  }

  return (
    <React.Fragment>
      <h2 className="text-center">Request a password reset</h2>
      {!!resetSucceeded &&
        <Alert variant="success">
          <h3>Success!</h3>
          <p>
            Your password reset request was accepted. An email has been sent to {email} with a temporary link allowing you to reset your password.
          </p>
          <p>(If you can't find the email, check your spam folder. Some email servers might put it in there!)</p>
        </Alert>
      }
      {!resetSucceeded &&
        <React.Fragment>
        <p>
          We'll send you an email with a temporary link allowing you to reset your password. After you click "Request reset email", look in your email inbox. (If you can't find the email, check your spam folder. Some email servers might put it in there!)
        </p>
        {!!resetFailed &&
          <Alert variant="danger" className="row error-message">
            <Col xs="auto">
              <FontAwesomeIcon icon="exclamation-triangle" size="2x" />
            </Col>
            <Col xs="10">
                Sorry, something went wrong with your request and the password reset email couldn't be sent. But if you contact the administrators they can help to resolve the problem.
              {/* FIXME: Add link to contact form here. */}
            </Col>
          </Alert>
        }
        {!!noSuchUser &&
          <Alert variant="danger" className="row error-message">
            <Col xs="auto">
              <FontAwesomeIcon icon="exclamation-triangle" size="2x" />
            </Col>
            <Col xs="10">
              Sorry, we don't have a registered user with that email address. Check that the address is correct or <Link to="register">sign up</Link>.
            </Col>
          </Alert>
        }
        {!!missingEmail &&
          <Alert variant="danger" className="row error-message">
            <Col xs="auto">
              <FontAwesomeIcon icon="exclamation-triangle" size="2x" />
            </Col>
            <Col xs="10">
              Sorry, you didn't provide a valid email address. Fill that field with a valid email address and try again.
            </Col>
          </Alert>
        }
        <Form role="form"
          id="start-pass-reset-form"
        >
          <Form.Group as={Row} controlId="startPassResetEmail">
            <Form.Label column sm={5}>
              Email
            </Form.Label>
            <Col sm={7}>
              <Form.Control
                type="email"
                name="email"
                placeholder="Enter your email address"
                autoComplete="email"
                onChange={e => setEmailValue(e.target.value, "my_email")}
              />
            </Col>
          </Form.Group>
          <Form.Group as={Row} controlId="startPassResetSubmitButton">
            <Col xs sm={5}>
            </Col>
            <Col className="start-pass-reset-submit-col">
              <Button variant="primary"
                  type="submit"
                  onClick={submitPasswordResetRequest}
                  disabled={!!requestInProgress ? true : false}
              >
                <FontAwesomeIcon icon="envelope" /> Request reset email
              </Button>
            </Col>
          </Form.Group>
        </Form>
        </React.Fragment>
      }
    </React.Fragment>
  );
}

const CompleteResetForm = ({resetKey, submitAction}) => {
  const myhistory = useHistory();
  const { user, dispatch } = useContext(UserContext);
  const [ passwordA, setPasswordA ] = useState();
  const [ passwordB, setPasswordB ] = useState();
  const [ passwordAMissing, setPasswordAMissing ] = useState(false);
  const [ passwordBMissing, setPasswordBMissing ] = useState(false);
  const [ inadequatePassword, setInadequatePassword ] = useState(false);
  const [ passwordsDontMatch, setPasswordsDontMatch ] = useState(false);
  const [ recaptchaFailed, setRecaptchaFailed ] = useState(false);
  const [ expiredResetKey, setExpiredResetKey ] = useState(false);
  const [ noSuchUser, setNoSuchUser ] = useState(false);
  const [ resetBlocked, setResetBlocked ] = useState(false);
  const [ resetFailed, setResetFailed ] = useState(false);
  const [ resetSucceeded, setResetSucceeded ] = useState(false);
  const [ requestInProgress, setRequestInProgress ] = useState(false);
  const [ errorDetails, setErrorDetails ] = useState(null);
  const [ showErrorDetails, setShowErrorDetails ] = useState(false);

  const serverErrorAction = (data) => {
    setRequestInProgress(false);
    setResetFailed(true);
    setErrorDetails(data.error)
  }

  const badRequestAction = (data) => {
    setRequestInProgress(false);
    if ( data.reason==="New passwords do not match" ) {
      setPasswordsDontMatch(true);
    } else if ( data.reason==="Missing request data" ) {
      if ( Object.keys(data.error).includes("new_password_A") ) {
         setPasswordAMissing(true)}
      if ( Object.keys(data.error).includes("new_password_B") ) {
         setPasswordBMissing(true)}
    } else if ( data.reason==="Password is not strong enough") {
      setInadequatePassword(true);
    } else if ( data.reason==="Password reset key was bad") {
      setExpiredResetKey(true);
    } else if ( data.reason==="User does not exist") {
      setNoSuchUser(true);
    } else {
      setResetFailed(true);
    }
  }

  const unauthorizedAction = (data) => {
    setRequestInProgress(false);
    if (data.reason==='Recaptcha failed') {
      setRecaptchaFailed(true);
    } else {
      setResetFailed(true);
      setErrorDetails(data.error);
    }
  }

  const actionBlockedAction = (data) => {
    setRequestInProgress(false);
    if ( data.reason === 'Action blocked' ) {
      setResetBlocked(true);
    } else {
      setResetFailed(true);
      setErrorDetails(data.error);
    }
  }

  const submitPasswordChange = token => {
    // handle autofilled data that doesn't trigger onChange state update
    setRequestInProgress(true);
    let myvalA = document.getElementById("complete-pass-reset-form").elements['passwordA'].value;
    let myvalB = document.getElementById("complete-pass-reset-form").elements['passwordB'].value;
    let subs = {};
    if ( !passwordA && !!myvalA ) {
      setPasswordA(myvalA);
      subs.passwordA = myvalA;
    }
    if ( !passwordB && !!myvalB ) {
      setPasswordB(myvalB);
      subs.passwordB = myvalB;
    }

    doPasswordReset({key: resetKey,
                     token: token,
                     passwordA: (!subs['passwordA'] ? passwordA : subs['passwordA']),
                     passwordB: (!subs['passwordB'] ? passwordB : subs['passwordB'])
                    })
    .then( respdata => {
        setInadequatePassword(false);
        setResetFailed(false);
        setResetSucceeded(false);
        setPasswordAMissing(false);
        setPasswordBMissing(false);
        setPasswordsDontMatch(false);
        setNoSuchUser(false);
        setExpiredResetKey(false);
        setResetBlocked(false);
        returnStatusCheck(respdata, myhistory,
          (respdata) => {
            setResetSucceeded(true);
            setRequestInProgress(false);
            myhistory.push('login?just_reset_password=true');
          },
          dispatch,
          {serverErrorAction: serverErrorAction,
           badRequestAction: badRequestAction,
           unauthorizedAction: unauthorizedAction,
           actionBlockedAction: actionBlockedAction
          })
    })
  }

  const changePassword = (event) => {
    submitAction(event, submitPasswordChange);
  }

  const updatePasswordAField = (val) => {
    setPasswordA(val);
    setPasswordAMissing(false);
  }

  const updatePasswordBField = (val) => {
    setPasswordB(val);
    setPasswordBMissing(false);
  }

  return (
    <React.Fragment>
      { user.userLoggedIn === true &&
        myhistory.goBack()
      }
      <h2 className="text-center">Set Your New Password</h2>
      <Form role="form"
        id="complete-pass-reset-form"
      >
        <Form.Group as={Row} controlId="doPassResetPasswordA">
          <Form.Label column sm={5}>
            New password
          </Form.Label>
          <Col sm={7}>
            <Form.Control
              type="password"
              name="passwordA"
              autoComplete="new-password"
              placeholder="Enter a new password"
              onChange={e => updatePasswordAField(e.target.value)}
            />
          </Col>
        </Form.Group>
        <Form.Group as={Row} controlId="doPassResetPasswordB">
          <Form.Label column sm={5}>
            Confirm password
          </Form.Label>
          <Col sm={7}>
            <Form.Control
              type="password"
              name="passwordB"
              autoComplete="new-password"
              placeholder="Re-type the new password"
              onChange={e => updatePasswordBField(e.target.value)}
            />
          </Col>
          {( !!passwordAMissing || !!passwordBMissing ) &&
              <Alert variant="danger" className="row error-message">
                <Col xs="auto">
                  <FontAwesomeIcon size="2x" icon="exclamation-triangle" /></Col>
                <Col xs="10">
                  You need to fill in both password fields.
                </Col>
              </Alert>
          }
          {!!passwordsDontMatch &&
              <Alert variant="danger" className="row error-message">
                <Col xs="auto">
                  <FontAwesomeIcon size="2x" icon="exclamation-triangle" /></Col>
                <Col xs="10">
                  The passwords you entered in the two fields aren't identical. Try again.
                </Col>
              </Alert>
          }
          {!!inadequatePassword &&
              <Alert variant="danger" className="row error-message">
                <Col xs="auto">
                  <FontAwesomeIcon size="2x" icon="exclamation-triangle" /></Col>
                <Col xs="10">
                  The password you chose isn't strong enough. Try a different password.
                </Col>
              </Alert>
          }
          {!!expiredResetKey &&
              <Alert variant="danger" className="row error-message">
                <Col xs="auto">
                  <FontAwesomeIcon size="2x" icon="exclamation-triangle" /></Col>
                <Col xs="10">
                  Sorry, the reset link you're using has expired. <Link to="reset_password">Click here</Link> to request a fresh one.
                </Col>
              </Alert>
          }
          {!!recaptchaFailed &&
              <Alert variant="danger" className="row error-message">
                <Col xs="auto">
                  <FontAwesomeIcon size="2x" icon="exclamation-triangle" /></Col>
                <Col xs="10">
                  Sorry, the system thinks you might not be a human. If you are one, try refreshing the page and submitting the form again. Or <Link to="reset_password">click here</Link> to request a fresh reset link.
                </Col>
              </Alert>
          }
          {!!noSuchUser &&
              <Alert variant="danger" className="row error-message">
                <Col xs="auto">
                  <FontAwesomeIcon size="2x" icon="exclamation-triangle" /></Col>
                <Col xs="10">
                  Sorry, we can't find a user that matches this password reset link. That could be because the link has already been used to reset your password once. <br/><br/>
                  <Link to="reset_password">Click here</Link> to request a fresh reset link. If that still doesn't work, contact the Paideia team and we'll help solve the problem.
                </Col>
              </Alert>
          }
          {!!resetBlocked &&
              <Alert variant="danger" className="row error-message">
                <Col xs="auto">
                  <FontAwesomeIcon size="2x" icon="exclamation-triangle" />
                </Col>
                <Col xs="10">
                  Sorry, the system won't allow us to reset your password right now. This could be because a reset is already in progress. Try again in a few minutes. If that still doesn't work, contact the Paideia team and we'll help solve the problem.
                </Col>
              </Alert>
          }
          {!!resetFailed &&
              <Alert variant="danger" className="row error-message">
                <Col xs="auto">
                  <FontAwesomeIcon size="2x" icon="exclamation-triangle" /></Col>
                <Col xs="10">
                  Sorry, something went wrong on our end and we weren't able to reset your password. But if you contact the Paideia team we'll help to resolve the problem.<br/>
                  {/* FIXME: add contact form link here */}
                  <Button variant="link"
                    onClick={() => setShowErrorDetails(!showErrorDetails)}>
                      <FontAwesomeIcon icon="bug" size="sm" />show error details
                  </Button>
                  <Collapse in={showErrorDetails}>
                    <div>{errorDetails}</div>
                  </Collapse>
                </Col>
              </Alert>
          }
          <Form.Text className="text-muted col col-xs col-sm-12">
            Your password must be at least 8 characters long. It must also include at least one upper case character and one number. Consider also including a special character (like #, &, !, etc.) and making it longer (up to 20 characters).
          </Form.Text>
        </Form.Group>
        <Form.Group as={Row} controlId="doPassResetSubmitButton">
          <Col xs sm={5}>
          </Col>
          <Col className="register-submit-col">
            <Button variant="primary"
                name="resetSubmitButton"
                type="submit"
                onClick={changePassword}
                disabled={!!requestInProgress ? true : false}
            >
              <FontAwesomeIcon icon="key" /> Set new password &nbsp;
            </Button>
          </Col>
        </Form.Group>
      </Form>
    </React.Fragment>
  );
}


const ResetPassword = () => {
  const queryParams = useQuery();
  const StartForm = withRecaptcha(StartResetForm);
  const CompleteForm = withRecaptcha(CompleteResetForm);

  return(
    <Row className="reset-password-component content-view justify-content-sm-center">
      <Col xs sm={8} lg={6}>
        {!!queryParams.get("key") ?
          <CompleteForm resetKey={queryParams.get("key")} />
          :
          <StartForm />
        }
      </Col>
    </Row>

  );
}

export default ResetPassword;