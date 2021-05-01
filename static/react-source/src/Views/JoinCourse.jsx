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
    Spinner,
    } from "react-bootstrap";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useElements, useStripe } from '@stripe/react-stripe-js';
import { withRecaptcha,
         joinCourseGroup } from '../Services/authService';
import { UserContext } from '../UserContext/UserProvider';
import { sendFormRequest,
         useFormManagement } from "../Services/formsService";
import { validateCourseKey,
         createCheckoutIntent
       } from "../Services/authService";
import { isAlphanumericString,
         isNumericString,
       } from "../Services/utilityService";

// FIXME: use actual publishable key in production
// const stripe_promise = loadStripe("pk_test_51IYtbhCzY7JkMiXGdU7a5MhH7UO6kk0pIiHEFZb5X4dKJ9KS98wdLKlfc4i9VCLekCtsRaV9uksdLTLNKP6Oy5sw000lqIdBpU");
const stripe_promise = loadStripe("pk_live_51IYtbhCzY7JkMiXGrewzvPLKJZz1K3As6DamvGqGDdXJwsJ0kswGXL2b1k4DvZcBu2B3d4Myfz4uILp80CbnRTGJ00ZUwOIsvf")

const CheckoutForm = ({ submitAction, courseKey, courseId, courseLabel }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [processing, setProcessing] = useState('');
  const [disabled, setDisabled] = useState(true);
  const [result, setResult] = useState({});
  const [clientSecret, setClientSecret] = useState('');
  const [joinFailed, setJoinFailed] = useState(false);
  const [joinFailureReason, setJoinFailureReason] = useState("");
  const myhistory = useHistory();
  const { user, dispatch } = useContext(UserContext);

  const fieldsAndValidators = {
    payment_name: ["string", `${user.firstName} ${user.lastName}`],
    payment_email: ["email", user.userEmail]
  };
  let {formFieldValues, setFormFieldValue, setFormFieldValuesDirectly,
    flags, setFlags, myCallbacks, showErrorDetails,
    setShowErrorDetails} = useFormManagement(fieldsAndValidators);

  // create object with state field value and setter for each field
  const fieldSet = {course_key: courseKey};

  myCallbacks.successAction = (data) => {
    setResult(data);
    setClientSecret(data.clientSecret);
  }

  myCallbacks.insufficientPrivilegesAction = (data) => {
    setFlags({missingRequestData: [],
              badRequestData: [],
              notLoggedIn: false,
              insufficientPrivileges: true,
              loginFailed: false,
              recaptchaFailed: false,
              actionBlocked: false,
              noRecord: false,
              dataConflict: false,
              serverError: false,
              success: true
            });
    if ( data.reason==="Stripe checkout session creation failed" ) {
      setFlags({...flags, serverError: data.error});
    }
    console.log(flags);
  }

  // Create PaymentIntent as soon as the page loads
  useEffect(() => {
    fieldSet.order_items = [{id: "student-membership"}];
    fieldSet.user_id = user.userId;
    submitAction(null,
      token => sendFormRequest(token, setFormFieldValue,
        {formId: 'joinClassPaymentForm',
         fieldSet: fieldSet,
         requestAction: createCheckoutIntent,
         extraArgs: ["token"],
         history: myhistory,
         dispatch: dispatch,
         successCallback: myCallbacks.successAction,
         otherCallbacks: myCallbacks,
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
        card: elements.getElement(CardElement),
        billing_details: {
          name: formFieldValues.payment_name,
          email: formFieldValues.payment_email
        }
      }
    });
    console.log(payload);
    if (payload.error) {
      setFlags({...flags,
                success: false,
                serverError: `Sorry, the payment failed. ${payload.error.message}`});
      setProcessing(false);
    } else {
      if (payload.paymentIntent.status==="succeeded") {
        setFlags({...flags,
                  serverError: false,
                  success: true});
        handleSuccess();
      }
      setProcessing(false);
    }
  };

  const handleSuccess = async () => {
    console.log("handling success***");
    let joinResult = await joinCourseGroup({user_id: user.userId,
                                      course_key: courseKey,
                                      course_id: courseId});
    console.log(joinResult);
    if (joinResult.status!=="success") {
      setJoinFailed(true);
      setJoinFailureReason(joinResult.error);
    }
  }

  return (
    <form id="joinClassPaymentForm" onSubmit={handleSubmit}>
      <h4>Checkout <FontAwesomeIcon icon="shopping-cart" size="sm" /></h4>
      {!flags.success &&
        <Row>
          <Col>
            <p>
              Complete your payment here to finish joining this course group. Before you click "Pay," make sure that you're joining the right course!
            </p>
          </Col>
        </Row>
      }
      <h5>Purchase item</h5>
      <Row className="purchase-item">
        <Col xs={2} className="purchase-item-img">
          <div className="purchase-item-img-wrapper">
            <FontAwesomeIcon icon="user-graduate" size="2x" />
          </div>
        </Col>
        <Col xs={7} className="purchase-item-desc">
          Paideia course group membership<br />
          <span className="checkout-courselabel">{courseLabel}</span>
        </Col>
        <Col xs={3} className="purchase-item-price">$15 cad<br />
          <span className="old-price">$30</span><br />
          <span className="discount-message">
            50% discount during beta
          </span>
        </Col>
      </Row>
      {!flags.success &&
      <>
        <h5>Payment information</h5>
        <Row >
          <Form.Label>Billing name</Form.Label>
          <Form.Control
            name="payment_name"
            placeholder=""
            disabled={false}
            onChange={e => setFormFieldValue(e.target.value, "payment_name")}
          />
          {/* <Form.Text>
            This must be exactly the same as the name on the
            credit card you use below.
          </Form.Text> */}
        </Row>
        <Form.Label>Payment method</Form.Label>
        <CardElement id="card-element" options={cardStyle} onChange={handleChange} />
        <Button
          disabled={processing || disabled || flags.success}
          id="submit"
          type="submit"
          variant="success"
        >
          {!!processing ? (
            <Spinner id="spinner" as="span" size="sm" animation="grow" role="status"
            aria-hidden="true" />
          ) : (
            "Pay $15 cad"
          )}
        </Button>
        <Button type="back"
          id="back"
          variant="secondary"
          onClick={() => { myhistory.push('/temp'); myhistory.goBack(); } }
        >
          Back
        </Button>
        <Button type="cancel"
          id="cancel"
          variant="secondary"
          onClick={() => myhistory.push("home")}
        >
          Cancel
        </Button>
      </>
      }
      {/* Show any error that happens when processing the payment */}
      {!!flags.serverError && (
        <Alert variant="danger">
          {flags.serverError}
        </Alert>
      )}
      {/* Show payment made upon completion */}
      {!!flags.success &&
      <>
        <h5>Payment Confirmation</h5>
        <Row className="payment-confirmation">
          <Col xs="2">
          </Col>
          <Col xs="7" className="paid-label">Total paid</Col>
          <Col xs="3" className="paid-amount">$15 cad</Col>
        </Row>
      </>
      }
      {/* Show a success message upon completion */}
      {!!flags.success &&
        <Alert variant="success" className="payment-success-alert">
          <Row>
            <Col className="icon-column" xs={1}>
              <FontAwesomeIcon icon="check-circle" size="2x" />
            </Col>
            <Col xs={11}>
              <h5>Payment succeeded!</h5>
              <p>You are now part of the course group. Your course information will appear on your <Link to="profile">user profile</Link>.</p>
            </Col>
          </Row>
        </Alert>
      }
      {/* Show any error that happens when joining course after payment */}
      {!!joinFailed &&
        <Alert variant="danger">
          <h5>Could not join class</h5>
          <p>
            Your payment was processed but something went wrong adding you to
            the course group. Please contact your instructor or the Paideia administrators to resolve the issue.
          </p>
          <p>{joinFailureReason}</p>
        </Alert>
      }
      {!!flags.success &&
        <Row className="print-page-message">
          <Col>
            <FontAwesomeIcon icon="print" size="sm" /> Print this page for your records
          </Col>
        </Row>
      }
      <Row className="powered-by-stripe">
        <Col>
          <FontAwesomeIcon icon="lock" size="sm" /> Safe and secure payment powered by <FontAwesomeIcon icon={["fab", "stripe"]} size="2x" />
        </Col>
      </Row>
    </form>
  )
}


const KeyValidationForm = ({courseKeySetter,
                            courseIdSetter,
                            courseLabelSetter,
                            setShowPaymentForm,
                            submitAction}) => {
  const myhistory = useHistory();
  const { user, dispatch } = useContext(UserContext);
  const [ requestInProcess, setRequestInProcess ] = useState(false);

  const fieldsAndValidators = {
    first_name: "string",
    last_name: "string",
    email: "email",
    timezone: "string",
    course_key: (val) => isAlphanumericString(val),
    user_id: [val => isNumericString(val), user.userId]
  }

  let {formFieldValues, setFormFieldValue, setFormFieldValuesDirectly,
    flags, setFlags, myCallbacks, showErrorDetails,
    setShowErrorDetails} = useFormManagement(fieldsAndValidators);

  // create object with state field value and setter for each field
  const fieldNames = Object.keys(fieldsAndValidators);
  const fieldSet = fieldNames.reduce((current, myName) => {
    return {...current, [myName]: formFieldValues[myName]}
  }, {});

  myCallbacks.successAction = (data) => {
    courseIdSetter(data.class_id);
    courseLabelSetter(data.class_label);
    courseKeySetter(formFieldValues.course_key)
    setShowPaymentForm(true);
    setFlags({missingRequestData: [],
              badRequestData: [],
              notLoggedIn: false,
              insufficientPrivileges: false,
              loginFailed: false,
              recaptchaFailed: false,
              actionBlocked: false,
              noRecord: false,
              dataConflict: false,
              serverError: false,
              success: true
            });
  }

  const checkCourseKey = (event) => {
    submitAction(event,
      token => sendFormRequest(token, setFormFieldValue,
        {formId: 'courseKeyForm',
         fieldSet: fieldSet,
         requestAction: validateCourseKey,
         extraArgs: ["token"],
         history: myhistory,
         dispatch: dispatch,
         successCallback: myCallbacks.successAction,
         otherCallbacks: myCallbacks,
        setInProgressAction: setRequestInProcess
      })
    );
  }

  return (
    <>
      <p>
        Enter the course key below to have the currently signed-in
        Paideia user placed in the corresponding course group.
      </p>
      <Alert variant="warning">
        <Row>
          <Col xs={1} className="icon-column">
            <FontAwesomeIcon icon="exclamation-circle" size="2x" />
          </Col>
          <Col xs={11}>
            If the information below doesn't match the account you want to use,
            log out and then log in again to the correct account before
            going any further.
          </Col>
        </Row>
      </Alert>
      <Form
        role="form"
        id="courseKeyForm"
      >
        <Form.Group as={Row} controlId="first_name">
          <Form.Label column sm={5}>
            Given name
          </Form.Label>
          <Col sm={7}>
            <Form.Control
              name="first_name"
              placeholder=""
              disabled={true}
              value={user.firstName}
              // onChange={e => setFormFieldValue(e.target.value, "email")}
            />
          </Col>
        </Form.Group>
        <Form.Group as={Row} controlId="last_name">
          <Form.Label column sm={5}>
            Family name
          </Form.Label>
          <Col sm={7}>
            <Form.Control
              name="last_name"
              placeholder=""
              disabled={true}
              value={user.lastName}
              // onChange={e => setFormFieldValue(e.target.value, "email")}
            />
          </Col>
        </Form.Group>
        <Form.Group as={Row} controlId="email">
          <Form.Label column sm={5}>
            Email
          </Form.Label>
          <Col sm={7}>
            <Form.Control
              name="email"
              placeholder=""
              disabled={true}
              value={user.userEmail}
              // onChange={e => setFormFieldValue(e.target.value, "email")}
            />
          </Col>
        </Form.Group>
        <Form.Group as={Row} controlId="timezone">
          <Form.Label column sm={5}>
            Time zone
          </Form.Label>
          <Col sm={7}>
            <Form.Control
              name="timezone"
              placeholder=""
              disabled={true}
              value={user.userTimezone}
              // onChange={e => setFormFieldValue(e.target.value, "email")}
            />
          </Col>
        </Form.Group>
        <Form.Group as={Row} controlId="course_key">
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
              {!!requestInProcess ?
                <Spinner animation="grow" size="sm" as="span" aria-hidden="true" role="status" /> : <FontAwesomeIcon icon="user-plus" />}
              {" "}Join the course
            </Button>
            <Button type="cancel"
              variant="secondary"
              onClick={() => myhistory.push("home")}
            >
              Cancel
            </Button>
          </Col>
        </Form.Group>
        {!!flags.noRecord &&
            <Alert variant="danger" className="col col-sm-12">
              <Row>
                <Col xs={1} className="icon-column">
                  <FontAwesomeIcon icon="exclamation-triangle" size="2x" />
                </Col>
                <Col>
                Sorry, that isn't a valid course key. Contact your instructor to request the current key for your course.
                </Col>
              </Row>
            </Alert>
        }
        {!!flags.insufficientPrivileges &&
            <Alert variant="danger" className="col col-sm-12">
              <Row>
                <Col xs={1} className="icon-column">
                  <FontAwesomeIcon icon="exclamation-triangle" size="2x" />
                </Col>
                <Col>
                Sorry, that course key is expired. Contact your instructor to request the current key for your course.
                </Col>
              </Row>
            </Alert>
        }
        {!!flags.missingRequestData && flags.missingRequestData.includes("course_key") &&
            <Alert variant="danger" className="col col-sm-12">
              <Row>
                <Col xs={1} className="icon-column">
                  <FontAwesomeIcon icon="exclamation-triangle" size="2x" />
                </Col>
                <Col>
                Type your course key in the box above before clicking the button to join the course.
                </Col>
              </Row>
            </Alert>
        }
        {!!flags.dataConflict &&
            <Alert variant="danger" className="col col-sm-12">
              <Row>
                <Col xs={1} className="icon-column">
                  <FontAwesomeIcon icon="exclamation-triangle" size="2x" />
                </Col>
                <Col>
                You are already a member of that course group. You should see the course information on your user profile.
                </Col>
              </Row>

            </Alert>
        }
      </Form>
      {!!flags.serverError &&
        <Alert variant="danger">
          <h4>Something Went Wrong</h4>
          <p>{flags.serverError}</p>
        </Alert>
      }
    </>
  )
}

const JoinCourse = ({ submitAction }) => {
  const { user, dispatch } = useContext(UserContext);
  const [ courseLabel, setCourseLabel ] = useState("");
  const [ courseId, setCourseId ] = useState();
  const [ courseKey, setCourseKey ] = useState("");
  const [ showPaymentForm, setShowPaymentForm ] = useState(false);

  return(
    <Row className="join-course-component content-view justify-content-sm-center">
      <Col sm={8} lg={6} xl={4}>
        <h2 className="text-center">Join a Course Group Here!</h2>
        <Alert variant="success" className="row error-message">
          <p>You've found the page for joining a course group on Paideia. While the app is free to use for your personal enrichment, there is a fee to use Paideia as part of a course.</p>
        </Alert>
        <br />
        {!showPaymentForm ?
          ( user.userLoggedIn !== true ?
            <p>
              You aren't signed in to a Paideia user account. Before joining
              a course group, <Link to="register?joining_course=true">sign up</Link> or <Link to="login?joining_course=true">log in</Link> to your account.
            </p>
            :
            <KeyValidationForm
              submitAction={submitAction}
              courseKeySetter={setCourseKey}
              courseIdSetter={setCourseId}
              courseLabelSetter={setCourseLabel}
              setShowPaymentForm={setShowPaymentForm}
            />
          )
          :
          <Elements stripe={stripe_promise}>
            <CheckoutForm
              submitAction={submitAction}
              courseKey={courseKey}
              courseLabel={courseLabel}
              courseId={courseId}
            />
          </Elements>
        }
      </Col>
    </Row>
  )
}

export default withRecaptcha(JoinCourse);