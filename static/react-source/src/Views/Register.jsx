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

import { register,
         returnStatusCheck
       } from '../Services/authService';
import { UserContext } from '../UserContext/UserProvider';
import { recaptchaKey } from '../variables';
import { loadScriptByURL } from '../Services/utilityService';

const Register = () => {
  const { user, dispatch } = useContext(UserContext);
  const myhistory = useHistory();
  const [ myFirstName, setMyFirstName ] = useState();
  const [ myLastName, setMyLastName ] = useState();
  const [ myTimeZone, setMyTimeZone ] = useState("America/Toronto");
  const [ myEmail, setMyEmail ] = useState();
  const [ myPassword, setMyPassword ] = useState();
  const [ emailAlreadyExists, setEmailAlreadyExists ] = useState(false);
  const [ registrationFailed, setRegistrationFailed ] = useState(false);
  const [ inadequatePassword, setInadequatePassword ] = useState(false);
  const [ missingData, setMissingData ] = useState([]);
  // FIXME: Values above are undefined if autocompleted. Problem?

  useEffect(() => {
    loadScriptByURL("recaptcha-key",
        `https://www.google.com/recaptcha/api.js?render=${recaptchaKey}`, function () {
            console.log("Recaptcha Script loaded!");
        }
    );
  });

  const registerServerErrorAction = () => {
    console.log("Something went wrong on the server end");
    setRegistrationFailed(true);
  }

  const registerDataConflictAction = () => {
    console.log("A user with this email already exists!");
    setEmailAlreadyExists(true);
  }

  const registerBadRequestAction = (mydata) => {
    if ( mydata.reason==="Password is not strong enough" ) {
      console.log("Password is not strong enough");
      setInadequatePassword(true);
    } else if ( mydata.reason==="Missing request data" ) {
      console.log("Missing request data");
      let missingObj = mydata.error;
      console.log(missingObj);
      setMissingData(Object.keys(missingObj));
    }
  }

  const getRegistration = (event) => {
    event.preventDefault();

    window.grecaptcha.ready(() => {
        window.grecaptcha.execute(recaptchaKey, { action: 'submit' })
        .then(token => {
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
                returnStatusCheck(userdata, myhistory,
                  (mydata) => {
                      if ( mydata.id != null ) {
                        console.log(`registration succeeded****`);
                        setEmailAlreadyExists(false);
                        setInadequatePassword(false);
                        setRegistrationFailed(false);
                        myhistory.push('login?just_registered=true');
                      } else {
                        console.log(`registration failed****`);
                        setRegistrationFailed(true);
                      }
                  },
                  dispatch,
                  {serverErrorAction: registerServerErrorAction,
                   dataConflictAction: registerDataConflictAction,
                   badRequestAction: registerBadRequestAction
                  })
            })
        });

    });
  }

  const setFieldValue = (val, fieldName) => {
    const fields = {my_last_name: setMyLastName,
                    my_first_name: setMyFirstName,
                    my_email: setMyEmail,
                    my_time_zone: setMyTimeZone,
                    my_password: setMyPassword
                   }
    fields[fieldName](val);
    const index = missingData.indexOf(fieldName);
    if (index > -1) {
      missingData.splice(index, 1);
    }
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
          {!!registrationFailed &&
            <Alert variant="danger">
              Sorry, something went wrong with your registration. But if you contact the administrators they can help to resolve the problem.
              {/* FIXME: Add link to contact form here. */}
            </Alert>
          }
          {!!missingData && missingData.length > 0 &&
            <Alert variant="danger">
              Sorry, you didn't fill in all of the fields. Fill in the missing information and try again.
              {/* FIXME: Add link to contact form here. */}
            </Alert>
          }
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
                  autoComplete="given-name"
                  onChange={e => setFieldValue(e.target.value, "my_first_name")}
                />
              </Col>
              {!!missingData && missingData.includes("my_first_name") &&
                <Alert variant="danger" className="col col-sm-12">
                  You need to provide a first name.
                </Alert>
              }
            </Form.Group>
            <Form.Group as={Row} controlId="registerLastName">
              <Form.Label column sm={5}>
                Last Name
              </Form.Label>
              <Col sm={7}>
                <Form.Control
                  name="lastName"
                  placeholder="Enter your surname or family name"
                  autoComplete="family-name"
                  onChange={e => setFieldValue(e.target.value, "my_last_name")}
                />
              </Col>
              {!!missingData && missingData.includes("my_last_name") &&
                <Alert variant="danger" className="col col-sm-12">
                  You need to provide a last name.
                </Alert>
              }
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
                  autoComplete="email"
                  onChange={e => setFieldValue(e.target.value, "my_email")}
                />
              </Col>
              {(!!missingData && missingData.includes("my_email")) ?
                <Alert variant="danger" className="col col-sm-12">
                  You need to provide your email address.
                </Alert>
                :
                (!!emailAlreadyExists ?
                  <Alert variant="danger" className="col col-sm-12">
                    A user with that email already exists. Try logging in <Link to="login">here</Link>. If you can't remember your password you can recover it from the login screen.
                  </Alert>
                  :
                  <Form.Text className="text-muted col col-sm-12">
                    We'll never share your email with anyone else. We'll only
                    use this to identify you and to contact you for things like
                    resetting your password.
                  </Form.Text>
                )
              }
            </Form.Group>
            <Form.Group as={Row} controlId="registerTimezone">
              <Form.Label column sm={5}>
                Your Time Zone
              </Form.Label>
              <Col sm={7}>
                <Form.Control as="select"
                  defaultValue={myTimeZone}
                  // value={myTimeZone}
                  onChange={e => setFieldValue(e.target.value, "my_time_zone")}
                >
                  {moment.tz.names().map(tz => <option
                      key={tz}
                      value={tz}
                    >{tz}</option>
                  )}
                </Form.Control>
              </Col>
              {(!!missingData && missingData.includes("my_last_name")) ?
                  <Alert variant="danger" className="col col-sm-12">
                    You need to provide a valid time zone.
                  </Alert>
                :
                  <Form.Text className="text-muted col col-xs col-sm-12">
                    When we analyze your learning on this app, your time zone will help us to know when you're starting a new day of activity.
                  </Form.Text>
              }
            </Form.Group>
            <Form.Group as={Row} controlId="registerPassword">
              <Form.Label column sm={5}>
                Password
              </Form.Label>
              <Col sm={7}>
                <Form.Control
                  type="password"
                  name="password"
                  autoComplete="new-password"
                  placeholder="Enter a password"
                  onChange={e => setFieldValue(e.target.value, "my_password")}
                />
              </Col>
              <Form.Text className="text-muted col col-xs col-sm-12">
                {(!!missingData && missingData.includes("my_password")) ?
                    <Alert variant="danger" className="col col-sm-12">
                      You need to provide a password.
                    </Alert>
                    :
                    (!!inadequatePassword &&
                      <Alert variant="danger">The password you chose isn't strong enough. Try a different password.</Alert>
                    )
                }
                Your password must be at least 8 characters long. It must also include at least one upper case character and one number. Consider also including a special character (like #, &, !, etc.) and making it longer (up to 20 characters).
              </Form.Text>
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
