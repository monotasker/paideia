import React, { useState } from "react";
import {
  Button,
  Form,
  Offcanvas
} from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { ErrorMessage, Formik } from "formik";
import * as Yup from 'yup';
import { getPromptData } from "../Services/stepFetchService";

const PathTestForm = () => {

  const assembleTestBlocks = (vals) => {
    const blockArray = {};
    const promotedObj = {
      cat2: vals.flagsPromotedTags2 ? vals.flagsPromotedTags2.split(',') : [],
      cat3: vals.flagsPromotedTags3 ? vals.flagsPromotedTags3.split(',') : [],
      cat4: vals.flagsPromotedTags4 ? vals.flagsPromotedTags4.split(',') : []
    }
    if ( vals.flagsNewBadges === true ) {
      blockArray["new_tags"] = {new_tags: vals.flagsNewBadgesTags ? vals.flagsNewBadgesTags.split(',') : [],
                                promoted: promotedObj}
    }
    if ( vals.flagsPromoted === true ) {
      blockArray["promoted"] = {
        new_tags: vals.flagsNewBadgesTags ? vals.flagsNewBadgesTags.split(',') : [],
        promoted: promotedObj
        }
    }
    if ( vals.flagsQuotaReached === true ) {
      blockArray["quota_reached"] = {quota: vals.flagsQuotaReachedNum}
    }
    if ( vals.flagsRedirect === true ) {
      blockArray["redirect"] = {next_loc: vals.flagsRedirectLoc};
    }
    if ( vals.flagsViewLessons === true ) {
      blockArray["slides"] = {new_tags: vals.flagsViewLessonsTags}
    }
    return(blockArray);
  }

  return(
    <Formik
      initialValues={ {pathnum: "", stepnum: "", location: "",
                      flagsFreshUser: false,
                      flagsViewLessons: false, flagsViewLessonsTags: "",
                      flagsNewBadges: false, flagsNewBadgesTags: "",
                      flagsPromoted: false, flagsPromotedTags: "",
                      flagsRedirect: false, flagsRedirectLoc: "",
                      flagsQuotaReached: false}}
      validationSchema={Yup.object({
        pathnum: Yup.number().positive().integer("Must be a number"),
        stepnum: Yup.number("Must be a number"),
        flagsFreshUser: Yup.boolean(),
        flagsViewLessons: Yup.boolean(),
        flagsNewBadges: Yup.boolean(),
        flagsNewBadgesTags: Yup.string(),
        flagsPromoted: Yup.boolean(),
        flagsPromotedTags: Yup.string(),
        flagsRedirect: Yup.boolean(),
        flagsQuotaReached: Yup.boolean()
      })}
      onSubmit={(values, { setSubmitting }) => {
        const payload = {testing: true,
                         path: values.pathnum,
                         step: values.stepnum,
                         new_user: values.flagsFreshUser,
                         set_blocks: assembleTestBlocks(values)}
        console.log(payload);
        // getPromptData(payload);
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

        <Form.Group controlId="flagsFreshUser">
          <Form.Check name="flagsFreshUser" type="checkbox"
            label="fresh user record"
            {...formik.getFieldProps("flagsFreshUser")}
          />
        </Form.Group>

        <Form.Group contolId="flagsViewLessons">
          <Form.Check name="flagsViewLessons" type="checkbox"
            label="view lessons"
            {...formik.getFieldProps("flagsViewLessons")}
          />
          <Form.Control name="flagsViewLessonsTags"
            placeholder="tags for the lessons to be viewed"
            {...formik.getFieldProps("flagsViewLessonsTags")}
            />
        </Form.Group>

        <Form.Group>
          <Form.Check name="flagsNewBadges" type="checkbox"
            label="new badges"
            {...formik.getFieldProps("flagsNewBadges")}
          />
          <Form.Control name="flagsNewBadgesTags"
            placeholder="the new badges to be begun"
            {...formik.getFieldProps("flagsNewBadgesTags")}
            />
        </Form.Group>

        <Form.Group>
          <Form.Check name="flagsPromoted" type="checkbox"
            label="promoted"
            {...formik.getFieldProps("flagsPromoted")}
          />
          <Form.Control name="flagsPromotedTags2"
            placeholder="the badges newly promoted to level 2"
            {...formik.getFieldProps("flagsPromotedTags2")}
            />
          <Form.Control name="flagsPromotedTags3"
            placeholder="the badges newly promoted to level 3"
            {...formik.getFieldProps("flagsPromotedTags3")}
            />
          <Form.Control name="flagsPromotedTags4"
            placeholder="the badges newly promoted to level 4"
            {...formik.getFieldProps("flagsPromotedTags4")}
            />
        </Form.Group>

        <Form.Group>
          <Form.Check name="flagsRedirect" type="checkbox"
            label="redirect"
            {...formik.getFieldProps("flagsRedirect")}
          />
          <Form.Select name="flagsRedirectLoc"
            aria-label="location to which redirect is aimed"
            {...formik.getFieldProps("flagsRedirectLoc")}
          >
            <option>Choose a specific destination for the redirect</option>
            <option value="1">Οἰκος Σιμωνος</option>
            <option value="6">Ἀγορα (Πανδοκειον Ἀλεξανδρου)</option>
            <option value="11">Συναγωγη</option>
            <option value="7">Στοα</option>
            <option value="14">Γυμνασιον</option>
            <option value="13">Βαλανειον</option>
          </Form.Select>
        </Form.Group>

        <Form.Group>
          <Form.Check name="flagsQuotaReached" type="checkbox"
            label="quota reached"
            {...formik.getFieldProps("flagsQuotaReached")}
          />
          <Form.Control name="flagsQuotaReachedNum"
            placeholder="arguments for the new badges to be begun"
            {...formik.getFieldProps("flagsQuotaReachedNum")}
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