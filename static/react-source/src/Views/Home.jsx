import React, { useEffect, useState } from "react";
import {
  Row,
  Col,
  Button,
  Card,
  Spinner
} from "react-bootstrap";
import { Link,
         useHistory,
         useLocation } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faHardHat,
  faSignInAlt
} from '@fortawesome/free-solid-svg-icons';
import MiniMasonry from "minimasonry";

import imgMaria from "../Images/woman1.png";
import imgHowDoesItWork from "../Images/info_How_Does_It_Work.svg";
import imgHowDoIType from "../Images/info_How_Do_I_Type_Greek.svg";
import imgFAQs from "../Images/info_What_Do_I_Need.svg";
import { urlBase } from "../variables";
import { fetchTestimonials } from "../Services/infoService";

const modalContent = [
  {img: imgHowDoesItWork,
   title: "How Does It Work?",
   shortTitle: "How Does It Work?",
   path: "how-it-works"},
  {img: imgHowDoIType,
   title: "How Do I Type Greek?",
   shortTitle: "How Do I Type Greek?",
   path: "typing-greek"},
  {img: imgFAQs,
   title: "Frequently Asked Questions",
   shortTitle: "FAQs",
   path: "faq"}
];

const ModalTrigger = ({title, shortTitle, img, path, history}) => {

  const navigate = (event) => {
    history.push(`${path}`);
  };

  return (
    <Col key={title} className='info-pane' md
      onClick={navigate}
    >
      <div className="info-illustration-wrapper">
        <h4>
            <Link className="long-title" to={path} onClick={e => {e.preventDefault()}}>{title}</Link>
            <Link className="short-title" to={path} onClick={e => {e.preventDefault()}}>{shortTitle}</Link>
        </h4>
        <img className='info-pane-illustration'
          alt={title} src={img}
        />
      </div>
    </Col>
  )
}


const openmessage = "Paideia is a fun and interactive place to learn New Testament Greek. To get started, register for a free account and then click the green button below to start exploring."

const Home = () => {
  const history = useHistory();
  const myLocation = useLocation();
  const locParts = myLocation.pathname.split('/');
  const middlePath = locParts[locParts.length - 2]==="paideia" ? "" : "paideia/"
  const [updatingTestimonials, setUpdatingTestimonials] = useState();
  const [testimonials, setTestimonials] = useState();

  const chooseRandom = (rawArray, targetLength) => {
    let randomIntArray = []
    while ( randomIntArray.length < targetLength ) {
      let randomInt = Math.floor(Math.random() * rawArray.length);
      if ( randomIntArray.indexOf(randomInt) === -1 ) {
        randomIntArray.push(randomInt);
      }
    }
    console.log(randomIntArray);
    let randomItemArray = []
    for (const i of randomIntArray) {
        randomItemArray.push(rawArray[i]);
    }
    console.log(randomItemArray);
    return(randomItemArray);
  };

  useEffect(() => {
    setUpdatingTestimonials(true);
    fetchTestimonials()
    .then(mydata => {
      setUpdatingTestimonials(false);
      setTestimonials(chooseRandom(mydata, 8));
      new MiniMasonry({
        container: '.testimonials',
        gutterY: 0,
        gutterX: 18
      });
    });
  }, []);

  return (
    <div className="home-component content-view">
    {/* Masthead row --------------------------------------------------*/}
    <Row className="masthead-row">
      <Col className="masthead">

        <img className="welcome-maria"
          alt="A smiling Greek woman"
          src={ imgMaria } />

        <div className="maria-bubble d-md-block">
          <h1>Welcome to Paideia!</h1>
          <p className='index-openmessage'>
            {openmessage}
          </p>
            <Button variant="success"
              as={Link} to={`/${urlBase}/walk/map`}
            >
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
          <p className='index-openmessage'>
            {openmessage}
          </p>
          <Button variant="success"
            as={Link} to={`/${urlBase}/walk/map`}
          >
            <FontAwesomeIcon icon={ faSignInAlt } />
            Explore
          </Button>
        </Col>
    </Row>

    {/*Alpha warning row -----------------------------------------------*/}
    <Row className="warning">
      <Col className="bg-danger">
          <div className="icon-wrapper">
            <FontAwesomeIcon icon={faHardHat} size="lg" />
          </div>
          <p className="long-warning-text">
           This app is still in "beta" testing stage and is under active development. Bug reports are appreciated.
          </p>
          <p className="short-warning-text">
           Beta version. Bug reports are appreciated.
          </p>
      </Col>
    </Row>

    {/*Info slide-out row -----------------------------------------------*/}
    <Row className='modal-set'>
        {modalContent.map( item => <ModalTrigger title={item.title}
                                      shortTitle={item.shortTitle}
                                      key={`modal_trigger_${item.title}`}
                                      img={item.img}
                                      path={`${middlePath}info/${item.path}`}
                                      history={history}
                                   />
         )
        }
    </Row>

    {/* Testimonials row ------------------------------------------------*/}
    <Row className='testimonials'>
        {!!updatingTestimonials ?
          <Spinner animation="grow" size="lg" />
          :
          !!testimonials && testimonials.length > 0 ?
            testimonials.map(t =>
              <div className="testimonial-item" xs="12" sm="6" md="4" lg="3" xl="2" key={t.title}>
                <p className="testimonial-body">
                  {t.content}
                  <span className="testimonial-name">{t.title}</span>
                </p>
              </div>
            )
          :
          ""
        }
    </Row>

  </div>
  );
}

export default Home;
