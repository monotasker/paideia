import React, {
  useContext,
  useEffect,
  useState
} from "react";
import {
  Form,
  Button,
  Row,
  Col,
  Alert
} from "react-bootstrap";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { useHistory,
         Link
} from 'react-router-dom';

import { recaptchaKey } from '../variables';
import { returnStatusCheck,
  startPasswordReset,
  doPasswordReset
} from '../Services/authService';
import { loadScriptByURL, useQuery } from '../Services/utilityService';
import { UserContext } from '../UserContext/UserProvider';

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

  const requestResetEmail = token => {
    // handle autofilled data that doesn't trigger onChange state update
    setRequestInProgress(true);
    let myval = document.getElementById("start-pass-reset-form").elements['email'].value;
    let subEmail = null;
    if ( !email && !!myval ) {
      setEmail(myval);
      subEmail = myval;
    }

    startPasswordReset({token: token,
                        email: !subEmail ? email : subEmail}
                      )
    .then( respdata => {
        returnStatusCheck(respdata, myhistory,
          (mydata) => {
            setResetSucceeded(true);
            setRequestInProgress(false);
          },
          dispatch,
          {serverErrorAction: serverErrorAction,
           badRequestAction: badRequestAction
          })
    })
  }

  const submitPasswordResetRequest = (event) => {
    submitAction(event, requestResetEmail);
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

const CompleteResetForm = ({myKey, submitAction}) => {
  const [ passwordA, setPasswordA ] = useState();
  const [ passwordB, setPasswordB ] = useState();
  const [ passwordAMissing, setPasswordAMissing ] = useState(false);
  const [ passwordBMissing, setPasswordBMissing ] = useState(false);
  const [ inadequatePassword, setInadequatePassword ] = useState(false);
  const [ passwordsDontMatch, setPasswordsDontMatch ] = useState(false);
  const [ resetFailed, setResetFailed ] = useState(false);
  const [ requestInProgress, setRequestInProgress ] = useState(false);

  const serverErrorAction = (data) => {
    setResetFailed(true);
  }

  const badRequestAction = (data) => {
    if ( data.reason==="New passwords do not match" ) {
      setPasswordsDontMatch(true);
    } else if ( data.reason==="Missing request data" ) {
      if ( Object.keys(data.error).includes("password_a") ) {
         setPasswordAMissing(true)}
      if ( Object.keys(data.error).includes("password_b") ) {
         setPasswordBMissing(true)}
    } else if ( data.reason==="Password inadequate") {
      setInadequatePassword(true);
    }
  }

  const changePassword = () => {

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
      <h2 className="text-center">Set Your New Password</h2>
      <Form role="form"
        id="complete-pass-reset-form"
      >
        <Form.Group as={Row} controlId="doPassResetPasswordA">
          <Form.Label column sm={5}>
            Enter your new password
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
            Enter the same password again
          </Form.Label>
          <Col sm={7}>
            <Form.Control
              type="password"
              name="passwordB"
              autoComplete="new-password"
              placeholder="Enter a new password"
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
          <Form.Text className="text-muted col col-xs col-sm-12">
            Your password must be at least 8 characters long. It must also include at least one upper case character and one number. Consider also including a special character (like #, &, !, etc.) and making it longer (up to 20 characters).
          </Form.Text>
        </Form.Group>
        <Form.Group as={Row} controlId="doPassResetSubmitButton">
          <Col xs sm={5}>
          </Col>
          <Col className="register-submit-col">
            <Button variant="primary"
                type="submit"
                onClick={changePassword}
                disabled={!!requestInProgress ? true : false}
            >
              <FontAwesomeIcon icon="user-plus" /> Create account
            </Button>
          </Col>
        </Form.Group>
      </Form>
    </React.Fragment>
  );
}


const ResetPassword = () => {
  const queryParams = useQuery();

  const submitAction = (event, myAction) => {
    event.preventDefault();
    window.grecaptcha.ready(() => {
        window.grecaptcha.execute(recaptchaKey, { action: 'register' })
        .then(token => {
            myAction(token);
        });
    });
  }

  useEffect(() => {
    loadScriptByURL("recaptcha-key",
        `https://www.google.com/recaptcha/api.js?render=${recaptchaKey}`, function () {
            console.log("Recaptcha Script loaded!");
        }
    );
  }, []);

  return(
    <Row className="login-component content-view justify-content-sm-center">
      <Col xs sm={8} lg={6}>
        {!!queryParams.get("key") ?
          <CompleteResetForm myKey={queryParams.get("key")}
            submitAction={submitAction}
          />
          :
          <StartResetForm submitAction={submitAction} />
        }
      </Col>
    </Row>

  );
}

export default ResetPassword;