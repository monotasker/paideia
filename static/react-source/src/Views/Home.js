import React, { Component } from "react";
import {
  Container,
  Row,
  Col,
  Button
} from "react-bootstrap";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faExclamationTriangle,
  faSignInAlt
} from '@fortawesome/free-solid-svg-icons';
import imgMaria from "../Images/woman1.png";

class Home extends Component {
  render() {
    return (
      <Container fluid>
      <Row>
        <h2>Welcome to Paideia!</h2>

        <img className="welcome-maria" src={ imgMaria } />

        <div className="maria-bubble hidden-xs">
          <p className="index-openmessage">Paideia is a fun and interactive place to learn New Testament Greek. To get started, register for a free account and then click the green button below to start exploring.</p>
          <Button variant="success">
            <FontAwesomeIcon icon={ faSignInAlt } />
            Explore
          </Button>
        </div>

      </Row>
      <Row>
        <Col>
          <Container>
            <p className="warning">
            <FontAwesomeIcon icon={faExclamationTriangle} size="lg" /> This app is a rough "alpha" version. Bug reports are appreciated.
            </p>
          </Container>
        </Col>
      </Row>
      <Row>
      </Row>
      </Container>
    );
  }
}

export default Home;
