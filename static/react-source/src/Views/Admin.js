import React, { Component } from 'react';
import {
  Container,
} from "react-bootstrap";
import { LinkContainer } from "react-router-bootstrap";
import { withRouter } from "react-router";

class Admin extends Component {
  constructor(props) {
    super(props);
    this.state = {
      currentPage: props.location.search
    }
  }

  render() {
    return(
      <div className="admin-component">
          {this.state.currentPage}
      </div>
    )
  }
}

export default withRouter(Admin);
