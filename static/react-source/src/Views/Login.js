import React, { Component } from "react";
import {
  Form,
  Button,
  Row,
  Col
} from "react-bootstrap";

const getLogin = (event) => {
  console.log('getting login');
  let response = fetch('/paideia/default/get_login', {
      method: "POST",
      cache: "no-cache",
      // mode: "cors",
      body: new FormData(event.target)
  })
  .then( myjson => {console.log(myjson);
  });
  event.preventDefault();
}

const Login = () => {
  return(
    <Row className="login-component justify-content-sm-center">
      <Col xs sm={4}>
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
      </Col>
    </Row>
  );
}

export default Login;
