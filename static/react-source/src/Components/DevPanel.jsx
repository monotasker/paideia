import React, { useState } from "react";
import {
  Button,
  Form,
  Offcanvas
} from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { ErrorMessage, Formik } from "formik";
import * as Yup from 'yup';

const PathTestForm = () => {
  return(
    <Formik
      initialValues={ {pathnum: "", stepnum: "", location: "",
                      flagsFreshUser: false, flagsViewLessons: false,
                      flagsNewBadges: false, flagsRedirect: false,
                      flagsQuotaReached: false}}
      validationSchema={Yup.object({
        pathnum: Yup.number().positive().integer("Must be a number"),
        stepnum: Yup.number("Must be a number"),
        flagsFreshUser: Yup.boolean(),
        flagsViewLessons: Yup.boolean(),
        flagsNewBadges: Yup.boolean(),
        flagsRedirect: Yup.boolean(),
        flagsQuotaReached: Yup.boolean()
      })}
      onSubmit={(values, { setSubmitting }) => {
        alert(JSON.stringify(values, null, 2));
        setSubmitting(false);
      }}
    >
      {formik => (
      <Form className="dev-tools-test-path-form"
        onSubmit={formik.handleSubmit}
      >
        <Form.Group className="" controlId="testPathFormPathnum">
          <Form.Control name="pathnum" placeholder="Path number"
            {...formik.getFieldProps("pathnum")}
            className={formik.touched.pathnum && formik.errors.pathnum ? "error" : null}
          />
        </Form.Group>
        <ErrorMessage name="pathnum" />

        <Form.Group className="" controlId="testPathFormStepnum">
          <Form.Control name="stepnum" placeholder="Step number"
            {...formik.getFieldProps("stepnum")}
          />
        </Form.Group>
        <ErrorMessage name="stepnum" />

        <Form.Group className="" controlId="testPathFormLocation">
          <Form.Select name="location"
            aria-label="Dev tools path testing location"
            {...formik.getFieldProps("location")}
          >
            <option>Choose a specific location for the test</option>
            <option value="1">Οἰκος Σιμωνος</option>
            <option value="6">Ἀγορα (Πανδοκειον Ἀλεξανδρου)</option>
            <option value="11">Συναγωγη</option>
            <option value="7">Στοα</option>
            <option value="14">Γυμνασιον</option>
            <option value="13">Βαλανειον</option>
          </Form.Select>
        </Form.Group>
        <ErrorMessage name="location" />

        <Form.Group controlId="testPathFormFlags">
          <Form.Check name="flagsFreshUser" type="checkbox"
            label="fresh user record"
            {...formik.getFieldProps("flagsFreshUser")}
          />
          <Form.Check name="flagsViewLessons" type="checkbox"
            label="view lessons"
            {...formik.getFieldProps("flagsViewLessons")}
          />
          <Form.Check name="flagsNewBadges" type="checkbox"
            label="new badges"
            {...formik.getFieldProps("flagsNewBadges")}
          />
          <Form.Check name="flagsRedirect" type="checkbox"
            label="redirect"
            {...formik.getFieldProps("flagsRedirect")}
          />
          <Form.Check name="flagsQuotaReached" type="checkbox"
            label="quota reached"
            {...formik.getFieldProps("flagsQuotaReached")}
          />
        </Form.Group>

        <Button variant="primary" type="submit">Go</Button>
      </Form>
    )}
    </Formik>
  )
}

const DevPanel = (props) => {
  const [ visible, setVisible ] = useState(false);

  const handleShow = () => {
    setVisible(true);
  }

  const handleClose = () => {
    setVisible(false);
  }


  return(<>
    <Button variant="warning"
      className="dev-tools-button"
      onClick={handleShow}
    >
        <FontAwesomeIcon icon="hard-hat" size="lg" />
    </Button>
    <Offcanvas show={visible} onHide={handleClose}
      placement="start"
      className="dev-tools-component"
      {...props}
    >
      <Offcanvas.Header closeButton>
        <Offcanvas.Title>Dev tools</Offcanvas.Title>
      </Offcanvas.Header>
      <Offcanvas.Body>
        <h5>Test path</h5>
        <PathTestForm />

        <h5>Impersonate</h5>
      </Offcanvas.Body>
    </Offcanvas>
  </>)
}

export default DevPanel;