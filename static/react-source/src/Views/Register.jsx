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
import { useHistory,
         Link
       } from 'react-router-dom';
import moment from 'moment';
import 'moment-timezone';

import { register, login, formatLoginData } from '../Services/authService';
import { UserContext } from '../UserContext/UserProvider';
import { recaptchaKey } from '../variables';



const Register = () => {
  const { user, dispatch } = useContext(UserContext);
  const myhistory = useHistory();
  const [ myFirstName, setMyFirstName ] = useState();
  const [ myLastName, setMyLastName ] = useState();
  const [ myTimeZone, setMyTimeZone ] = useState("America/Toronto");
  const [ myEmail, setMyEmail ] = useState();
  const [ myPassword, setMyPassword ] = useState();
  // FIXME: Values above are undefined if autocompleted. Problem?

  useEffect(() => {
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

    loadScriptByURL("recaptcha-key",
        `https://www.google.com/recaptcha/api.js?render=${recaptchaKey}`, function () {
            console.log("Recaptcha Script loaded!");
        }
    );
  });

  const getRegistration = (event) => {
    console.log('getting new registration');
    event.preventDefault();

    window.grecaptcha.ready(() => {
        window.grecaptcha.execute(recaptchaKey, { action: 'submit' })
        .then(token => {
            console.log({theToken: token,
                      theFirstName: myFirstName,
                      theLastName: myLastName,
                      theTimeZone: myTimeZone,
                      theEmail: myEmail,
                      thePassword: myPassword
                      });
            register({theToken: token,
                      theFirstName: myFirstName,
                      theLastName: myLastName,
                      theTimeZone: myTimeZone,
                      theEmail: myEmail,
                      thePassword: myPassword
                      })
            .then( userdata => {
              console.log("initializing new user----------");
              console.log(userdata);
              if ( userdata.id != null ) {
                let loginData = new FormData({email: myEmail,
                                              password: myPassword})
                login(loginData)
                .then( loginData => {
                  if ( loginData.id != null ) {
                    dispatch({
                      type: 'initializeUser',
                      payload: formatLoginData(loginData)
                    })
                  } else {
                    console.log(`login failed`);
                  }
                })
              } else {
                  console.log(`registration failed`);
              }
            })
        });

    });
  }

  return(
    <Row className="register-component content-view justify-content-sm-center">
      <Col sm={8} lg={6} xl={4}>
        { user.userLoggedIn === true &&
          myhistory.goBack()
        }
        { user.userLoggedIn === false && (
          <React.Fragment>
          <h2 className="text-center">Create an account here!</h2>
          <Form
            // onSubmit={getRegistration}
            role="form"
          >
              <Form.Group as={Row} controlId="registerFirstName">
                <Form.Label column sm={5}>
                  First Name
                </Form.Label>
                <Col sm={7}>
                  <Form.Control
                    name="firstName"
                    placeholder="Enter your first name"
                    // autoComplete=""
                    onChange={e => setMyFirstName(e.target.value)}
                  />
                </Col>
              </Form.Group>
            <Form.Group as={Row} controlId="registerLastName">
              <Form.Label column sm={5}>
                Last Name
              </Form.Label>
              <Col sm={7}>
                <Form.Control
                  name="lastName"
                  placeholder="Enter your surname or family name"
                  // autoComplete=""
                  onChange={e => setMyLastName(e.target.value)}
                />
              </Col>
            </Form.Group>
            <Form.Group as={Row} controlId="registerEmail">
              <Form.Label column sm={5}>
                Email
              </Form.Label>
              <Col sm={7}>
                <Form.Control
                  type="email"
                  name="email"
                  placeholder="Enter your email address"
                  // autoComplete=""
                  onChange={e => setMyEmail(e.target.value)}
                  // className="col col-sm-7"
                />
              </Col>
              <Form.Text className="text-muted col col-sm-12">
                We'll never share your email with anyone else. We'll only
                use this to identify you and to contact you for things like
                resetting your password.
              </Form.Text>
            </Form.Group>
            <Form.Group as={Row} controlId="registerTimezone">
              <Form.Label column sm={5}>
                Your Time Zone
              </Form.Label>
              <Col sm={7}>
                <Form.Control as="select"
                  defaultValue={myTimeZone}
                  value={myTimeZone}
                  onChange={e => setMyTimeZone(e.target.value)}
                >
                  {moment.tz.names().map(tz => <option
                      key={tz}
                      value={tz}
                    >{tz}</option>
                  )}
                </Form.Control>
              </Col>
              <Form.Text className="text-muted col col-xs col-sm-12">
                When we analyze your learning on this app, your time zone will help us to know when you're starting a new day of activity.
              </Form.Text>
            </Form.Group>
            <Form.Group as={Row} controlId="registerPassword">
              <Form.Label column sm={5}>
                Password
              </Form.Label>
              <Col sm={7}>
                <Form.Control
                  type="password"
                  name="password"
                  autoComplete="current-password"
                  placeholder="Enter a password"
                  onChange={e => setMyPassword(e.target.value)}
                />
              </Col>
            </Form.Group>
            <Form.Group as={Row} controlId="registerSubmitButton">
              <Col xs sm={5}>
              </Col>
              <Col className="register-submit-col">
                <Button variant="primary"
                    type="submit"
                    onClick={getRegistration}
                >
                  Create account
                </Button>
              </Col>
            </Form.Group>
          </Form>
          <Alert variant="success"
            className="register-login-message"
          >
            <span>Already have an account?</span>
            <Button as={Link} to={`login`}
              variant="outline-success"
            >Log in
            </Button>
          </Alert>
          </React.Fragment>
        )}
      </Col>
    </Row>
  );
}

export default Register;
