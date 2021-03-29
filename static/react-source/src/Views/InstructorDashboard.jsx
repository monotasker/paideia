import "core-js/stable";
import "regenerator-runtime/runtime";
import React, { useState, useEffect, useContext } from "react";
import { useHistory, Link } from "react-router-dom";

import {
  Alert,
  Button,
  Col,
  Collapse,
  Form,
  FormGroup,
  Row,
  Spinner,
  Tab,
  Table,
  Tabs
} from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import moment from "moment";
import DayPickerInput from "react-day-picker/DayPickerInput";
import { formatDate, parseDate } from "react-day-picker/moment";
import 'react-day-picker/lib/style.css';

import { UserContext } from "../UserContext/UserProvider";
import { doApiCall,
         returnStatusCheck,
         isIntegerString } from "../Services/utilityService";
import { urlBase } from "../variables";
import { sendFormRequest,
         useFormManagement,
       } from "../Services/formsService";

const StudentRow = ({ studentData, classInProcess, history, dispatch,
                      defaults, courseId }) => {
  const [ showStudentDetails, setShowStudentDetails ] = useState(false);
  const [ fetchingStudent, setFetchingStudent ] = useState(false);

  let {uid, first_name, last_name, current_set, starting_set, ending_set,
        final_grade, grade, counts, start_date, end_date, custom_start, custom_end, previous_end_date, progress, custom_a_cap, custom_b_cap, custom_c_cap, custom_d_cap, tp_id} = studentData;

  const fieldsAndValidators = {
    [`starting_set%${uid}`]: ["number", starting_set],
    [`ending_set%${uid}`]: ["number", ending_set],
    [`grade%${uid}`]: ["alphanumeric", grade],
    [`custom_start%${uid}`]: ["date", moment(custom_start).toDate()],
    [`custom_end%${uid}`]: ["date", moment(custom_end).toDate()],
    [`custom_a_cap%${uid}`]: ["number", custom_a_cap],
    [`custom_b_cap%${uid}`]: ["number", custom_b_cap],
    [`custom_c_cap%${uid}`]: ["number", custom_c_cap],
    [`custom_d_cap%${uid}`]: ["number", custom_d_cap]
  };

  let {formFieldValues, setFormFieldValue,
        setFormFieldsDirectly, flags, setFlags, myCallbacks, showErrorDetails,
        setShowErrorDetails} = useFormManagement(fieldsAndValidators);

  const updateStudentData = event => {
    event.preventDefault();
    console.log("submitting--------");
    console.log(formFieldValues);
    console.log(Object.entries(formFieldValues));
    let submitValues = Object.entries(formFieldValues).map(
      ([key, value], i) => {
        // const newKey = key.split("%")[0];
        // const newValue = value===defaults[newKey] ? undefined : value;
        return([key.split("%")[0], value])
      }
    );
    console.log('submitValues');
    console.log(submitValues);
    let submitObject = Object.fromEntries(submitValues);
    console.log('submitObject');
    console.log(submitObject);
    submitObject.class_section = courseId;
    let myStartString = !!submitObject.custom_start ? submitObject.custom_start.toISOString() : null;
    let myEndString = !!submitObject.custom_end ? submitObject.custom_end.toISOString() : null;
    const updateData = {...submitObject, name: uid,
                        custom_start: myStartString, custom_end: myEndString};

    sendFormRequest(null, setFormFieldValue,
      {formId: `dashboard-student-info-${first_name}_${last_name}_${uid}`,
        fieldSet: updateData,
        requestAction: () => doApiCall(updateData, "update_student_data",
                                      "form"),
        history: history,
        dispatch: dispatch,
        successCallback: myCallbacks.successAction,
        otherCallbacks: {
          serverErrorAction: myCallbacks.serverErrorAction,
          badRequestAction: myCallbacks.badRequestAction,
          insufficientPrivilegesAction: myCallbacks.insufficientPrivilegesAction,
          notLoggedInAction: myCallbacks.notLoggedInAction
        },
        setInProgressAction: setFetchingStudent
      });
  }

  console.log('classInProcess');
  console.log(classInProcess);

  return(
    <Form role="form"
      id={`dashboard-student-info-${first_name}_${last_name}_${uid}`}
    >
      <Form.Row >
        <Col md={3}>
          <Link to={`/${urlBase}/profile/${uid}`}>
            {last_name}, {first_name}
          </Link>
        </Col>
        <Col md={2}>
          <span className="dashboard-student-info-current">
            <span className="dashboard-student-info-current-label">
              {!!classInProcess ? "Current" : "Final"} badge set
            </span>
            {!!classInProcess ? current_set : ending_set }
          </span>
        </Col>
        <Col md={2}>
          <span className="dashboard-student-info-starting-set">
            <span className="dashboard-student-info-starting-set-label">
              Started at set
            </span>
            {starting_set}
          </span>
        </Col>
        <Col md={2}>
          <span className="dashboard-student-info-progressed">
            <span className="dashboard-student-info-progressed-label">
              Progressed
            </span>
            {progress} sets
          </span>
        </Col>
        <Col md={2}>
          <span className="dashboard-student-info-letter">
            <span className="dashboard-student-info-letter-label">
              Earned{!!classInProcess ? " so far" : ""}
            </span>
            {grade}
          </span>
        </Col>
        <Col md={1}>
          <Button className="dashboard-student-info-show-details"
            onClick={() => setShowStudentDetails(!showStudentDetails)} size="sm" variant="primary"
          >
            <FontAwesomeIcon icon="angle-down" size="sm" />
          </Button>
        </Col>
      </Form.Row>
      <Collapse in={showStudentDetails}>
        <div className="dashboard-student-details-container">
      <Form.Row>
        <Col xs={12} md={6}>
          <h4>Recent Activity</h4>
          <Table className="dashboard-student-info-active" size="sm">
            <thead>
              <tr>
                <td></td>
                <td>Days active</td>
                <td>Days meeting minimum</td>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>This week</td>
                <td>{counts[0]}</td>
                <td>{counts[1]}</td>
              </tr>
              <tr>
                <td>Last week</td>
                <td>{counts[2]}</td>
                <td>{counts[3]}</td>
              </tr>
            </tbody>
          </Table>
        </Col>
        <Col xs={12} md={6} classNames="dashboard-student-info-dates">
          <h4>Individual Course Dates</h4>
          <Row>
            <Form.Group controlId={`custom_start%${uid}`}
              className={!formFieldValues[`custom_start%${uid}`] ? "default-value" : ""}
            >
              <Form.Label>Individual start date</Form.Label>
              <DayPickerInput
                onDayChange={day => setFormFieldValue(day, `custom_start%${uid}`)}
                formatDate={formatDate}
                parseDate={parseDate}
                format="LL"
                value={formFieldValues[`custom_start%${uid}`] || defaults.custom_start}
                placeholder={`${formatDate(
                  new Date(formFieldValues[`custom_start%${uid}`]), 'LL')}`}
                onChange={e => setFormFieldValue(e.target.value, `custom_start%${uid}`)}
              />
            </Form.Group>
          </Row>
          <Row>
            <Form.Group controlId={`custom_end%${uid}`}
              className={!formFieldValues[`custom_end%${uid}`] ? "default-value" : ""}
            >
              <Form.Label>Individual end date</Form.Label>
              <DayPickerInput
                onDayChange={day => setFormFieldValue(day, `custom_end%${uid}`)}
                formatDate={formatDate}
                parseDate={parseDate}
                format="LL"
                value={formFieldValues[`custom_end%${uid}`] || defaults.custom_end}
                placeholder={`${formatDate(
                  new Date(formFieldValues[`custom_end%${uid}`]), 'LL')}`}
                onChange={e => setFormFieldValue(e.target.value, `custom_end%${uid}`)}
              />
            </Form.Group>
          </Row>
        </Col>
        <Col xs={12} md={8} classNames="dashboard-student-info-caps">
          <h4>Individual grade caps</h4>
          <Table bordered size="sm">
            <thead>
              <tr>
                <td>A</td>
                <td>B</td>
                <td>C</td>
                <td>D</td>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <Form.Group controlId={`custom_a_cap%${uid}`}
                    className={!formFieldValues[`custom_a_cap%${uid}`] ? "default-value" : ""}
                  >
                    <Form.Control
                      value={formFieldValues[`custom_a_cap%${uid}`]}
                      placeholder={defaults.custom_a_cap}
                      onChange={e => setFormFieldValue(!!isIntegerString(e.target.value) ? parseInt(e.target.value) : "", `custom_a_cap%${uid}`)}
                    />
                  </Form.Group>
                </td>
                <td>
                  <Form.Group controlId={`custom_b_cap%${uid}`}
                    className={!formFieldValues[`custom_b_cap%${uid}`] ? "default-value" : ""}
                  >
                    <Form.Control
                      value={formFieldValues[`custom_b_cap%${uid}`] || defaults.custom_b_cap}
                      onChange={e => setFormFieldValue(parseInt(e.target.value), `custom_b_cap%${uid}`)}
                    />
                  </Form.Group>
                </td>
                <td>
                  <Form.Group controlId={`custom_c_cap%${uid}`}
                    className={!formFieldValues[`custom_c_cap%${uid}`] ? "default-value" : "new-value"}
                  >
                    <Form.Control
                      value={formFieldValues[`custom_c_cap%${uid}`] || defaults.custom_c_cap}
                      onChange={e => setFormFieldValue(parseInt(e.target.value), `custom_c_cap%${uid}`)}
                    />
                  </Form.Group>
                </td>
                <td>
                  <Form.Group controlId={`custom_d_cap%${uid}`}
                    className={!formFieldValues[`custom_d_cap%${uid}`] ? "default-value" : ""}
                  >
                    <Form.Control
                      value={formFieldValues[`custom_d_cap%${uid}`] || defaults.custom_d_cap}
                      onChange={e => setFormFieldValue(parseInt(e.target.value), `custom_d_cap%${uid}`)}
                      className={formFieldValues[`custom_d_cap%${uid}`]===defaults.custom_d_cap ? "default-value" : ""}
                    />
                  </Form.Group>
                </td>
              </tr>
            </tbody>
          </Table>
        </Col>
        <Col xs={12} md={4}>
          <Button variant="primary"
              type="submit"
              onClick={updateStudentData}
              disabled={!!fetchingStudent ? true : false }
          >
            <FontAwesomeIcon icon="save" /> Save changes
          </Button>
        </Col>
      </Form.Row>
      </div>

    </Collapse>
  </Form>
  );
}

const InstructorDashboard = () => {

    const { user, dispatch } = useContext(UserContext);
    const myhistory = useHistory();
    const [ courseKey, setCourseKey ] = useState();
    const [ myClasses, setMyClasses ] = useState(!!user.instructing ?
      user.instructing.sort(
        (a, b) => (Date.parse(a.start_date) > Date.parse(b.start_date)) ? -1 : 1)
      :
      []
    );
    const [ activeClassId, setActiveClassId ] = useState(
      myClasses.length > 0 ? myClasses[0].id : 0);
    // const [ activeClassInfo, setActiveClassInfo ] = useState(myClasses[0]);
    const [ classInProcess, setClassInProcess ] = useState(myClasses[0].in_process || undefined);
    const [ classMembers, setClassMembers ] = useState([]);
    const [ fetchingClass, setFetchingClass ] = useState(false);
    const history = useHistory();

    let classFieldsAndValidators = {id: null, institution: "string",
                                    academic_year: null, term: "string",
                                    course_section: "string",
                                    start_date: null, end_date: null,
                                    paths_per_day: "integer",
                                    days_per_week: "integer",
                                    a_target: "integer", b_target: "integer",
                                    c_target: "integer", d_target: "integer",
                                    f_target: "integer",
                                    a_cap: null, b_cap: null,
                                    c_cap: null, d_cap: null
                                   }

    // flags are unauthorized, serverError, badRequest, noRecord, success
    // callbacks are serErrorAction, unauthorizedAction,
    // badRequestAction, noRecordAction, successAction
    let {formFieldValues, setFormFieldValue, setFormFieldValuesDirectly,
         flags, setFlags, myCallbacks, showErrorDetails, setShowErrorDetails
        } = useFormManagement(classFieldsAndValidators);
    console.log("in main component: formFieldValues is:");
    console.log(formFieldValues);
    console.log("in main component: classMembers is:");
    console.log(classMembers);

    useEffect(() => {
      if ( activeClassId!==0 ) {
        setFetchingClass(true);
        doApiCall({course_id: activeClassId}, 'get_course_data', "JSON")
        .then(info => {
          returnStatusCheck(info, history,
            info => {
              console.log(info);
              if ( info.hasOwnProperty("institution") ) {
                let currentValues = {...formFieldValues};
                Object.keys(info).forEach(field => {
                  // console.log(`setting ${field} value: ${info[field]}`);
                  if (['start_date', 'end_date'].includes(field)) {
                    console.log(`setting ${field} value: ${info[field]}`);
                    currentValues = {...currentValues,
                                     [field]: moment(info[field]).toDate()};
                  } else if (!["members", "status_code"].includes(field)) {
                    currentValues = {...currentValues, [field]: info[field]};
                  }
                });
                setFormFieldValuesDirectly(currentValues);
                setClassMembers(info.members);
                setCourseKey(info.class_key);
                setClassInProcess(info.in_process);
                myCallbacks.successAction();
                setFetchingClass(false);
              } else {
                myCallbacks.serverErrorAction();
              }
            },
            dispatch,
            {insufficientPrivilegesAction: myCallbacks.unauthorizedAction,
            noRecordAction: myCallbacks.noRecordAction,
            serverErrorAction: myCallbacks.serverErrorAction
            }
          );
        });
      }
    }, [activeClassId]);

    const updateClassData = (event) => {
      event.preventDefault();
      let myStartString = formFieldValues.start_date.toISOString();
      let myEndString = formFieldValues.end_date.toISOString();
      const updateData = {...formFieldValues, id: activeClassId,
                          start_date: myStartString, end_date: myEndString};

      sendFormRequest(null, setFormFieldValue,
        {formId: 'dashboard-class-info-form',
         fieldSet: updateData,
         requestAction: () => doApiCall(updateData, "update_course_data",
                                        "form"),
         history: myhistory,
         dispatch: dispatch,
         successCallback: myCallbacks.successAction,
         otherCallbacks: {
           serverErrorAction: myCallbacks.serverErrorAction,
           badRequestAction: myCallbacks.badRequestAction,
           insufficientPrivilegesAction: myCallbacks.insufficientPrivilegesAction,
           notLoggedInAction: myCallbacks.notLoggedInAction
         },
         setInProgressAction: setFetchingClass
        });
    }
    console.log("flags:");
    console.log(flags);

    return(
      <Row className="dashboard-component content-view">
        <Col className="dashboard-component-inner-wrapper">
          { (!user || user.userLoggedIn !== true || !!flags.notLoggedIn ) &&
              myhistory.push(`/${urlBase}/login?need_login=true`)
          }
          { ( !user.userRoles || !["instructors", "administrators"]
                  .some(r => user.userRoles.includes(r) ) || !!flags.insufficientPrivileges ) ?
            <Alert variant="danger">
              <Col xs="auto">
                <FontAwesomeIcon size="2x" icon="exclamation-triangle" />
              </Col>
              <Col xs="10">
                Sorry, you have to be logged in as an instructor or administrator to enter this area.
              </Col>
            </Alert>
            :
          <React.Fragment>
          <h2>My Dashboard</h2>
          <Form.Group controlId="classFormClassSelector">
            <Form.Label>Choose a class group</Form.Label>
            <Form.Control as="select"
              onChange={e => setActiveClassId(e.target.value)}
            >
              {myClasses.map((c, index) =>
                <option key={index} value={c.id}>
                  {`${c.course_section}, ${c.term}, ${c.academic_year}, ${c.institution}`}
                </option>
              )}
            </Form.Control>
          </Form.Group>

        <Tabs>
        <Tab eventKey="course-details" title="Course Details" className="course-details">
        {!!fetchingClass ?
          <Spinner animation="grow" variant="info" />
          :
          <Form role="form"
            id="dashboard-class-info-form"
          >
            <Form.Row>
              <Col className="dashboard-class-basic" xs={12} md={6} lg={4}>
                <h3>Basic Info<FontAwesomeIcon icon="graduation-cap" /></h3>
                <Form.Group controlId="institution">
                  <Form.Label>Institution</Form.Label>
                  <Form.Control
                    value={formFieldValues.institution || ''}
                    onChange={e => setFormFieldValue(e.target.value, "institution")}
                  ></Form.Control>
                </Form.Group>
                <Form.Group controlId="course_section">
                  <Form.Label>Course Title</Form.Label>
                  <Form.Control
                    value={formFieldValues.course_section || ''}
                    onChange={e => setFormFieldValue(e.target.value, "course_section")}
                  ></Form.Control>
                </Form.Group>
                <Form.Row>
                  <Col>
                    <Form.Group controlId="academic_year">
                      <Form.Label>Year</Form.Label>
                      <Form.Control
                        value={formFieldValues.academic_year || ''}
                        onChange={e => setFormFieldValue(e.target.value, "academic_year")}
                      ></Form.Control>
                    </Form.Group>
                  </Col>
                  <Col>
                    <Form.Group controlId="term">
                      <Form.Label>Term</Form.Label>
                      <Form.Control
                        value={formFieldValues.term || ''}
                        onChange={e => setFormFieldValue(e.target.value, "term")}
                      ></Form.Control>
                    </Form.Group>
                  </Col>
                </Form.Row>
              </Col>
              <Col className="dashboard-class-key" xs={12} md={6} lg={4}>
                <h3>Course Registration Key<FontAwesomeIcon icon="key" /></h3>
                <span className="dashboard-class-key-string">{courseKey}</span>
                <Form.Text>Give this key to students in your classes. To join this
                  course group in Paideia, they need to enter the key at this link:
                </Form.Text>
                <FontAwesomeIcon icon="link" size="sm" /><Link to="join_course">https://learngreek.ca/paideia/join_course</Link>
                <Alert variant="info">Note that each student will be required to upgrade their account to "Student" level (paid) to join the course group if they are not already a premium supporter.
                </Alert>
              </Col>
              <Col className="dashboard-class-info" xs={12} md={6} lg={4}>
                <Row>
                  <Col>
                    <h3>Course Dates<FontAwesomeIcon icon="calendar-check"  /></h3>
                    <Form.Group controlId="start_date">
                      <Form.Label>Begins</Form.Label>
                      <DayPickerInput
                        onDayChange={day => setFormFieldValue(day, "start_date")}
                        formatDate={formatDate}
                        parseDate={parseDate}
                        format="LL"
                        // dayPickerProps={{
                        //   selectedDays: formFieldValues.start_date
                        // }}
                        value={formFieldValues.start_date}
                        placeholder={`${formatDate(new Date(formFieldValues.start_date), 'LL')}`}
                        onChange={e => setFormFieldValue(e.target.value, "start_date")}
                        // classNames="form-control"
                      />
                    </Form.Group>
                    <Form.Group controlId="end_date">
                      <Form.Label>Ends</Form.Label>
                      <DayPickerInput
                        onDayChange={day => setFormFieldValue(day, "end_date")}
                        formatDate={formatDate}
                        parseDate={parseDate}
                        format="LL"
                        // dayPickerProps={{
                        //   selectedDays: formFieldValues.end_date
                        // }}
                        value={formFieldValues.end_date}
                        placeholder={`${formatDate(new Date(formFieldValues.end_date), 'LL')}`}
                        onChange={e => setFormFieldValue(e.target.value, "end_date")}
                        // classNames="form-control"
                      />
                    </Form.Group>
                  </Col>
                </Row>
                <Row>
                  <Col>
                    <h3>Minimum Participation<FontAwesomeIcon icon="check-circle"  /></h3>
                    <Form.Text>
                        How much will you require your students to use Paideia? The app will track whether students are meeting these minimum targets.
                    </Form.Text>
                    <Form.Row>
                      <Col>
                        <Form.Group controlId="paths_per_day">
                          <Form.Label>Paths per day</Form.Label>
                          <Form.Control
                            value={formFieldValues.paths_per_day || ''}
                            onChange={e => setFormFieldValue(parseInt(e.target.value), "paths_per_day")}
                          ></Form.Control>
                        </Form.Group>
                      </Col>
                      <Col>
                        <Form.Group controlId="days_per_week">
                          <Form.Label>Days per week</Form.Label>
                          <Form.Control
                            value={formFieldValues.days_per_week || ''}
                            onChange={e => setFormFieldValue(parseInt(e.target.value), "days_per_week")}
                          ></Form.Control>
                        </Form.Group>
                      </Col>
                    </Form.Row>
                  </Col>
                </Row>
              </Col>
              <Col className="dashboard-class-targets" xs={12} md={6} lg={12}>
                <h3>Grading Targets<FontAwesomeIcon icon="bullseye"  /></h3>
                <Table size="sm">
                  <thead>
                    <tr>
                      <th>Letter Grade</th>
                      <th>Personal Set Progress</th>
                      <th></th>
                      <th>Absolute Set Reached</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>A</td>
                      <td>
                        <FormGroup controlId="a_target">
                          <Form.Control value={formFieldValues.a_target || ''}
                            onChange={e => setFormFieldValue(parseInt(e.target.value), "a_target")}
                          /> new sets
                        </FormGroup>
                      </td>
                      <td>OR</td>
                      <td>

                        <FormGroup controlId="a_cap">
                          Begin set <Form.Control value={formFieldValues.a_cap || ''}
                            onChange={e => setFormFieldValue(parseInt(e.target.value), "a_cap")}
                          />
                        </FormGroup>
                      </td>
                    </tr>
                    <tr>
                      <td>B</td>
                      <td>
                        <FormGroup controlId="b_target">
                          <Form.Control value={formFieldValues.b_target || ''}
                            onChange={e => setFormFieldValue(parseInt(e.target.value), "b_target")}
                          /> new sets
                        </FormGroup>
                      </td>
                      <td>OR</td>
                      <td>
                        <FormGroup controlId="b_cap">
                          Begin set <Form.Control value={formFieldValues.b_cap || ''}
                            onChange={e => setFormFieldValue(parseInt(e.target.value), "b_cap")}
                          />
                        </FormGroup>
                      </td>
                    </tr>
                    <tr>
                      <td>C</td>
                      <td>
                        <FormGroup controlId="c_target">
                          <Form.Control value={formFieldValues.c_target || ''}
                            onChange={e => setFormFieldValue(parseInt(e.target.value), "c_target")}
                          /> new sets
                        </FormGroup>
                      </td>
                      <td>OR</td>
                      <td>
                        <FormGroup controlId="c_cap">
                          Begin set <Form.Control value={formFieldValues.c_cap || ''}
                            onChange={e => setFormFieldValue(parseInt(e.target.value), "c_cap")}
                          />
                        </FormGroup>
                      </td>
                    </tr>
                    <tr>
                      <td>D</td>
                      <td>
                        <FormGroup controlId="d_target">
                          <Form.Control value={formFieldValues.d_target || ''}
                            onChange={e => setFormFieldValue(parseInt(e.target.value), "d_target")}
                          /> new sets
                        </FormGroup>
                      </td>
                      <td>OR</td>
                      <td>
                        <FormGroup controlId="d_cap">
                          Begin set <Form.Control value={formFieldValues.d_cap || ''}
                            onChange={e => setFormFieldValue(parseInt(e.target.value), "d_cap")}
                          />
                        </FormGroup>
                      </td>
                    </tr>
                    <tr>
                      <td>F</td>
                      <td>
                        <FormGroup controlId="f_target">
                          <Form.Control value={formFieldValues.f_target || ''}
                            onChange={e => setFormFieldValue(parseInt(e.target.value), "f_target")}
                          /> new sets
                        </FormGroup>
                      </td>
                      <td>OR</td>
                      <td>
                        NA
                      </td>
                    </tr>
                  </tbody>
                </Table>
              </Col>
            </Form.Row>
            <Button variant="primary"
                type="submit"
                onClick={updateClassData}
                disabled={!!fetchingClass ? true : false }
            >
              <FontAwesomeIcon icon="save" /> Save changes
            </Button>
          </Form>
        }
        </Tab> {/* end of course parameters tab */}

        <Tab eventKey="course-students" title="Students"
          className="course-students"
        >
        {!!fetchingClass ?
          <Spinner animation="grow" variant="info" />
          :
          <React.Fragment>
          {!!classMembers && classMembers.length > 0 &&
            classMembers.map(m =>
              <StudentRow studentData={m}
                classInProcess={classInProcess}
                history={myhistory}
                dispatch={dispatch}
                key={`${m.first_name}_${m.last_name}_${m.uid}`}
                defaults={
                  {custom_start: formFieldValues.start_date,
                   custom_end: formFieldValues.end_date,
                   custom_a_cap: formFieldValues.a_cap,
                   custom_b_cap: formFieldValues.b_cap,
                   custom_c_cap: formFieldValues.c_cap,
                   custom_d_cap: formFieldValues.d_cap
                }}
                courseId={formFieldValues.id}
              />
          )}
          </React.Fragment>
        }
        </Tab>
        </Tabs>
        </React.Fragment>
        }
        </Col>
      </Row>
    )
}

export default InstructorDashboard;