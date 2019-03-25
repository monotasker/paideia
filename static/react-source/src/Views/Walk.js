import React, { Component } from "react";
import {
  Container,
} from "react-bootstrap";
import { LinkContainer } from "react-router-bootstrap";

import mapImageSvg from "../Images/town_map.svg";

class Walk extends Component {
  constructor(props) {
    super(props);
    this.state = {
      currentPage: (props.match.params.walkPage || null)
    }
  }

  render() {
    return (
      <Container fluid>
        <object id='town_map' data={mapImageSvg} type='image/svg+xml'></object>
      </Container>
    );
  }
}

export default Walk;
