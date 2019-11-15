import React, { Component } from "react";
import {
   Container,
 } from "react-bootstrap";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faChevronLeft,
} from '@fortawesome/free-solid-svg-icons';

const ContentPage = (props) => {
  return(
    <Row className='content-page-component'>
        <a onClick={this.props.backFunc}>
          <FontAwesomeIcon icon={faChevronLeft} size="lg" pull="left" />
        </a>
      <h2>{this.props.title}</h2>
      {this.props.children}
    </Row>
)}

export default ContentPage;
