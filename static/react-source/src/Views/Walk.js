import React, { Component } from "react";
import ReactDOM from "react-dom";
import {
  Container,
} from "react-bootstrap";
import { LinkContainer } from "react-router-bootstrap";
import {
  Transition,
  TransitionGroup
} from "react-transition-group";
import Velocity from "velocity-animate";

import { make_map_pan } from "../Services/mapNavService";
import SvgMap from "./SvgMap.js";
import Step from "./Step.js";

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
    this.showMe = this.showMe.bind(this);
    this.hideMe = this.hideMe.bind(this);
  }

  goToLocation(newLoc) {
    this.setState({currentPage: newLoc});
    if ( newLoc == "map" ) {
      this.setState({...this.state, mapIn: true, stepIn: false});
    } else {
      this.setState({...this.state, mapIn: false, stepIn: true});
    }
  }

  showMe(node) {
    console.log("show");
    Velocity(node,
      {opacity: '1',
       display: block},
      {duration: 1000, delay: 1000});
  }

  hideMe(nodeID) {
    console.log("hide");
    Velocity(node,
      {opacity: '0',
       display: none},
      1000);
  }

  render() {
    console.log(this.state.mapIn);
    return (
      <TransitionGroup className="walk-container" >
        <Transition
          in={ this.state.mapIn }
          onEnter={ node => this.showMe(node) }
          onExit={ node => this.hideMe(node) }
          timeout={300}
        >
          <SvgMap navFunction={this.goToLocation} />
        </Transition>
        <Transition
          in={ this.state.stepIn }
          onEnter={ node => this.showMe(node) }
          onExit={ node => this.hideMe(node) }
          timeout={300}
          mountOnEnter
        >
          <Step
            myRoute={this.state.currentPage}
            navFunction={this.goToLocation}
          />
        </Transition>
      </TransitionGroup>
    );
  }
}

export default Walk;
