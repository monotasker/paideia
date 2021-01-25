import React, {
  useContext
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
  Link,
  useLocation
} from 'react-router-dom';

import { login, formatLoginData } from '../Services/authService';
import { UserContext } from '../UserContext/UserProvider';
import { useQuery } from '../Services/utilityService';


const Login = () => {
  const useQuery = () => {
    return new URLSearchParams(useLocation().search);
  }
  const { user, dispatch } = useContext(UserContext);
  const history = useHistory();
  const queryParams = useQuery();
  console.log(`query:`);
  console.log(queryParams.get("just_registered"));

  const getLogin = (event) => {
    let formdata = new FormData(event.target);
    event.preventDefault();

    login(formdata)
    .then( userdata => {
      if ( userdata.id != null ) {
        dispatch({
          type: 'initializeUser',
          payload: formatLoginData(userdata)
        })
      } else {
        console.log(`login failed`);
      }
    })
  }

  return(
    <Row className="login-component content-view justify-content-sm-center">
      <Col xs sm={6} lg={4}>
        { user.userLoggedIn === true &&
          history.goBack()
        }
        { user.userLoggedIn === false && (
          <React.Fragment>
          <h2 className="text-center">How About Logging In?</h2>
          {queryParams.get("just_registered")==="true" &&
            <Alert variant="success">
              Now you can log in using the email and password that you just used to create your account!
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
              />
              {/* <Form.Text className="text-muted">Your email address acts as your username</Form.Text> */}
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
              />
            </Form.Group>
            <Button variant="primary" type="submit">
              <FontAwesomeIcon icon="sign-in-alt" /> Log in
            </Button>
          </Form>
          <Alert variant="success" className="login-register-message">
            <span>Don't have an account yet?</span>
            <Button as={Link}
              to={`register`}
              variant="outline-success"
            >
              <FontAwesomeIcon icon="user-plus" /> Sign up!
            </Button>
          </Alert>
          </React.Fragment>
        )}
      </Col>
    </Row>
  );
}

export default Login;
