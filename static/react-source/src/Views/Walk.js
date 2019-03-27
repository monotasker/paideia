import React, { Component } from "react";
import {
  Container,
} from "react-bootstrap";
import { LinkContainer } from "react-router-bootstrap";

import { make_map_pan } from "../Services/mapNavService";
import SvgMap from "./SvgMap.js";
import Step from "./Step.js";

class Walk extends Component {
  constructor(props) {
    super(props);
    this.activeRoutes = ["path5424", "path5418"];
    this.state = {
      currentPage: (props.match.params.walkPage || "map")
    }
    this.goToLocation = this.goToLocation.bind(this);
  }

  goToLocation(newLoc) {
    this.setState({currentPage: newLoc});
  }

  render() {
    return (
      <Container fluid className="walk-container">
        <SvgMap
          myRoute={this.state.currentPage}
          navFunction={this.goToLocation}
        />
        <Step
          myRoute={this.state.currentPage}
          activeRoutes={this.activeRoutes}
          navFunction={this.goToLocation}
        />
      </Container>
    );
  }
}

export default Walk;
