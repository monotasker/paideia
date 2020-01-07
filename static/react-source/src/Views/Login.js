import React, {
  useContext
} from "react";
import {
  Form,
  Button,
  Row,
  Col
} from "react-bootstrap";
import { login } from '../Services/authService';
import { UserContext } from '../UserContext/UserProvider';
import { withRouter } from 'react-router';

const Login = (props) => {
  const { user, dispatch } = useContext(UserContext);

  const getLogin = (event) => {
    console.log('getting login');
    let formdata = new FormData(event.target);
    event.preventDefault();

    login(formdata)
    .then( response => response.json() )
    .then( userdata => {
      if ( userdata.id != null ) {
        console.log(userdata);
        return dispatch({
          type: 'initializeUser',
          payload: {
            userId: userdata['id'],
            firstName: userdata['first_name'],
            lastName: userdata['last_name'],
            email: userdata['email'],
            userLoggedIn: true,
            userRoles: [],
            userToken: '',
            userTimezone: userdata['time_zone']
          }
        })
      } else {
        console.log(`login failed`);
        console.log(userdata);
      }
      console.log(user);
    })
  }

  return(
    <Row className="login-component content-view justify-content-sm-center">
      <Col xs sm={4}>
        { user.userLoggedIn == true &&
          history.back()
        }
        { user.userLoggedIn == false && (
          <React.Fragment>
          <h2 className="text-center">How About Logging In?</h2>
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
            <Button variant="primary" type="submit">Log in</Button>
          </Form>
          </React.Fragment>
        )}
      </Col>
    </Row>
  );
}

export default withRouter(Login);
