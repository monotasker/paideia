import React, { useState, useContext, useEffect } from "react";
import {
  Row,
  Col,
  Accordion,
  Card,
  Button
} from "react-bootstrap";

import { UserContext } from "../UserContext/UserProvider";
import { fetchLessons } from "../Services/stepFetchService";

const LessonList = () => {

  return  (
    <Accordion defaultActiveKey="0">
      <Card>
        <Card.Header>
          <Accordion.Toggle as={Button} variant="link" eventKey="0">
            Click me!
          </Accordion.Toggle>
        </Card.Header>
        <Accordion.Collapse eventKey="0">
          <Card.Body>Hello! I'm the body</Card.Body>
        </Accordion.Collapse>
      </Card>
      <Card>
        <Card.Header>
          <Accordion.Toggle as={Button} variant="link" eventKey="1">
            Click me!
          </Accordion.Toggle>
        </Card.Header>
        <Accordion.Collapse eventKey="1">
          <Card.Body>Hello! I'm another body</Card.Body>
        </Accordion.Collapse>
      </Card>
    </Accordion>
  )
}

const VideoDisplay = () => {
  return (<div>Video</div>)
}

const Videos = (props) => {

  const { user, dispatch } = useContext(UserContext);
  const [lessons, setLessons ] = useState([]);
  const [activeLesson, setActiveLesson] = useState(0);
  const [loading, setLoading] = useState(false);

  useEffect( () => {
    fetchLessons()
    .then(mydata => {
      setLessons(mydata);
    });
  });

  return (
    <Row className="videos-component content-view">
      <Col className="">
      <h2>Video Lessons</h2>

        <Row className="lessons-display-container">
          <Col>
            <LessonList defaultSet={user.currentBadgeSet} />
          </Col>

          <Col>
            <VideoDisplay activeLesson={activeLesson} />
          </Col>

        </Row>


      </Col>
    </Row>
  )
}

export default Videos;
