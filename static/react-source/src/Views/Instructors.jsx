import React, { Component } from 'react';
import {
  Row,
} from "react-bootstrap";
import { LinkContainer } from "react-router-bootstrap";
import { withRouter } from "react-router";

class Instructors extends Component {
  constructor(props) {
    super(props);
    this.state = {
      currentPage: this.props.location.search
    }
  }

  render() {
    return(
      <div className="instructors-component content-view">
        {this.state.currentPage}
      </div>
    )
  }
}

export default withRouter(Instructors);
