import React, {
  useContext,
  useState,
  useEffect
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
  returnStatusCheck
} from '../Services/authService';
import { UserContext } from '../UserContext/UserProvider';
import { useQuery } from '../Services/utilityService';
import { recaptchaKey } from '../variables';
import { loadScriptByURL } from '../Services/utilityService';


const Login = () => {
  const { user, dispatch } = useContext(UserContext);
  const history = useHistory();
  const queryParams = useQuery();
  const [ email, setEmail ] = useState();
  const [ password, setPassword ] = useState();
  const [ missing, setMissing ] = useState([]);
  const [ loginFailed, setLoginFailed ] = useState(false);
  const [ serverProblem, setServerProblem ] = useState(false);

  useEffect(() => {
    loadScriptByURL("recaptcha-key",
        `https://www.google.com/recaptcha/api.js?render=${recaptchaKey}`, function () {
            console.log("Recaptcha Script loaded!");
        }
    );
  }, []);

  const serverErrorAction = (data) => {
    console.log("server error");
    console.log(data);
    setServerProblem(true);
  }
  const unauthorizedAction = () => {
    console.log("unauthorized");
    setLoginFailed(true);
  }
  const badRequestAction = (data) => {
    console.log("bad request: missing...");
    console.log(data.error);
    setMissing(Object.keys(data.error));
    setLoginFailed(false);
  }

  const setFieldValue = (val, fieldName) => {
    const fields = {email: setEmail, password: setPassword}
    fields[fieldName](val);
    const index = missing.indexOf(fieldName);
    if (index > -1) {
      missing.splice(index, 1);
    }
  }

  const getLogin = (event) => {
    event.preventDefault();

    window.grecaptcha.ready(() => {
        window.grecaptcha.execute(recaptchaKey, { action: 'login' })
        .then(token => {
            login({token: token,
                   email: email,
                   password: password
                  })
            .then( userdata => {
                console.log("checking status");
                returnStatusCheck(userdata, history,
                  (mydata) => {
                      if ( mydata.id != null ) {
                        setLoginFailed(false);
                        setServerProblem(false);
                        dispatch({
                          type: 'initializeUser',
                          payload: formatLoginData(mydata)
                        })
                      } else {
                        setServerProblem(true);
                        console.log(`login failed`);
                      }
                  },
                  dispatch,
                  {serverErrorAction: serverErrorAction,
                   unauthorizedAction: unauthorizedAction,
                   badRequestAction: badRequestAction
                  })
            })
        });
    });
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
          {missing.length > 0 &&
            <Alert variant="danger" className="error-message row">
              <Col xs="auto">
                <FontAwesomeIcon size="2x" icon="exclamation-triangle" />
              </Col>
              <Col xs="10">
                Some information was missing! Fill in the required fields and try again.
              </Col>
            </Alert>
          }
          <Form onSubmit={getLogin} role="form">
            <Form.Group controlId="loginEmail">
              <Form.Label>
                Email Address
              </Form.Label>
              <Form.Control
                type="email"
                name="email"
                placeholder="Enter your email address"
                autoComplete="email"
                onChange={e => setFieldValue(e.target.value, "email")}
              />
              {missing.length > 0 && missing.includes("email") &&
                <Alert variant="danger" className="error-message">
                  <FontAwesomeIcon icon="exclamation-triangle" /> You need to include your email address.
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
                onChange={e => setFieldValue(e.target.value, "password")}
              />
              {missing.length > 0 && missing.includes("password") &&
                <Alert variant="danger" className="error-message">
                  <FontAwesomeIcon icon="exclamation-triangle" /> You need to include your password.
                </Alert>
              }
            </Form.Group>
            <Button variant="primary"
              type="submit"
            >
              <FontAwesomeIcon icon="sign-in-alt" /> Log in
            </Button>
          </Form>
          {!!loginFailed &&
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
          {!!serverProblem &&
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

export default Login;
