import React, { Component } from "react";
import {
    Row,
    Col
} from "react-bootstrap";
import { LinkContainer } from "react-router-bootstrap";

class Step extends Component {
  render() {
    return(
      <Row id="step_row" className="{ this.props.myRoute }">
        <Col>
        { this.props.myRoute }
        </Col>
      </Row>
    )
  }
}

export default Step;
