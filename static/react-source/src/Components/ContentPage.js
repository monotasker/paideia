import React, { Component } from "react";
import {
   Container,
 } from "react-bootstrap";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faChevronLeft,
} from '@fortawesome/free-solid-svg-icons';

class ContentPage extends Component {

  render() {
    return(
        <Container>
            <a onClick={this.props.backFunc}>
              <FontAwesomeIcon icon={faChevronLeft} size="lg" pull="left" />
            </a>
          <h2>{this.props.title}</h2>
          {this.props.children}
        </Container>
    )
  }
}

export default ContentPage;
