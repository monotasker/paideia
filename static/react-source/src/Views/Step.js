import React, { Component } from "react";
import {
    Row,
    Col,
    Button
} from "react-bootstrap";
import { LinkContainer } from "react-router-bootstrap";

class Step extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    console.log(this.props);
    return(
      <Row id="step_row" className={this.props.myroute + " stepPane"} >
        <Col>
          Here's some text.
          {this.props.myroute}
          <Button
            onClick={() => this.props.navfunction("map")}
            >
          </Button>
        </Col>
      </Row>
    )
  }
}

export default Step;
