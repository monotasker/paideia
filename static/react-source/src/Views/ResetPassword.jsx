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

import {
  startPasswordReset,
  doPasswordReset,
  withRecaptcha
} from '../Services/authService';
import { useQuery} from '../Services/utilityService';
import { UserContext } from '../UserContext/UserProvider';
import { sendFormRequest,
         useFormManagement } from '../Services/formsService';


const StartResetForm = ({submitAction}) => {
  const myhistory = useHistory();
  const { user, dispatch } = useContext(UserContext);
  const [ requestInProgress, setRequestInProgress ] = useState(false);

  let { formFieldValues, setFormFieldValue, setFormFieldsDirectly,
        flags, setFlags, myCallbacks, showErrorDetails, setShowErrorDetails
      } = useFormManagement({email: "email"});

  const submitPasswordResetRequest = (event) => {
    console.log(`requesting for ${formFieldValues.email}`);
    submitAction(event,
        (token) => {sendFormRequest(token, setFormFieldValue,
          {formId: "start-pass-reset-form",
           fieldSet: {email: formFieldValues.email},
           requestAction: startPasswordReset,
           extraArgs: ["token"],
           history: myhistory,
           dispatch: dispatch,
           successCallback: myCallbacks.successAction,
           otherCallbacks: {
             serverErrorAction: myCallbacks.serverErrorAction,
             noRecordAction: myCallbacks.noRecordAction,
             dataConflictAction: myCallbacks.dataConflictAction,
             missingRequestDataAction: myCallbacks.missingRequestDataAction,
             recaptchaFailedAction: myCallbacks.recaptchaFailedAction
           },
           setInProgressAction: setRequestInProgress
        })
      }
    )
  }
  console.log("flags is:");
  console.log(flags);

  return (
    <React.Fragment>
      <h2 className="text-center">Request a password reset</h2>
      {!!flags.success &&
        <Alert variant="success">
          <h3>Success!</h3>
          <p>
            Your password reset request was accepted. An email has been sent to {formFieldValues.email} with a temporary link allowing you to reset your password.
          </p>
          <p>(If you can't find the email, check your spam folder. Some email servers might put it in there!)</p>
        </Alert>
      }
      {!flags.success &&
        <React.Fragment>
        <p>
          We'll send you an email with a temporary link allowing you to reset your password. After you click "Request reset email", look in your email inbox. (If you can't find the email, check your spam folder. Some email servers might put it in there!)
        </p>
        {!!flags.serverError &&
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
        {!!flags.noRecord &&
          <Alert variant="danger" className="row error-message">
            <Col xs="auto">
              <FontAwesomeIcon icon="exclamation-triangle" size="2x" />
            </Col>
            <Col xs="10">
              Sorry, we don't have a registered user with that email address. Check that the address is correct or <Link to="register">sign up</Link>.
            </Col>
          </Alert>
        }
        {!!flags.dataConflict &&
          <Alert variant="danger" className="row error-message">
            <Col xs="auto">
              <FontAwesomeIcon icon="exclamation-triangle" size="2x" />
            </Col>
            <Col xs="10">
              Sorry, a password reset is already in process for this user. If you requested one earlier, check your email for the link to perform the reset.
            </Col>
          </Alert>
        }
        {!!flags.missingRequestData.length > 0 &&
            flags.missingRequestData.includes("email") &&
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
          <Form.Group as={Row} controlId="email">
            <Form.Label column sm={5}>
              Email
            </Form.Label>
            <Col sm={7}>
              <Form.Control
                type="email"
                name="email"
                placeholder="Enter your email address"
                autoComplete="email"
                onChange={e => setFormFieldValue(e.target.value, "email")}
              />
            </Col>
            {!!flags.badRequestData.length > 0 &&
                flags.badRequestData.includes("email") &&
              <Alert variant="danger" className="row error-message">
                <Col xs="auto">
                  <FontAwesomeIcon icon="exclamation-triangle" size="2x" />
                </Col>
                <Col xs="10">
                  Please provide a valid email address.
                </Col>
              </Alert>
            }
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
  const [ requestInProgress, setRequestInProgress ] = useState(false);

  const myFields = {password_A: "password",
                    password_B: "password"}

  let { formFieldValues, setFormFieldValue, setFormFieldsDirectly,
        flags, setFlags, myCallbacks, showErrorDetails, setShowErrorDetails
      } = useFormManagement(myFields);

  const fieldSet = Object.keys(myFields).reduce((current, myName) => {
    return {...current, [myName]: formFieldValues[myName]}
  }, {});

  myCallbacks.badRequestDataAction = (data) => {
    if ( data.reason==="New passwords do not match" ) {
      setFlags({...flags, passwordsDoNotMatch: true});
    } else if ( data.reason==="Password is not strong enough") {
      setFlags({...flags, badRequestData: ["password"]});
    }
  }

  myCallbacks.successAction = (data) => {
    myhistory.push('login?just_reset_password=true');
  }

  const changePassword = (event) => {
    setFlags({...flags, passwordsDoNotMatch: false});
    submitAction(event,
      (token) => {sendFormRequest(token, setFormFieldValue,
           {formId: "complete-pass-reset-form",
            fieldSet: {...fieldSet,
                       key: resetKey
                      },
            requestAction: doPasswordReset,
            extraArgs: ["token"],
            history: myhistory,
            dispatch: dispatch,
            successCallback: myCallbacks.successAction,
            otherCallbacks: {
              serverErrorAction: myCallbacks.serverErrorAction,
              badRequestDataAction: myCallbacks.badRequestAction,
              missingRequestDataAction: myCallbacks.missingRequestDataAction,
              noRecordAction: myCallbacks.noRecordAction,
              insufficientPrivilegesAction: myCallbacks.insufficientPrivilegesAction,
              actionBlockedAction: myCallbacks.actionBlockedAction,
              recaptchaFailedAction: myCallbacks.recaptchaFailedAction
            },
            setInProgressAction: setRequestInProgress
          })
        }
    );
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
        <Form.Group as={Row} controlId="doPassResetKey" className="hidden-field">
          <Form.Label column sm={5}>
            Reset Key
          </Form.Label>
          <Col sm={7}>
            <Form.Control
              readOnly
              name="resetKey"
              value={resetKey}
            />
          </Col>
        </Form.Group>
        <Form.Group as={Row} controlId="password_A">
          <Form.Label column sm={5}>
            New password
          </Form.Label>
          <Col sm={7}>
            <Form.Control
              type="password"
              name="password_A"
              autoComplete="new-password"
              placeholder="Enter a new password"
              onChange={e => setFormFieldValue(e.target.value, "password_A")}
            />
          </Col>
        </Form.Group>
        <Form.Group as={Row} controlId="password_B">
          <Form.Label column sm={5}>
            Confirm password
          </Form.Label>
          <Col sm={7}>
            <Form.Control
              type="password"
              name="password_B"
              autoComplete="new-password"
              placeholder="Re-type the new password"
              onChange={e => setFormFieldValue(e.target.value, "password_B")}
            />
          </Col>
          {( flags.missingRequestData.length > 0 &&
                (flags.missingRequestData.includes("password_A") ||
                 flags.missingRequestData.includes("password_B"))
           ) &&
              <Alert variant="danger" className="row error-message">
                <Col xs="auto">
                  <FontAwesomeIcon size="2x" icon="exclamation-triangle" /></Col>
                <Col xs="10">
                  You need to fill in both password fields.
                </Col>
              </Alert>
          }
          {!!flags.passwordsDoNotMatch &&
              <Alert variant="danger" className="row error-message">
                <Col xs="auto">
                  <FontAwesomeIcon size="2x" icon="exclamation-triangle" /></Col>
                <Col xs="10">
                  The passwords you entered in the two fields aren't identical. Try again.
                </Col>
              </Alert>
          }
          {!!flags.badRequestData.length > 0 &&
                flags.badRequestData.includes("password_A") &&
              <Alert variant="danger" className="row error-message">
                <Col xs="auto">
                  <FontAwesomeIcon size="2x" icon="exclamation-triangle" /></Col>
                <Col xs="10">
                  The password you chose isn't strong enough. Try a different password.
                </Col>
              </Alert>
          }
          {!!flags.insufficientPrivileges &&
              <Alert variant="danger" className="row error-message">
                <Col xs="auto">
                  <FontAwesomeIcon size="2x" icon="exclamation-triangle" /></Col>
                <Col xs="10">
                  Sorry, the reset link you're using has expired. <Link to="reset_password">Click here</Link> to request a fresh one.
                </Col>
              </Alert>
          }
          {!!flags.recaptchaFailed &&
              <Alert variant="danger" className="row error-message">
                <Col xs="auto">
                  <FontAwesomeIcon size="2x" icon="exclamation-triangle" /></Col>
                <Col xs="10">
                  Sorry, the system thinks you might not be a human. If you are one, try refreshing the page and submitting the form again. Or <Link to="reset_password">click here</Link> to request a fresh reset link.
                </Col>
              </Alert>
          }
          {!!flags.noRecord &&
              <Alert variant="danger" className="row error-message">
                <Col xs="auto">
                  <FontAwesomeIcon size="2x" icon="exclamation-triangle" /></Col>
                <Col xs="10">
                  Sorry, we can't find a user that matches this password reset link. That could be because the link has already been used to reset your password once. <br/><br/>
                  <Link to="reset_password">Click here</Link> to request a fresh reset link. If that still doesn't work, contact the Paideia team and we'll help solve the problem.
                </Col>
              </Alert>
          }
          {!!flags.actionBlocked &&
              <Alert variant="danger" className="row error-message">
                <Col xs="auto">
                  <FontAwesomeIcon size="2x" icon="exclamation-triangle" />
                </Col>
                <Col xs="10">
                  Sorry, the system won't allow us to reset your password right now. This could be because a reset is already in progress. Try again in a few minutes. If that still doesn't work, contact the Paideia team and we'll help solve the problem.
                </Col>
              </Alert>
          }
          {!!flags.serverError &&
              <Alert variant="danger" className="row error-message">
                <Col xs="auto">
                  <FontAwesomeIcon size="2x" icon="exclamation-triangle" /></Col>
                <Col xs="10">
                  Sorry, something went wrong on our end and we weren't able to reset your password. But if you contact the Paideia team we'll help to resolve the problem.<br/>
                  {/* FIXME: add contact form link here */}
                  {typeof flags.serverError==="string" &&
                    <React.Fragment>
                    <Button variant="link"
                      onClick={() => setShowErrorDetails(!showErrorDetails)}>
                        <FontAwesomeIcon icon="bug" size="sm" />show error details
                    </Button>
                    <Collapse in={showErrorDetails}>
                      <div>{flags.serverError}</div>
                    </Collapse>
                    </React.Fragment>
                  }
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
  const CompleteForm = withRecaptcha(CompleteResetForm, "completePasswordReset");
  const StartForm = withRecaptcha(StartResetForm, "startPasswordReset");

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