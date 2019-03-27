import React, { Component } from "react";
import {
    Row,
    Col
} from "react-bootstrap";
import { LinkContainer } from "react-router-bootstrap";

class Step extends Component {
  render() {
    return(
      this.props.activeRoutes.includes(this.props.myRoute) &&
      <Row>
        <Col>
        { this.props.myRoute }
        </Col>
      </Row>
    )
  }
}

export default Step;
