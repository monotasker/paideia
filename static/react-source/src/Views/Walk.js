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

const WalkGroup = styled(TransitionGroup)`
  div#exploring-mask                          {display: block;
                                               position: absolute;
                                               background-color: rgba(255,255,255,1.0);
                                               width: 100%;
                                               height: 100%;
                                               text-align: center;
      img                                     {position: absolute;
      }
  }
  .svgMapPane-enter {
    opacity: 0;
  }

  .svgMapPane-enter-active {
    opacity: 1;
    transition: opacity 2000ms;
  }

  .svgMapPane-exit {
    opacity: 1;
  }

  .svgMapPane-exit-active {
    opacity: 1;
    transition: opacity 2000ms;
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
    return (
      <TransitionGroup className="walk-container" >
        <CSSTransition
          in={ this.state.mapIn }
          classNames="svgMapPane"
          timeout={2000}
        >
          <SvgMap navFunction={this.goToLocation} />
        </CSSTransition>
        <CSSTransition
          in={ this.state.stepin }
          classNames="stepPane"
          timeout={300}
        >
          <Step
            myroute={this.state.currentpage}
            navfunction={this.gotolocation}
          />
        </CSSTransition>
      </TransitionGroup>
    );
  }
}



export default Walk;
