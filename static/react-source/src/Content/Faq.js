import React, { Component } from "react";
// import {
//    Container,
//  } from "react-bootstrap";
// import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
// import {
//   faChevronLeft,
// } from '@fortawesome/free-solid-svg-icons';

import ContentPage from '../Components/ContentPage';
import Collapsible from '../Components/Collapsible';

class FaqContent extends Component {

  render() {
    return(
        <ContentPage
          title="Frequently Asked Questions"
          backFunc={this.props.backFunc}
        >
        </ContentPage>
    )
  }
}

export default FaqContent;
