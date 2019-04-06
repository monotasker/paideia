import React, { Component } from "react";
import ReactDOM from "react-dom";
import {
  Container,
} from "react-bootstrap";
import { LinkContainer } from "react-router-bootstrap";
import {
  CSSTransition,
  TransitionGroup
} from "react-transition-group";
import styled from "styled-components";
import Velocity from "velocity-animate";

import { make_map_pan } from "../Services/mapNavService";
import SvgMap from "./SvgMap.js";
import Step from "./Step.js";

const WalkRow = styled.div`

  .svgMapPane-enter,
  .svgMapPane-appear {
    opacity: 0;
  }

  .svgMapPane-enter-done,
  .svgMapPane-appear-done {
    opacity: 1;
    transition: opacity 1000ms;
  }

  .svgMapPane-exit {
    opacity: 1;
  }

  .svgMapPane-exit-active {
    opacity: 0;
    transition: opacity 500ms;
  }

  .svgMapPane-exit-done {
    opacity: 0;
    display: none;
  }

  .stepPane-enter {
    opacity: 0;
  }

  .stepPane-enter-done {
    opacity: 1;
    transition: opacity 300ms;
  }

  .stepPane-exit {
    opacity: 1;
  }

  .stepPane-exit-active {
    opacity: 0;
    transition: opacity 300ms;
  }

  .stepPane-exit-done {
    opacity: 0;
    position: absolute;
  }
`;

class Walk extends Component {
  constructor(props) {
    super(props);
    this.activeRoutes = ["path5424", "path5418"];
    this.state = {
      currentPage: (props.match.params.walkPage || "map"),
      mapIn: true,
      stepIn: false
    }
    this.goToLocation = this.goToLocation.bind(this);
    this.showStep = this.showStep.bind(this);
    this.showMap = this.showMap.bind(this);
  }

  goToLocation(newLoc) {
    this.setState({currentPage: newLoc});
    let newState =  newLoc == "map" ? true : false;
    this.setState({mapIn: newState});
  }

  showStep() {
    console.log("fired!");
    this.setState({stepIn: true});
  }

  showMap() {
    console.log("fired!");
    this.setState({mapIn: true});
  }

  render() {
    return (
      <WalkRow className="walk-container" >
        <CSSTransition
          in={ this.state.mapIn }
          classNames="svgMapPane"
          timeout={2000}
          appear={true}
          onExited={this.showStep}
        >
          <SvgMap
            navFunction={this.goToLocation}
            id="town_map"
          />
        </CSSTransition>

        <CSSTransition
          in={ this.state.stepIn }
          classNames="stepPane"
          timeout={300}
          onExited={this.showMap}
          mountOnEnter
        >
          <Step
            myroute={this.state.currentPage}
            navfunction={this.goToLocation}
          />
        </CSSTransition>

      </WalkRow>
    );
  }
}



export default Walk;
