import React from "react";
import {
  Col,
  Row,
 } from "react-bootstrap";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faChevronLeft,
} from '@fortawesome/free-solid-svg-icons';

const ContentPage = (props) => {
  return(
    <Col className='content-page-component' sm='8'>
      <a onClick={props.backFunc}
        className="content-page-back-link"
      >
        <FontAwesomeIcon icon={faChevronLeft} size="lg" pull="left" />
      </a>
      <h2 className='content-page-title'>{props.title}</h2>
      {props.children}
    </Col>
)}

export default ContentPage;
