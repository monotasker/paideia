import React, { useState, useContext } from "react";
import {
    Button,
    Form,
    Row,
    Col,
} from "react-bootstrap";
import { Formik } from "formik";
import * as Yup from "yup";
import { useHistory } from "react-router";

import { doApiCall, returnStatusCheck } from "../Services/utilityService";
import { UserContext } from "../UserContext/UserProvider";
import { FormErrorMessage } from "../Services/formsService";
import { withRecaptcha } from "../Services/authService";

const sendMessageAction= (payload, setSubmitting, token) => {
    payload['token'] = token;
    doApiCall(payload, "contact", "JSON", "POST").then(mydata => {
      setSubmitting(false);
    });
}

const ContactFormInner = ({submitAction}) => {
    const [ submissionSucceeded, setSubmissionSucceeded ] = useState(false);
    const [ submitting, setSubmitting ] = useState(false);
    const [ emailResult, setEmailResult ] = useState();
    const history = useHistory();
    const { user, dispatch } = useContext(UserContext);


    return(
    <Formik
      initialValues={{subject: "", firstName: "", lastName: "",
                      body: "", returnAddress: ""}}
      validationSchema={Yup.object({
        subject: Yup.string(),
        body: Yup.string(),
        firstName: Yup.string(),
        lastName: Yup.string(),
        returnAddress: Yup.string().email()
      })}
      onSubmit={(values, { setSubmitting }) => {
        const payload = {subject: values.subject,
                         body: values.body,
                         first_name: values.firstName,
                         last_name: values.lastName,
                         return_address: values.returnAddress}
        setSubmissionSucceeded(false);
        submitAction(null,
          (token) => sendMessageAction(payload, setSubmitting, token))
        .then(stepfetch => {
                  returnStatusCheck(stepfetch, history,
                    (mydata) => {
                      setSubmissionSucceeded(true);
                      setEmailResult(mydata);
                    },
                    dispatch
                  )
                });
      }}
    >
      {formik => (
      <Form className="contact-form"
        onSubmit={formik.handleSubmit}
      >
        <Row>
          <h2>Contact Us</h2>
          <Col>
            <Form.Control name="subject" placeholder="Provide a subject for your message"
              {...formik.getFieldProps("subject")}
              className={formik.touched.subject && formik.errors.subject ? "error" : null}
            />
            <FormErrorMessage component="span" name="subject" />
          </Col>
        </Row>
        <Row>
          <Col>
            <Form.Control name="firstName" placeholder="Provide your first name"
              {...formik.getFieldProps("firstName")}
              className={formik.touched.firstName && formik.errors.firstName ? "error" : null}
            />
            <FormErrorMessage component="span" name="firstName" />
          </Col>
        </Row>
        <Row>
          <Col>
            <Form.Control name="lastName" placeholder="Provide your last name or family name"
              {...formik.getFieldProps("lastName")}
              className={formik.touched.lastName && formik.errors.lastName ? "error" : null}
            />
            <FormErrorMessage component="span" name="lastName" />
          </Col>
        </Row>
        <Row>
          <Col>
            <Form.Control name="returnAddress" placeholder="Provide your email address"
              {...formik.getFieldProps("returnAddress")}
              className={formik.touched.returnAddress && formik.errors.returnAddress ? "error" : null}
            />
            <FormErrorMessage component="span" name="returnAddress" />
          </Col>
        </Row>
        <Row>
          <Col>
            <Form.Control name="body" placeholder="Type your message here"
              {...formik.getFieldProps("body")}
              className={formik.touched.body && formik.errors.body ? "error" : null}
            />
            <FormErrorMessage component="span" name="body" />
          </Col>
        </Row>
        <Row className="result-display-row">
          <Col>{emailResult}
          </Col>
        </Row>
        <Button variant="primary" type="submit">Send</Button>
      </Form>
      )}
    </Formik>
    )
}

const ContactForm = withRecaptcha(ContactFormInner, "sendMessageAction");

export default ContactForm;