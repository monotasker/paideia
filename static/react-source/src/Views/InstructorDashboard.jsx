import "core-js/stable";
import "regenerator-runtime/runtime";
import React, { useState, useEffect, useContext } from "react";
import { useHistory, Link } from "react-router-dom";

import {
  Alert,
  Button,
  Col,
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
import { doApiCall, returnStatusCheck } from "../Services/utilityService";
import { urlBase } from "../variables";
import { sendFormRequest,
         useFormManagement,
       } from "../Services/formsService";

const StudentRow = () => {

    let studentFieldsAndValidators = {

    };


    let {studentFormFieldValues, setStudentFormFieldValue,
         setStudentFieldDirectly, studentFlags, setStudentFlags, myStudentCallbacks, showStudentErrorDetails,
         setShowStudentErrorDetails} = useFormManagement(studentFieldsAndValidators);

}

const InstructorDashboard = () => {

    const { user, dispatch } = useContext(UserContext);
    const myhistory = useHistory();
    const [ myClasses, setMyClasses ] = useState(!!user.instructing ?
      user.instructing.sort(
        (a, b) => (Date.parse(a.start_date) > Date.parse(b.start_date)) ? -1 : 1)
      :
      []
    );
    const [ activeClassId, setActiveClassId ] = useState(
      myClasses.length > 0 ? myClasses[0].id : 0);
    const [ activeClassInfo, setActiveClassInfo ] = useState(myClasses[0]);
    const [ classInProcess, setClassInProcess ] = useState();
    const [ classMembers, setClassMembers ] = useState([]);
    const [ fetchingClass, setFetchingClass ] = useState(false);
    const [ fetchingStudents, setFetchingStudents ] = useState(false);
    const history = useHistory();

    let classFieldsAndValidators = {id: null, institution: null,
                                    academic_year: null, term: null,
                                    course_section: null,
                                    start_date: null, end_date: null,
                                    paths_per_day: null,
                                    days_per_week: null,
                                    a_target: null, b_target: null,
                                    c_target: null, d_target: null,
                                    f_target: null,
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
                  console.log(`setting ${field} value: ${info[field]}`);
                  if (['start_date', 'end_date'].includes(field)) {
                    currentValues = {...currentValues,
                                     [field]: moment(info[field]).toDate()};
                  } else if (!["members", "status_code"].includes(field)) {
                    currentValues = {...currentValues, [field]: info[field]};
                  }
                });
                setFormFieldValuesDirectly(currentValues);
                setClassMembers(info.classMembers);
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
      const updateData = {...formFieldValues, id: activeClassId};

      sendFormRequest(null, {
          formId: 'dashboard-class-info-form',
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


    return(
      <Row className="dashboard-component content-view">
        <Col>
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
          <Form.Group controlId="classForm.classSelector">
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
        <Tab eventKey="course-details" title="Course Details">
        <Form role="form"
          id="dashboard-class-info-form"
        >
          <Form.Row>
            <Col className="dashboard-class-info" xs={12} lg={4}>
              {!!fetchingClass && <Spinner animation="grow" variant="info" />}
              <h3>
                {formFieldValues.institution} {formFieldValues.term} {formFieldValues.academic_year}
              </h3>
              <Form.Group controlId="start_date">
                <Form.Label>Begins</Form.Label>
                <DayPickerInput
                  onDayChange={day => setFormFieldValue(day, "start_date")}
                  formatDate={formatDate}
                  parseDate={parseDate}
                  format="LL"
                  dayPickerProps={{
                    selectedDays: formFieldValues.start_date
                  }}
                  placeholder={`${formatDate(new Date(formFieldValues.start_date), 'LL')}`}
                  onChange={e => setFormFieldValue(e.target.value, "start_date")}
                />
              </Form.Group>
              <Form.Group controlId="end_date">
                <Form.Label>Ends</Form.Label>
                <DayPickerInput
                  onDayChange={day => setFormFieldValue(day, "end_date")}
                  formatDate={formatDate}
                  parseDate={parseDate}
                  format="LL"
                  dayPickerProps={{
                    selectedDays: formFieldValues.end_date
                  }}
                  placeholder={`${formatDate(new Date(formFieldValues.end_date), 'LL')}`}
                  onChange={e => setFormFieldValue(e.target.value, "end_date")}
                />
              </Form.Group>
            </Col>
            <Col>
              <h4>Minimum Participation Requirements</h4>
              <Form.Group controlId="paths_per_day">
                <Form.Label>Minimum paths / day</Form.Label>
                <Form.Control
                  value={formFieldValues.paths_per_day}
                  onChange={e => setFormFieldValue(e.target.value, "paths_per_day")}
                ></Form.Control>
              </Form.Group>
              <Form.Group controlId="days_per_week">
                <Form.Label>Minimum days / week</Form.Label>
                <Form.Control
                  value={formFieldValues.days_per_week}
                  onChange={e => setFormFieldValue(e.target.value, "days_per_week")}
                ></Form.Control>
              </Form.Group>
            </Col>
            <Col>
              <h4>Grading Targets</h4>
              <Table>
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
                        <Form.Control value={formFieldValues.a_target}
                          onChange={e => setFormFieldValue(e.target.value, "a_target")}
                        />
                      </FormGroup> new sets
                    </td>
                    <td>OR</td>
                    <td>

                      <FormGroup controlId="a_cap">
                        Begin set <Form.Control value={formFieldValues.a_cap}
                          onChange={e => setFormFieldValue(e.target.value, "a_cap")}
                        />
                      </FormGroup>
                    </td>
                  </tr>
                  <tr>
                    <td>B</td>
                    <td>
                      <FormGroup controlId="b_target">
                        <Form.Control value={formFieldValues.b_target}
                          onChange={e => setFormFieldValue(e.target.value, "b_target")}
                        /> new sets
                      </FormGroup>
                    </td>
                    <td>OR</td>
                    <td>
                      <FormGroup controlId="b_cap">
                        Begin set <Form.Control value={formFieldValues.b_cap}
                          onChange={e => setFormFieldValue(e.target.value, "b_cap")}
                        />
                      </FormGroup>
                    </td>
                  </tr>
                  <tr>
                    <td>C</td>
                    <td>
                      <FormGroup controlId="c_target">
                        <Form.Control value={formFieldValues.c_target}
                          onChange={e => setFormFieldValue(e.target.value, "c_target")}
                        /> new sets
                      </FormGroup>
                    </td>
                    <td>OR</td>
                    <td>
                      <FormGroup controlId="c_cap">
                        Begin set <Form.Control value={formFieldValues.c_cap}
                          onChange={e => setFormFieldValue(e.target.value, "c_cap")}
                        />
                      </FormGroup>
                    </td>
                  </tr>
                  <tr>
                    <td>D</td>
                    <td>
                      <FormGroup controlId="d_target">
                        <Form.Control value={formFieldValues.d_target}
                          onChange={e => setFormFieldValue(e.target.value, "d_target")}
                        /> new sets
                      </FormGroup>
                    </td>
                    <td>OR</td>
                    <td>
                      <FormGroup controlId="d_cap">
                        Begin set <Form.Control value={formFieldValues.d_cap}
                          onChange={e => setFormFieldValue(e.target.value, "d_cap")}
                        />
                      </FormGroup>
                    </td>
                  </tr>
                  <tr>
                    <td>F</td>
                    <td>
                      <FormGroup controlId="f_target">
                        <Form.Control value={formFieldValues.f_target}
                          onChange={e => setFormFieldValue(e.target.value, "f_target")}
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
        </Tab> {/* end of course parameters tab */}

        <Tab eventKey="course-students" title="Students">
          <Table className="course-students-table">
            <thead>
              <tr>
                <td>Family Name</td>
                <td>Given Name</td>
                <td>
                  {!!classInProcess ? "Current badge set" : "Final badge set"}
                </td>
                <td>Starting badge set</td>
                <td>Progress this course</td>
                <td>Current grade achieved</td>
              </tr>
            </thead>
            <tbody>
              {!!classMembers && classMembers.length > 0 &&
                classMembers.map(m =>
              <React.Fragment key={`${m.first_name}_${m.last_name}`}>
              <tr >
                <td rowSpan="2">
                  <Link to={`/${urlBase}/profile/${m.uid}`}>
                    {m.last_name}
                  </Link>
                </td>
                <td>
                  <Link to={`/${urlBase}/profile/${m.uid}`}>
                    {m.first_name}
                  </Link>
                </td>
                <td>{!!classInProcess ? m.current_set : m.ending_set }</td>
                <td>{m.starting_set}</td>
                <td>{m.progress} badge sets</td>
                <td>{m.grade}</td>
                {/* <td>{m.custom_start}</td>
                <td>{m.custom_end}</td>
                <td>{m.starting_set}</td>
                <td>{m.ending_set}</td>
                <td>{m.custom_a_cap}</td>
                <td>{m.custom_b_cap}</td>
                <td>{m.custom_c_cap}</td>
                <td>{m.custom_d_cap}</td>
                <td>{m.final_grade}</td> */}
              </tr>
              <tr>
                {/* two cells blocked off by name */}
                <td colSpan="5">
                  <Table>
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
                        <td>{m.counts[0]}</td>
                        <td>{m.counts[1]}</td>
                      </tr>
                      <tr>
                        <td>Last week</td>
                        <td>{m.counts[2]}</td>
                        <td>{m.counts[3]}</td>
                      </tr>
                    </tbody>
                  </Table>
                  <Table>
                    <tbody>
                      <tr>
                        <td>Individual start date</td>
                        <td>{m.custom_start}</td>
                      </tr>
                      <tr>
                        <td>Individual end date</td>
                        <td>{m.custom_end}</td>
                      </tr>
                    </tbody>
                  </Table>
                  <Table>
                    <thead>
                      <tr>
                        <td>Individual grade caps</td>
                      </tr>
                      <tr>
                        <td>A</td>
                        <td>B</td>
                        <td>C</td>
                        <td>D</td>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>{m.custom_a_cap}</td>
                        <td>{m.custom_a_cap}</td>
                        <td>{m.custom_c_cap}</td>
                        <td>{m.custom_d_cap}</td>
                      </tr>
                    </tbody>
                  </Table>
                </td>
              </tr>
              </React.Fragment>
              )}
            </tbody>
          </Table>
        </Tab>
        </Tabs>
        </React.Fragment>
        }
        </Col>
      </Row>
    )
}

export default InstructorDashboard;