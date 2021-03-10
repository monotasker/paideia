import React, {
  useContext,
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
import {
  useHistory,
  Link
} from 'react-router-dom';

import {
  login,
  formatLoginData,
  withRecaptcha
} from '../Services/authService';
import { UserContext } from '../UserContext/UserProvider';
import { useQuery } from '../Services/utilityService';
import {
  sendFormRequest,
  useFormManagement
} from "../Services/formsService";

const LoginInner = ({submitAction}) => {
  const { user, dispatch } = useContext(UserContext);
  const history = useHistory();
  const queryParams = useQuery();
  const [ requestInProgress, setRequestInProgress ] = useState(false);

  let { formFieldValues, setFormFieldValue, setFormFieldsDirectly,
        flags, setFlags, myCallbacks
      } = useFormManagement({"email": "email", "password": null});

  myCallbacks.successAction = (data) => {
    if ( data.id != null ) {
      dispatch({
        type: 'initializeUser',
        payload: formatLoginData(data)
      })
    } else {
      setFlags({...flags, serverError: true});
    }
  }

  const getLogin = event => {
    submitAction(event,
      token => sendFormRequest(token, setFormFieldValue, {
        formId: 'login-form',
        fieldSet: {email: formFieldValues.email,
                   password: formFieldValues.password},
        requestAction: login,
        extraArgs: ["token"],
        history: history,
        dispatch: dispatch,
        successCallback: myCallbacks.successAction,
        otherCallbacks: {
          serverErrorAction: myCallbacks.serverErrorAction,
          loginFailedAction: myCallbacks.loginFailedAction,
          badRequestDataAction: myCallbacks.badRequestDataAction,
          missingRequestDataAction: myCallbacks.missingRequestDataAction
        },
        setInProgressAction: setRequestInProgress
      })
    );
  }

  return(
    <Row className="login-component content-view justify-content-sm-center">
      <Col xs sm={8} lg={6}>
        { user.userLoggedIn === true && (
            ( queryParams.get("just_reset_password")==="true" ||
              queryParams.get("just_registered")==="true" ) ?
              history.push('home')
              :
              history.goBack()
          )
        }
        { user.userLoggedIn === false && (
          <React.Fragment>
          <h2 className="text-center">How About Logging In?</h2>
          {queryParams.get("need_login")==="true" &&
            <Alert variant="danger">
              <Col xs="auto">
                <FontAwesomeIcon size="2x" icon="exclamation-triangle" />
              </Col>
              <Col xs="10">
                Sorry, you have to be logged in to access that area. You can log in now to continue or sign up.
              </Col>
            </Alert>
          }
          {queryParams.get("just_registered")==="true" &&
            <Alert variant="success">
              Now you can log in using the email and password that you just used to create your account!
            </Alert>
          }
          {queryParams.get("just_reset_password")==="true" &&
            <Alert variant="success">
              Now you can log in using your new password!
            </Alert>
          }
          {flags.missingRequestData.length > 0 &&
            <Alert variant="danger" className="error-message row">
              <Col xs="auto">
                <FontAwesomeIcon size="2x" icon="exclamation-triangle" />
              </Col>
              <Col xs="10">
                Some information was missing! Fill in the required fields and try again.
              </Col>
            </Alert>
          }
          <Form onSubmit={getLogin} role="form" id="login-form">
            <Form.Group controlId="loginEmail">
              <Form.Label>
                Email Address
              </Form.Label>
              <Form.Control
                type="email"
                name="email"
                placeholder="Enter your email address"
                autoComplete="email"
                onChange={e => setFormFieldValue(e.target.value, "email")}
              />
              {flags.missingRequestData.length > 0 &&
                flags.missingRequestData.includes("email") &&
                <Alert variant="danger" className="error-message">
                  <FontAwesomeIcon icon="exclamation-triangle" /> You need to include your email address.
                </Alert>
              }
              {flags.badRequestData.length > 0 &&
              flags.badRequestData.includes("email") &&
                <Alert variant="danger" className="error-message">
                  <FontAwesomeIcon icon="exclamation-triangle" /> You need to provide a valid email address.
                </Alert>
              }
            </Form.Group>
            <Form.Group controlId="loginPassword">
              <Form.Label>
                Password
              </Form.Label>
              <Form.Control
                type="password"
                name="password"
                autoComplete="current-password"
                placeholder="Password"
                onChange={e => setFormFieldValue(e.target.value, "password")}
              />
              {flags.missingRequestData.length > 0 &&
                flags.missingRequestData.includes("password") &&
                <Alert variant="danger" className="error-message">
                  <FontAwesomeIcon icon="exclamation-triangle" /> You need to include your password.
                </Alert>
              }
              {flags.badRequestData.length > 0 &&
                flags.badRequestData.includes("password") &&
                <Alert variant="danger" className="error-message">
                  <FontAwesomeIcon icon="exclamation-triangle" /> You need to include a password that is complex enough.
                </Alert>
              }
            </Form.Group>
            <Button variant="primary"
              type="submit"
            >
              <FontAwesomeIcon icon="sign-in-alt" /> Log in
            </Button>
          </Form>
          {flags.loginFailed===true &&
            <Alert variant="danger" className="error-message row">
              <Col xs="auto">
                <FontAwesomeIcon icon="exclamation-triangle" size="2x" />
              </Col>
              <Col xs="10">
                Sorry, we didn't recognize that combination of email and password. Check your information and try again. <br/><br/>
                If you can't remember your password, you can <Link to="reset_password">request a password reset</Link>.
              </Col>
            </Alert>
          }
          {flags.serverError===true &&
            <Alert variant="danger" className="error-message row">
              <Col xs="auto">
                <FontAwesomeIcon icon="exclamation-triangle" size="2x" />
              </Col>
              <Col xs="10">
                Sorry, something went wrong on our end. Please contact the app administrators and we'll help solve the problem.
              </Col>
            </Alert>
          }
          {queryParams.get("just_registered")!=="true" &&
           queryParams.get("just_reset_password")!=="true" &&
           <React.Fragment>
            <Alert variant="success" className="login-register-message">
              <span>Don't have an account?</span>
              <Button as={Link}
                to={`register`}
                variant="outline-success"
                disabled={!!requestInProgress ? true : false }
              >
                <FontAwesomeIcon icon="user-plus" /> Sign up!
              </Button>
            </Alert>
            <Alert variant="primary" className="login-reset-message">
              Don't remember your password? You can <Link to="reset_password">request a password reset</Link>.
            </Alert>
          </React.Fragment>
          }
          </React.Fragment>
        )}
      </Col>
    </Row>
  );
}

const Login = withRecaptcha(LoginInner);

export default Login;
