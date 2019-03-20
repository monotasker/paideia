import React, { Component } from 'react';
import {
  Container,
} from "react-bootstrap";
import { LinkContainer } from "react-router-bootstrap";

class Instructors extends Component {
  constructor(props) {
    super(props);
    this.state = {
      currentPage: this.props.match.params.instrPage
    }
  }

  render() {
    return(
      <Container fluid>
        {this.state.currentPage}
      </Container>
    )
  }
}

export default Instructors;
