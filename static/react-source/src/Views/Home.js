import React, { Component } from "react";
import {
  Container,
  Row,
  Col,
  Button,
  Card
} from "react-bootstrap";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faExclamationTriangle,
  faSignInAlt
} from '@fortawesome/free-solid-svg-icons';
import imgMaria from "../Images/woman1.png";
import imgHowDoesItWork from "../Images/info_How_Does_It_Work.svg";
import imgKnownBugs from "../Images/info_Known_Bugs_and_Issue.svg";
import imgHowDoIType from "../Images/info_How_Do_I_Type_Greek.svg";
import imgWhatDoINeed from "../Images/info_What_Do_I_Need.svg";


const modalContent = [
  {img: imgWhatDoINeed,
   title: "What Do I Need?"},
  {img: imgHowDoIType,
   title: "How Do I Type Greek?"},
  {img: imgKnownBugs,
   title: "Known Bugs and Issues"}
];


const modalTriggers = modalContent.map( (item) =>
  <Col key={item.title} className='info-pane' md>
    <div className='info-illustration-wrapper'>
      <img className='info-pane-illustration' src={item.img} />
      <h4><a href="#">{item.title}</a></h4>
    </div>
  </Col>
);


class Home extends Component {
  constructor(props) {
    super(props);
    this.state = {
      pane1Open: false
    }
  }

  render() {
    return (

      <Container fluid>

      {/* Masthead row --------------------------------------------------*/}
      <Row>
        <Col className="masthead">

        <img className="welcome-maria" src={ imgMaria } />

        <div className="maria-bubble d-md-block">
          <h1>Welcome to Paideia!</h1>
          <p className="index-openmessage">Paideia is a fun and interactive place to learn New Testament Greek. To get started, register for a free account and then click the green button below to start exploring.</p>
          <Button variant="success">
            <FontAwesomeIcon icon={ faSignInAlt } />
            Explore
          </Button>
        </div>
        </Col>
      </Row>

      {/*Maria's message on narrow screens -------------------------------*/}
      <Row className="maria-bubble-mobile d-md-none clearfix">
          <Col>
            <h1>Welcome to Paideia!</h1>
            <p className="index-openmessage">Paideia is a fun and interactive place to learn New Testament Greek. To get started, register for a free account and then click the green button below to start exploring.</p>
            <Button variant="success">
              <FontAwesomeIcon icon={ faSignInAlt } />
              Explore
            </Button>
          </Col>
      </Row>

      {/*Alpha warning row -----------------------------------------------*/}
      <Row className="warning">
        <Col className="bg-danger">
          <Container>
            <p className="text-warning">
            <FontAwesomeIcon icon={faExclamationTriangle} size="lg" /> This app is a rough "alpha" version. Bug reports are appreciated.
            </p>
          </Container>
        </Col>
      </Row>

      {/*Info slide-out row -----------------------------------------------*/}
      <Row className='modal-set'>
          {modalTriggers}
      </Row>

    </Container>
    );
  }
}

export default Home;
