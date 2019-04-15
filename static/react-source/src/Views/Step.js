import React, { Component } from "react";
import styled from "styled-components";
import {
    Row,
    Col,
    Button
} from "react-bootstrap";
import { LinkContainer } from "react-router-bootstrap";

const StepRow = styled(Row)`
`;

class Step extends Component {
  constructor(props) {
    super(props);
  }

  componentDidMount() {
    if (!this.context.isLoggedIn) {
      this.context.setUser();
    }
    if (!this.context.currentPath) {
      this.context.setCurrentPath(this.props.myroute);
    }
    if (!this.context.currentStep) {
      this.context.setCurrentStep();
    }
  }

  render() {
    console.log(this.props);
    return(
      <StepRow id="step_row" className={this.props.myroute + " stepPane"} >
        <div>
          {this.context.currentPath}
          {this.props.myroute}
          <Button
            onClick={() => this.props.navfunction("map")}
            >
            Click me
          </Button>
        </div>
        <div>
          {this.context.currentStep.prompt}
        </div>
      </StepRow>
    )
  }
}

export default Step;
