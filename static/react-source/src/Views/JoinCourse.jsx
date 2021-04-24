import React,
  { useState,
    useContext,
    useEffect
  } from "react";
import { useHistory,
         Link
       } from 'react-router-dom';
import {
    Alert,
    Button,
    Col,
    Form,
    Row,
    } from "react-bootstrap";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useElements, useStripe } from '@stripe/react-stripe-js';
import { withRecaptcha } from '../Services/authService';
import { UserContext } from '../UserContext/UserProvider';
import { sendFormRequest,
         useFormManagement } from "../Services/formsService";
import { validateCourseKey,
         createCheckoutIntent
       } from "../Services/authService";
import { isAlphanumericString } from "../Services/utilityService";

// FIXME: use actual publishable key in production
const stripe_promise = loadStripe("pk_test_51IYtbhCzY7JkMiXGdU7a5MhH7UO6kk0pIiHEFZb5X4dKJ9KS98wdLKlfc4i9VCLekCtsRaV9uksdLTLNKP6Oy5sw000lqIdBpU");

const CheckoutForm = ({ submitAction, courseKey }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [processing, setProcessing] = useState('');
  const [disabled, setDisabled] = useState(true);
  const [result, setResult] = useState({});
  const [clientSecret, setClientSecret] = useState('');
  const myhistory = useHistory();
  const { user, dispatch } = useContext(UserContext);

  const fieldsAndValidators = {course_key: "string"};
  let {formFieldValues, setFormFieldValue, setFormFieldValuesDirectly,
    flags, setFlags, myCallbacks, showErrorDetails,
    setShowErrorDetails} = useFormManagement(fieldsAndValidators);

  // create object with state field value and setter for each field
  const fieldSet = {course_key: courseKey};

  myCallbacks.successAction = (data) => {
    setResult(data);
    setClientSecret(data.clientSecret);
  }

  // Create PaymentIntent as soon as the page loads
  useEffect(() => {
    fieldSet.order_items = [{id: "student-membership"}];
    submitAction(null,
      token => sendFormRequest(token, setFormFieldValue,
        {formId: 'joinClassPaymentForm',
         fieldSet: fieldSet,
         requestAction: createCheckoutIntent,
         extraArgs: ["token"],
         history: myhistory,
         dispatch: dispatch,
         successCallback: myCallbacks.successAction,
         otherCallbacks: {
           serverErrorAction: myCallbacks.serverErrorAction,
           dataConflictAction: myCallbacks.dataConflictAction,
           badRequestDataAction: myCallbacks.badRequestDataAction,
           missingRequestDataAction: myCallbacks.missingRequestDataAction
         },
        setInProgressAction: setProcessing
      })
    );
  }, []);

  // css to control stripe iframe styles
  const cardStyle = {
    style: {
      base: {
        color: "#32325d",
        fontFamily: 'Arial, sans-serif',
        fontSmoothing: "antialiased",
        fontSize: "16px",
        "::placeholder": {
          color: "#32325d"
        }
      },
      invalid: {
        color: "#fa755a",
        iconColor: "#fa755a"
      }
    }
  };

  // Listen for changes in the CardElement
  // and display any errors as the customer types their card details
  const handleChange = async (event) => {
    setDisabled(event.empty);
    setFlags({...flags, serverError: event.error ? event.error.message : false});
  };

  const handleSubmit = async ev => {
    ev.preventDefault();
    setProcessing(true);
    const payload = await stripe.confirmCardPayment(clientSecret, {
      payment_method: {
        card: elements.getElement(CardElement)
      }
    });
    if (payload.error) {
      setFlags({...flags,
                success: false,
                serverError: `Payment failed ${payload.error.message}`});
      setProcessing(false);
    } else {
      setFlags({...flags,
                serverError: false,
                success: true});
      setProcessing(false);
    }
  };

  return (
    <form id="payment-form" onSubmit={handleSubmit}>
      <CardElement id="card-element" options={cardStyle} onChange={handleChange} />
      <button
        disabled={processing || disabled || flags.success}
        id="submit"
      >
        <span id="button-text">
          {processing ? (
            <div className="spinner" id="spinner"></div>
          ) : (
            "Pay now"
          )}
        </span>
      </button>
      {/* Show any error that happens when processing the payment */}
      {!!flags.serverError && (
        <div className="card-error" role="alert">
          {flags.serverError}
        </div>
      )}
      {/* Show a success message upon completion */}
      <p className={flags.success ? "result-message" : "result-message hidden"}>
        Payment succeeded, see the result in your
        <a
          href={`https://dashboard.stripe.com/test/payments`}
        >
          {" "}
          Stripe dashboard.
        </a>
      </p>
    </form>
  )
}


const JoinCourse = ({ submitAction }) => {
  const myhistory = useHistory();
  const { user, dispatch } = useContext(UserContext);
  const [ showPaymentForm, setShowPaymentForm ] = useState(false);
  const [ requestInProcess, setRequestInProcess ] = useState(false);
  const fieldsAndValidators = {course_key: "string"};
  let {formFieldValues, setFormFieldValue, setFormFieldValuesDirectly,
    flags, setFlags, myCallbacks, showErrorDetails,
    setShowErrorDetails} = useFormManagement(fieldsAndValidators);

  const fieldSet = {course_key: (val) => isAlphanumericString(val)}

  const checkCourseKey = (event) => {
    submitAction(event,
      token => sendFormRequest(token, setFormFieldValue,
        {formId: 'couseKeyForm',
         fieldSet: fieldSet,
         requestAction: validateCourseKey,
         extraArgs: ["token"],
         history: myhistory,
         dispatch: dispatch,
         successCallback: myCallbacks.successAction,
         otherCallbacks: {
           serverErrorAction: myCallbacks.serverErrorAction,
           dataConflictAction: myCallbacks.dataConflictAction,
           badRequestDataAction: myCallbacks.badRequestDataAction,
           missingRequestDataAction: myCallbacks.missingRequestDataAction
         },
        setInProgressAction: setRequestInProcess
      })
    );
  }

  return(
    <Row className="join-course-component content-view justify-content-sm-center">
      <Col sm={8} lg={6} xl={4}>
        <h2 className="text-center">Join a Course Group Here!</h2>
        <Alert variant="success" className="row error-message">
          <p>You've found the page for joining a course group on Paideia. While the app is free to use for your personal enrichment, there is a fee to use Paideia as part of a course, getting feedback and guidance from an instructor.</p>
        </Alert>
        <br />
        <Alert variant="warning" className="row error-message">
        <Col xs="auto">
          <FontAwesomeIcon icon="hard-hat" size="2x" />
        </Col>
        <Col xs="10">
          <p>The payment form is still <b>under construction</b>. We want to make sure it's as secure as possible to keep you and your data safe. But <b>check back in a few days</b> to join your course group.</p>

          <p>Until then, feel free to <Link to="register">sign up</Link> for a free account and explore the app on your own.</p>

          {!showPaymentForm ?
            <Form
              role="form"
              id="courseKeyForm"
            >
              <Form.Group as={Row} controlId="first_name">
                <Form.Label column sm={5}>
                  Course Key
                </Form.Label>
                <Col sm={7}>
                  <Form.Control
                    name="course_key"
                    placeholder=""
                    onChange={e => setFormFieldValue(e.target.value, "course_key")}
                  />
                </Col>
              </Form.Group>
              <Form.Group as={Row} controlId="courseKeySubmitButton">
                <Col sm={5}>
                </Col>
                <Col sm={7}>
                  <Button variant="primary"
                      type="submit"
                      onClick={checkCourseKey}
                      disabled={!!requestInProcess ? true : false }
                  >
                    <FontAwesomeIcon icon="user-plus" /> Join the course
                  </Button>
                </Col>
              </Form.Group>
            </Form>
            :
            <Elements stripe={stripe_promise}>
              <CheckoutForm submitAction={submitAction}
                courseKey={formFieldValues.courseKey}
              />
            </Elements>
          }
        </Col>
        </Alert>
      </Col>
    </Row>
  )
}

export default withRecaptcha(JoinCourse);