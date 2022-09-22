import React, { useState, useContext } from "react";
import {
    Button,
    Form,
    Row,
    Col,
    Spinner,
} from "react-bootstrap";
import { Formik } from "formik";
import * as Yup from "yup";
import { useHistory } from "react-router";

import { doApiCall, returnStatusCheck } from "../Services/utilityService";
import { UserContext } from "../UserContext/UserProvider";
import { FormErrorMessage } from "../Services/formsService";
import { withRecaptcha } from "../Services/authService";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { DEBUGGING } from "../variables";

const sendMessageAction = async (payload, setSubmitting, token) => {
    payload['token'] = token;
    const mailResponse = await doApiCall(payload, "contact", "JSON", "POST")
      .then(mydata => { DEBUGGING && console.log(mydata); return mydata;});
    DEBUGGING && console.log(mailResponse);
    return( mailResponse );
}

const ContactFormInner = ({submitAction}) => {
    const [ submissionSucceeded, setSubmissionSucceeded ] = useState(false);
    const [ emailResult, setEmailResult ] = useState();
    const [ submissionFailure, setSubmissionFailure ] = useState("");
    const history = useHistory();
    const { user, dispatch } = useContext(UserContext);

    const otherActions = (setSubmitting) => {
      return(
        {
        missingRequestDataAction: (data) => {
          setSubmitting(false);
          setSubmissionSucceeded(false);
          setSubmissionFailure(`Missing field: ${data.error.missing}`);
        },
        badRequestDataAction: null, // bad endpoint
        insufficientPrivilegesAction: () => {
          setSubmitting(false);
          setSubmissionSucceeded(false);
          setSubmissionFailure("Recaptcha check failed")
        },  // failed recaptcha
        serverErrorAction: () => {
          setSubmitting(false);
          setSubmissionSucceeded(false);
          setSubmissionFailure("Something went wrong")
        }
        }
      )
    };

    return(
    <Row className="contact-form-component content-view justify-content-sm-center">
      <Col xs sm={8} lg={6} xl={6}>
    <Formik
      initialValues={{subject: "",
                      firstName: !!user.userLoggedIn ? user.firstName : "",
                      lastName: !!user.userLoggedIn ? user.lastName : "",
                      body: "",
                      returnAddress: !!user.userLoggedIn ? user.email : ""}}
      validationSchema={Yup.object({
        subject: Yup.string().required(),
        body: Yup.string().required(),
        firstName: Yup.string().required(),
        lastName: Yup.string().required(),
        returnAddress: Yup.string().email().required()
      })}
      onSubmit={(values, { setSubmitting }) => {
        const payload = {subject: values.subject,
                         body: values.body,
                         first_name: values.firstName,
                         last_name: values.lastName,
                         return_address: values.returnAddress}
        setSubmissionSucceeded(false);
        submitAction(null,
          (token) => sendMessageAction(payload, setSubmitting, token)
              .then(messageResponse => {
                returnStatusCheck(messageResponse, history,
                  (mydata) => {
                    DEBUGGING && console.log(mydata);
                    setSubmitting(false);
                    setSubmissionSucceeded(true);
                    setEmailResult(mydata.email);
                  },
                  dispatch,
                  otherActions(setSubmitting)
                )
              })
        );
      }}
    >
      {formik => (
      !submissionSucceeded ? (
      <Form className="contact-form"
        onSubmit={formik.handleSubmit}
      >
        <Row>
          <h2>Contact Us</h2>
        </Row>
        <Row>
          <Form.Group as={Col} controlId="contactFormFirstName">
            <Form.Label>First Name</Form.Label>
            <Form.Control name="firstName" placeholder="Provide your first name"
              {...formik.getFieldProps("firstName")}
              className={formik.touched.firstName && formik.errors.firstName ? "error" : null}
            />
            <FormErrorMessage component="span" name="firstName" />
          </Form.Group>
        </Row>
        <Row>
          <Form.Group as={Col} controlId="contactFormLastName">
            <Form.Label>Last Name</Form.Label>
            <Form.Control name="lastName" placeholder="Provide your last name or family name"
              {...formik.getFieldProps("lastName")}
              className={formik.touched.lastName && formik.errors.lastName ? "error" : null}
            />
            <FormErrorMessage component="span" name="lastName" />
          </Form.Group>
        </Row>
        <Row>
          <Form.Group  as={Col} controlId="contactFormReturnAddress">
            <Form.Label>Your return email</Form.Label>
            <Form.Control name="returnAddress" type="email"
              placeholder="Provide your email address"
              {...formik.getFieldProps("returnAddress")}
              className={formik.touched.returnAddress && formik.errors.returnAddress ? "error" : null}
            />
            <FormErrorMessage component="span" name="returnAddress" />
          </Form.Group>
        </Row>
        <Row>
          <Form.Group as={Col} controlId="contactFormSubject">
            <Form.Label>Message subject</Form.Label>
            <Form.Control name="subject" placeholder="Provide a subject for your message"
              {...formik.getFieldProps("subject")}
              className={formik.touched.subject && formik.errors.subject ? "error" : null}
            />
            <FormErrorMessage component="span" name="subject" />
          </Form.Group>
        </Row>
        <Row>
          <Form.Group as={Col} controlId="contactFormBody">
            <Form.Label>Your Message</Form.Label>
            <Form.Control name="body" as="textarea" rows="10"
              placeholder="Type your message here"
              {...formik.getFieldProps("body")}
              className={formik.touched.body && formik.errors.body ? "error" : null}
            />
            <FormErrorMessage component="span" name="body" />
          </Form.Group>
        </Row>
        <Row>
          <Col>
            <Button variant="primary" type="submit"
              disabled={!!formik.isSubmitting ? true : false}
            >
              {!formik.isSubmitting ? <FontAwesomeIcon icon="envelope" /> : <Spinner animation="grow" size="sm" />} Send
            </Button>
            {submissionFailure}
          </Col>
        </Row>
      </Form>
      ): (<>
        <Row>
          <h2>Contact Us</h2>
        </Row>
        <Row className="result-display-row">
          <Col>
            {!emailResult ? "Waiting..." : (
              <>
              <Row>
                <Col>
                  <h3>Success!</h3>
                </Col>
              </Row>
              <Row className="contactResultLeadin">
                <Col>Here's the message that was sent.</Col>
              </Row>
              <Row className="contactResultFrom">
                <Col xs sm="4" className="label"> From</Col>
                <Col>{emailResult.first_name} {emailResult.last_name} </Col>
              </Row>
              <Row className="contactResultReturn">
                <Col xs sm="4" className="label"> Return address </Col>
                <Col> {emailResult.return_address} </Col>
              </Row>
              <Row className="contactResultSubject">
                <Col xs sm="2" className="label">Subject</Col>
                <Col>{emailResult.email_subject} </Col>
              </Row>
              <Row className="contactResultEmailText">
                <Col>
                  {emailResult.email_text}
                </Col>
              </Row>
              </>
            )}
          </Col>
        </Row>
      </>
      )
      )}
    </Formik>
    </Col>
    </Row>
    )
}

const ContactForm = withRecaptcha(ContactFormInner, "sendMessageAction");

export default ContactForm;