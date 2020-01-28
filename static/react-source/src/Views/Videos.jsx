import React, { Component } from "react";
import {
  Row,
  Col,
} from "react-bootstrap";

class Videos extends Component {
  render() {
    return (
      <Row className="videos-component content-view">
        <Col className="">
        <h2>Videos</h2>
        <p>Mauris sem velit, vehicula eget sodales vitae,
        rhoncus eget sapien:</p>
        <ul>
          <li>Nulla pulvinar diam</li>
          <li>Facilisis bibendum</li>
          <li>Vestibulum vulputate</li>
          <li>Eget erat</li>
          <li>Id porttitor</li>
        </ul>
        </Col>
      </Row>
    );
  }
}

export default Videos;
