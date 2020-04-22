import React, { useState, useEffect, useContext } from "react";

import {
  Row,
  Col,
  Form,
  Spinner,
} from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import {UserContext} from "../UserContext/UserProvider";


const InstructorDashboard = () => {

    const { user, reducer } = useContext(UserContext);
    const [ myClasses, setMyClasses ] = useState(user.instructing.sort(
        (a, b) => (Date.parse(a.start_date) > Date.parse(b.start_date)) ? -1 : 1)
    );
    const [ activeClassId, setActiveClassId ] = useState(myClasses[0].id);
    const [ classInstitution, setClassInstitution ] = useState(myClasses[0].institution);
    const [ classYear, setClassYear ] = useState(myClasses[0].academic_year);
    const [ classTerm, setClassTerm ] = useState(myClasses[0].term);
    const [ classSection, setClassSection ] = useState(myClasses[0].course_section);
    const [ classStart, setClassStart ] = useState(myClasses[0].start_date);
    const [ classEnd, setClassEnd ] = useState(myClasses[0].end_date);
    const [ classDailyQuota, setClassDailyQuota ] = useState(myClasses[0].paths_per_day);
    const [ classWeeklyQuota, setClassWeeklyQuota ] = useState(myClasses[0].days_per_week);
    const [ classTargetA, setClassTargetA ] = useState(myClasses[0].a_target);
    const [ classTargetB, setClassTargetB ] = useState(myClasses[0].b_target);
    const [ classTargetC, setClassTargetC ] = useState(myClasses[0].c_target);
    const [ classTargetD, setClassTargetD ] = useState(myClasses[0].d_target);
    const [ classTargetF, setClassTargetF ] = useState(myClasses[0].f_target);
    const [ classCapA, setClassCapA ] = useState(myClasses[0].a_cap);
    const [ classCapB, setClassCapB ] = useState(myClasses[0].b_cap);
    const [ classCapC, setClassCapC ] = useState(myClasses[0].c_cap);
    const [ classCapD, setClassCapD ] = useState(myClasses[0].d_cap);
    const [ classMembers, setClassMembers ] = useState([]);
    const [ classSignInLink, setClassSignInLink ] = useState(null);
    const [ classRegCode, setClassRegCode ] = useState(null);

    useEffect(() => {

    }
    )

    return(
    <Row className="dashboard-component content-view">
      <h2>My Dashboard</h2>
      <Col className="dashboard-class-selector" xs={12} lg={4}>
        <Form.Group controlId="exampleForm.ControlSelect1">
          <Form.Label>Example select</Form.Label>
          <Form.Control as="select">
            {myClasses.map((c, index) =>
              <option key={index}>
                {`${c.course_section}, ${c.term}, ${c.academic_year}, ${c.institution}`}
              </option>
            )}
          </Form.Control>
        </Form.Group>
      </Col>

      <Col className="dashboard-classes" xs={12} lg={4}>
        <Form.Group controlId="exampleForm.ControlSelect1">
          <Form.Label>Example select</Form.Label>
          <Form.Control as="select">
            {myClasses.map((c, index) =>
              <option key={index}>
                {`${c.course_section}, ${c.term}, ${c.academic_year}`}
              </option>
            )}
          </Form.Control>
        </Form.Group>
      </Col>
    </Row>
    )
}

export default InstructorDashboard;