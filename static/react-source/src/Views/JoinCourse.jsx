import React,
  { useState,
    useContext
  } from "react";
import {
         Link
       } from 'react-router-dom';
import {
    Alert,
    Col,
    Row,
} from "react-bootstrap";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { withRecaptcha } from '../Services/authService';
import { UserContext } from '../UserContext/UserProvider';
import { sendFormRequest,
         useFormManagement } from "../Services/formsService";

const JoinCourse = () => {
  const { user, dispatch } = useContext(UserContext);

  return(
    <Row className="join-course-component content-view justify-content-sm-center">
      <Col sm={8} lg={6} xl={4}>
        <h2 className="text-center">Join a Course Group Here!</h2>
        <Alert variant="success" className="row error-message">
          <p>You've found the page for joining a course group on Paideia. While the app is free to use for your personal enrichment, there is a fee to use Paideia as part of a course, getting feedback and guidance from an instructor.</p>
        </Alert>
        <br />
        <Alert variant="warning" className="row error-message">
        <Col xs="auto">
          <FontAwesomeIcon icon="hard-hat" size="2x" />
        </Col>
        <Col xs="10">
          <p>The payment form is still <b>under construction</b>. We want to make sure it's as secure as possible to keep you and your data safe. But <b>check back in a few days</b> to join your course group.</p>

          <p>Until then, feel free to <Link to="register">sign up</Link> for a free account and explore the app on your own.</p>
        </Col>
        </Alert>
      </Col>
    </Row>
  )
}

export default JoinCourse;