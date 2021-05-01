import React, {
  useContext,
  useEffect,
  useState
} from "react";
import {
  Form,
  Button,
  Row,
  Col,
  Alert
} from "react-bootstrap";
import { Typeahead } from 'react-bootstrap-typeahead';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { useHistory,
         Link
       } from 'react-router-dom';
import moment from 'moment';
import 'moment-timezone';

import { register,
         withRecaptcha
       } from '../Services/authService';
import { UserContext } from '../UserContext/UserProvider';

import { useQuery } from "../Services/utilityService";
import { sendFormRequest,
         useFormManagement } from "../Services/formsService";

const Register = ({submitAction}) => {
  const { user, dispatch } = useContext(UserContext);
  const myhistory = useHistory();
  const queryParams = useQuery();
  // const [ myTimeZone, setMyTimeZone ] = useState("America/Toronto");
  const [ requestInProgress, setRequestInProgress ] = useState(false);

  const fieldsAndValidators = {last_name: null, first_name: null,
                               email: "email", time_zone: null,
                               password: "password"}

  let { formFieldValues, setFormFieldValue, setFormFieldsDirectly,
        flags, setFlags, myCallbacks, showErrorDetails, setShowErrorDetails
      } = useFormManagement(fieldsAndValidators);
  if ( formFieldValues.time_zone===null ) {
    setFormFieldValue("America/Toronto", "time_zone");
  }

  myCallbacks.successAction = (data) => {
      let joining = queryParams.get("joining_course")==="true" ?
        "&joining_course=true" : "";
      myhistory.push(`login?just_registered=true${joining}`);
  }

  // create object with state field value and setter for each field
  const fieldNames = Object.keys(fieldsAndValidators);
  const fieldSet = fieldNames.reduce((current, myName) => {
    return {...current, [myName]: formFieldValues[myName]}
  }, {});
  console.log('before submission: fieldSet is');
  console.log(fieldSet);

  const getRegistration = (event) => {
    submitAction(event,
      token => sendFormRequest(token, setFormFieldValue,
        {formId: 'registrationForm',
         fieldSet: fieldSet,
         requestAction: register,
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
        setInProgressAction: setRequestInProgress
      })
    );
  }

  return(
    <Row className="register-component content-view justify-content-sm-center">
      <Col sm={8} lg={6} xl={4}>
        { user.userLoggedIn === true &&
          (myhistory.length <= 3 ?
            myhistory.push('profile')
            :
            myhistory.goBack()
          )
        }
        { user.userLoggedIn === false && (
          <React.Fragment>
          <h2 className="text-center">Create an account here!</h2>
          {!!flags.serverError &&
            <Alert variant="danger" className="row error-message">
              <Col xs="auto">
                <FontAwesomeIcon icon="exclamation-triangle" size="2x" />
              </Col>
              <Col xs="10">
                 Sorry, something went wrong with your registration. But if you contact the administrators they can help to resolve the problem.
                {/* FIXME: Add link to contact form here. */}
              </Col>
            </Alert>
          }
          {!!flags.missingRequestData &&
              flags.missingRequestData.length > 0 &&
            <Alert variant="danger" className="row error-message">
              <Col xs="auto">
                <FontAwesomeIcon icon="exclamation-triangle" size="2x" />
              </Col>
              <Col xs="10">
               Sorry, you didn't fill in all of the fields. Fill in the missing information and try again.
              {/* FIXME: Add link to contact form here. */}
              </Col>
            </Alert>
          }
          <Form
            role="form"
            id="registrationForm"
          >
            <Form.Group as={Row} controlId="first_name">
              <Form.Label column sm={5}>
                First Name
              </Form.Label>
              <Col sm={7}>
                <Form.Control
                  name="first_name"
                  placeholder="Enter your first name"
                  autoComplete="given-name"
                  onChange={e => setFormFieldValue(e.target.value, "first_name")}
                />
              </Col>
              {!!flags.missingRequestData &&
                  flags.missingRequestData.includes("first_name") &&
                <Alert variant="danger" className="col col-sm-12">
                  <FontAwesomeIcon icon="exclamation-triangle" /> You need to provide a first name.
                </Alert>
              }
            </Form.Group>
            <Form.Group as={Row} controlId="last_name">
              <Form.Label column sm={5}>
                Last Name
              </Form.Label>
              <Col sm={7}>
                <Form.Control
                  name="last_name"
                  placeholder="Enter your surname or family name"
                  autoComplete="family-name"
                  onChange={e => setFormFieldValue(e.target.value, "last_name")}
                />
              </Col>
              {!!flags.missingRequestData &&
                  flags.missingRequestData.includes("last_name") &&
                <Alert variant="danger" className="col col-sm-12">
                  <FontAwesomeIcon icon="exclamation-triangle" /> You need to provide a last name.
                </Alert>
              }
            </Form.Group>
            <Form.Group as={Row} controlId="email">
              <Form.Label column sm={5}>
                Email
              </Form.Label>
              <Col sm={7}>
                <Form.Control
                  type="email"
                  name="email"
                  placeholder="Enter your email address"
                  autoComplete="email"
                  onChange={e => setFormFieldValue(e.target.value, "email")}
                />
              </Col>
              {(!!flags.badRequestData &&
                  flags.badRequestData.includes("email")) &&
                <Alert variant="danger" className="col col-sm-12">
                  <FontAwesomeIcon icon="exclamation-triangle" /> You need to provide a valid email address.
                </Alert>
              }
              {(!!flags.missingRequestData &&
                  flags.missingRequestData.includes("email")) ?
                <Alert variant="danger" className="col col-sm-12">
                  <FontAwesomeIcon icon="exclamation-triangle" /> You need to provide your email address.
                </Alert>
                :
                (!!flags.dataConflict ?
                  <Alert variant="danger" className="row error-message">
                    <Col xs="auto">
                      <FontAwesomeIcon size="2x" icon="exclamation-triangle" />
                    </Col>
                    <Col xs="10">
                      A user with that email already exists. Try logging in <Link to="login">here</Link>. If you can't remember your password you can recover it from the login screen.
                    </Col>
                  </Alert>
                  :
                  <Form.Text className="text-muted col col-sm-12">
                    We'll never share your email with anyone else. We'll only
                    use this to identify you and to contact you for things like
                    resetting your password.
                  </Form.Text>
                )
              }
            </Form.Group>
            <Form.Group as={Row} controlId="time_zone">
              <Form.Label column sm={5}>
                Your Time Zone
              </Form.Label>
              <Col sm={7}>
                <Typeahead
                  id="time_zone"
                  labelKey="tz"
                  inputProps={{name: "time_zone"}}
                  placeholder="Choose a time zone"
                  onChange={selected => setFormFieldValue(selected, "time_zone")}
                  options={moment.tz.names()}
                  defaultInputValue={!Array.isArray(formFieldValues.time_zone) ? formFieldValues.time_zone : formFieldValues.time_zone[0]}
                />
              </Col>
              {(!!flags.missingRequestData &&
                    flags.missingRequestData.includes("time_zone")) ?
                  <Alert variant="danger" className="col col-sm-12">
                    <FontAwesomeIcon icon="exclamation-triangle" /> You need to provide a valid time zone.
                  </Alert>
                :
                  <Form.Text className="text-muted col col-xs col-sm-12">
                    When we analyze your learning on this app, your time zone will help us to know when you're starting a new day of activity.
                  </Form.Text>
              }
            </Form.Group>
            <Form.Group as={Row} controlId="password">
              <Form.Label column sm={5}>
                Password
              </Form.Label>
              <Col sm={7}>
                <Form.Control
                  type="password"
                  name="password"
                  autoComplete="new-password"
                  placeholder="Enter a password"
                  onChange={e => setFormFieldValue(e.target.value, "password")}
                />
              </Col>
              {(!!flags.missingRequestData &&
                    flags.missingRequestData.includes("password")) ?
                  <Alert variant="danger" className="col col-sm-12">
                    <FontAwesomeIcon icon="exclamation-triangle" /> You need to provide a password.
                  </Alert>
                  :
                  (!!flags.badRequestData &&
                      flags.badRequestData.includes("password") &&
                    <Alert variant="danger" className="row error-message">
                      <Col xs="auto">
                        <FontAwesomeIcon size="2x" icon="exclamation-triangle" /></Col>
                      <Col xs="10">
                        The password you chose isn't strong enough. Try a different password.
                      </Col>
                    </Alert>
                  )
              }
              <Form.Text className="text-muted col col-xs col-sm-12">
                Your password must be at least 8 characters long. It must also include at least one upper case character and one number. Consider also including a special character (like #, &, !, etc.) and making it longer (up to 20 characters).
              </Form.Text>
            </Form.Group>
            <Form.Group as={Row} controlId="registerSubmitButton">
              <Col xs sm={5}>
              </Col>
              <Col className="register-submit-col">
                <Button variant="primary"
                    type="submit"
                    onClick={getRegistration}
                    disabled={!!requestInProgress ? true : false }
                >
                  <FontAwesomeIcon icon="user-plus" /> Create account
                </Button>
              </Col>
            </Form.Group>
          </Form>
          <Alert variant="success"
            className="register-login-message"
          >
            <span>Already have an account?</span>
            <Button as={Link} to={`login`}
              variant="outline-success"
            >
              <FontAwesomeIcon icon="sign-in-alt" /> Log in
            </Button>
          </Alert>
          </React.Fragment>
        )}
      </Col>
    </Row>
  );
}

export default withRecaptcha(Register);
