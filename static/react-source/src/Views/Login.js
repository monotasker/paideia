import React, { Component } from "react";
import {
  Form,
  Button,
} from "react-bootstrap";

const getLogin = (event) => {
  fetch('http://localhost:8000/paideia/default/call/json/get_login', {
      method: "GET",
      cache: "no-cache",
      mode: "cors",
  })
  .then(function(myJson) {
    console.log(myJson);
  })
  event.preventDefault();
}

const Login = () => {
  return(
      <Form onSubmit={this.getLogin} role="form">
        <Form.Group controlId="loginEmail">
          <Form.Label>Email Address</Form.Label>
          <Form.Control type="email" placeholder="Enter your email address"></Form.Control>
          <Form.Text className="text-muted">Some instruction</Form.Text>
        </Form.Group>
        <Form.Group controlId="loginPassword">
          <Form.Label>Password</Form.Label>
          <Form.Control type="password" placeholder="Password"></Form.Control>
          <Form.Text className="text-muted">Some instruction</Form.Text>
        </Form.Group>
        <Button variant="primary" type="submit">Log in</Button>
      </Form>
  );
}

export default Login;
