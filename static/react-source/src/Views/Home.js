import React, { Component } from "react";
import {
  Container,
  Row,
  Col,
  Button,
  Card
} from "react-bootstrap";
import styled from "styled-components";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faExclamationTriangle,
  faSignInAlt
} from '@fortawesome/free-solid-svg-icons';

import {
  darken
} from "../variables.js";
import imgMaria from "../Images/woman1.png";
import imgHowDoesItWork from "../Images/info_How_Does_It_Work.svg";
import imgKnownBugs from "../Images/info_Known_Bugs_and_Issue.svg";
import imgHowDoIType from "../Images/info_How_Do_I_Type_Greek.svg";
import imgWhatDoINeed from "../Images/info_What_Do_I_Need.svg";


const Masthead = styled(Col)`
  background-image: url(${props => props.theme.images.$mapPng});
  min-height: 360px;
  margin-top: 0;
  margin-bottom: 0;
  padding-bottom: 0;
  border: 0px solid transparent;
  overflow: hidden;
  height: 28rem;
  @media (max-width: ${props => props.theme.breakpoints.$md}) {
                      height: 10rem;
  }
  img.welcome-maria  {position: absolute;
                      left:0;
      @media (max-width: ${props => props.theme.breakpoints.$md}) {
                      height:36rem;
      }
  }
}
`;

const MariaRow = styled.div`
  background-color: white!important;
  padding:2rem;
  button {background-color: ${props => props.theme.palleteColors.$pallette4};
          border: 1px solid ${props => props.theme.palleteColors.$palletteBG};
          margin-top: 0.5rem;
  }
`;

const MariaRowMessage = styled.p`
  font-size: ${props => props.theme.typography.$fontSizeBase};
  color: #888;
`;

const MariaRowH1 = styled.h1`
  font-family: 'Amatic SC', cursive;
  font-weight: regular;
  font-size: 3rem;
  color: darken(${props => props.theme.palleteColors.$pallette1}, 30);
`;

const MariaBubble = styled(MariaRow)`
  position:absolute;
  top:5rem;
  left:360px;
  box-shadow: 2px 4px 0 rgba(0,0,0,0.5);
  border-radius:2rem;
  z-index: 10;
  display: none;
  overflow-y: hidden;
  :after {                    border-right: 25px solid #fff;
                              border-top: 25px solid transparent;
                              left: -25px;
                              top: 40%;
                              content: '';
                              position: absolute;
  }
  :before {                   border-right: 23px solid rgba(0,0,0,0.5);
                              border-top: 23px solid transparent;
                              left: -23px;
                              top: 42%;
                              content: '';
                              position: absolute;
    }
`;

const WarningRow = styled(Row)`
  background-color: ${props => props.theme.semanticColors.$danger};
  color: ${props => props.theme.semanticColors.$warning};
  padding: 1.25rem 0;
  p                          {text-align: center;
  }
`;

const InfoWrapper = styled.div`
    //text-align: center;
    // width:100%;
    @media (max-width: ${props => props.theme.breakpoints.$md}) {text-align: left;
    }
`;

const InfoLink = styled.div`
  color: ${props => props.theme.colors.$white};
  margin-top: 2rem;
  font-size: ${props => props.theme.typography.$fontSizeBase};
  @media (max-width: ${props => props.theme.breakpoints.$sm}) {line-height: 3em;
                                         height: 3em;
  }
  :hover                             {text-decoration: dotted;
  }
`;

const InfoIllustration = styled.img`
  width:12rem;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  padding: 0.5rem;
  // margin: 0px auto;
  @media (max-width: ${props => props.theme.breakpoints.$sm}) {float: right;
                                      width: 3rem;
                                      padding: 1rem;
  }
`;

const ModalRow = styled(Row)`
  color: #efefef;
  background-color: ${props => props.theme.palleteColors.$pallette3};
  text-align: center;
  padding-top: 3rem;
  padding-bottom: 3rem;
  @media (max-width: ${props => props.theme.breakpoints.$md})  {padding: 0;
                                         text-align: left;
                                         padding-left: 2rem;
                                         padding-right: 2rem;
  }
  p                       {hyphens: auto;
  }
`;

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
    <InfoWrapper>
      <InfoIllustration className='info-pane-illustration' src={item.img} />
      <h4><a href="#">{item.title}</a></h4>
    </InfoWrapper>
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
      <div className="home-component">
      {/* Masthead row --------------------------------------------------*/}
      <Row className="masthead-row">
        <Masthead className="masthead">

          <img className="welcome-maria" src={ imgMaria } />

          <MariaBubble className="maria-bubble d-md-block">
            <MariaRowH1>Welcome to Paideia!</MariaRowH1>
            <MariaRowMessage>
              Paideia is a fun and interactive place to learn New Testament Greek. To get started, register for a free account and then click the green button below to start exploring.
            </MariaRowMessage>
            <Button variant="success">
              <FontAwesomeIcon icon={ faSignInAlt } />
              Explore
            </Button>
          </MariaBubble>
        </Masthead>
      </Row>

      {/*Maria's message on narrow screens -------------------------------*/}
      <MariaRow className="maria-bubble-mobile d-md-none clearfix">
          <Col>
            <MariaRowH1>Welcome to Paideia!</MariaRowH1>
            <MariaRowMessage>
              Paideia is a fun and interactive place to learn New Testament Greek. To get started, register for a free account and then click the green button below to start exploring.
            </MariaRowMessage>
            <Button variant="success">
              <FontAwesomeIcon icon={ faSignInAlt } />
              Explore
            </Button>
          </Col>
      </MariaRow>

      {/*Alpha warning row -----------------------------------------------*/}
      <WarningRow className="warning">
        <Col className="bg-danger">
          <Container>
            <p className="text-warning">
            <FontAwesomeIcon icon={faExclamationTriangle} size="lg" /> This app is a rough "alpha" version. Bug reports are appreciated.
            </p>
          </Container>
        </Col>
      </WarningRow>

      {/*Info slide-out row -----------------------------------------------*/}
      <ModalRow className='modal-set'>
          {modalTriggers}
      </ModalRow>

    </div>
    );
  }
}

export default Home;
