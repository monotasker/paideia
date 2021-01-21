import React, {
  useContext,
  useEffect,
  useState
} from "react";
import {
  Form,
  Button,
  Row,
  Col
} from "react-bootstrap";
import { withRouter, useHistory } from 'react-router';
import moment from 'moment';
import 'moment-timezone';

import { register, formatLoginData } from '../Services/authService';
import { UserContext } from '../UserContext/UserProvider';
import { recaptchaKey } from '../variables';



const Register = () => {
  const { user, dispatch } = useContext(UserContext);
  const history = useHistory();
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
              console.log(userdata);
            // if ( userdata.id != null ) {
            //     dispatch({
            //     type: 'initializeUser',
            //     payload: formatLoginData(userdata)
            //     })
            // } else {
            //     console.log(`registration failed`);
            // }
            })
        });

    });
  }

  return(
    <Row className="register-component content-view justify-content-sm-center">
      <Col xs sm={4}>
        { user.userLoggedIn === true &&
          history.back()
        }
        { user.userLoggedIn === false && (
          <React.Fragment>
          <h2 className="text-center">Create an account here!</h2>
          <Form
            // onSubmit={getRegistration}
            role="form"
          >
            <Form.Group controlId="registerFirstName">
              <Form.Label>
                First Name
              </Form.Label>
              <Form.Control
                name="firstName"
                placeholder="Enter your first name"
                // autoComplete=""
                onChange={e => setMyFirstName(e.target.value)}
                // value={myEmail}
              />
            </Form.Group>
            <Form.Group controlId="registerLastName">
              <Form.Label>
                Last Name
              </Form.Label>
              <Form.Control
                name="lastName"
                placeholder="Enter your surname or family name"
                // autoComplete=""
                onChange={e => setMyLastName(e.target.value)}
                // value={myEmail}
              />
            </Form.Group>
            <Form.Group controlId="registerEmail">
              <Form.Label>
                Email Address
              </Form.Label>
              <Form.Control
                type="email"
                name="email"
                placeholder="Enter your email address"
                // autoComplete=""
                onChange={e => setMyEmail(e.target.value)}
                // value={myEmail}
              />
              <Form.Text className="text-muted">
                We'll never share your email with anyone else. We'll only
                use this to identify you and to contact you for things like
                resetting your password.
              </Form.Text>
            </Form.Group>
            <Form.Group controlId="registerTimezone">
                <Form.Label>Your Time Zone</Form.Label>
                <Form.Control as="select"
                  defaultValue={myTimeZone}
                  onChange={e => setMyTimeZone(e.target.value)}
                >
                  {moment.tz.names().map(tz => <option
                      key={tz}
                      value={tz}
                      selected={tz===myTimeZone ? "selected" : false }
                    >{tz}</option>
                  )}
                </Form.Control>
            </Form.Group>
            <Form.Group controlId="registerPassword">
              <Form.Label>
                Password
              </Form.Label>
              <Form.Control
                type="password"
                name="password"
                autoComplete="current-password"
                placeholder="Enter a password"
                onChange={e => setMyPassword(e.target.value)}
                // value={myPassword}
              />
            </Form.Group>
            <Button variant="primary"
                // className="g-recaptcha"
                // type="submit"
                onClick={getRegistration}
            >
                  Create account
            </Button>
          </Form>
          </React.Fragment>
        )}
      </Col>
    </Row>
  );
}

export default withRouter(Register);
