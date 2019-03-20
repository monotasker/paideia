import React, { Component } from 'react';
import {
  Container,
} from "react-bootstrap";
import { LinkContainer } from "react-router-bootstrap";

class Info extends Component {
  constructor(props) {
    super(props);
    this.state = {
      currentPage: props.match.params.infoPage
    }
  }

  render() {
    return(
      <Container>
        {this.state.currentPage}
      </Container>
    )
  }
}

export default Info;
