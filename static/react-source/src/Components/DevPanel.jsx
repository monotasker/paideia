import React, { useState } from "react";
import {
  Button,
  Col,
  Form,
  Offcanvas,
  Row
} from "react-bootstrap";
import { useHistory } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Formik } from "formik";
import * as Yup from 'yup';
import { getPromptData } from "../Services/stepFetchService";
import { FormErrorMessage } from "../Services/formsService";
import { urlBase } from "../variables";

const PathTestForm = ({setStepData}) => {

  const history = useHistory();

  const assembleTestBlocks = (vals) => {
    const blockArray = {};
    const promotedObj = {
      cat2: vals.flagsPromotedTags2 ?
        vals.flagsPromotedTags2.split(',').map(Number) : [],
      cat3: vals.flagsPromotedTags3 ?
        vals.flagsPromotedTags3.split(',').map(Number) : [],
      cat4: vals.flagsPromotedTags4 ?
        vals.flagsPromotedTags4.split(',').map(Number) : []
    };
    if ( vals.flagsNewBadges === true ) {
      blockArray["new_tags"] = {
        new_tags: vals.flagsNewBadgesTags ?
          vals.flagsNewBadgesTags.split(',').map(Number) : [],
        promoted: promotedObj};
    }
    if ( vals.flagsPromoted === true ) {
      blockArray["promoted"] = {
        new_tags: vals.flagsNewBadgesTags ? vals.flagsNewBadgesTags.split(',') : [],
        promoted: promotedObj
        };
    }
    if ( vals.flagsQuotaReached === true ) {
      blockArray["quota_reached"] = {quota: vals.flagsQuotaReachedNum};
    }
    if ( vals.flagsRedirect === true ) {
      blockArray["redirect"] = {next_loc: vals.flagsRedirectLoc};
    }
    if ( vals.flagsViewLessons === true ) {
      blockArray["slides"] = {
        new_tags: vals.flagsViewLessonsTags ? vals.flagsViewLessonsTags.split(',').map(Number) : []
      };
    }
    return(blockArray);
  }

  return(
    <Formik
      initialValues={ {pathnum: "", stepnum: "", location: "",
                      flagsFreshUser: false,
                      flagsViewLessons: false, flagsViewLessonsTags: "",
                      flagsNewBadges: false, flagsNewBadgesTags: "",
                      flagsPromoted: false, flagsPromotedTags2: "",
                      flagsPromotedTags3: "", flagsPromotedTags4: "",
                      flagsRedirect: false, flagsRedirectLoc: "",
                      flagsQuotaReached: false, flagsQuotaReachedNum: ""}}
      validationSchema={Yup.object({
        pathnum: Yup.number().typeError("Must be a number").positive("Must be a positive number").integer("Must be an integer"),
        stepnum: Yup.number().typeError("Must be a number").positive("Must be a positive number"),
        flagsFreshUser: Yup.boolean(),
        flagsViewLessons: Yup.boolean(),
        flagsViewLessonsTags: Yup.string().matches(/^(\d+,\s?)*(\d+)$/,
          {message: "Must be comma separated list of numbers"}),
        flagsNewBadges: Yup.boolean(),
        flagsNewBadgesTags: Yup.string().matches(/^(\d+,\s?)*(\d+)$/,
          {message: "Must be comma separated list of numbers"}),
        flagsPromoted: Yup.boolean(),
        flagsPromotedTags2: Yup.string().matches(/^(\d+,\s?)*(\d+)$/,
          {message: "Must be comma separated list of numbers"}),
        flagsPromotedTags3: Yup.string().matches(/^(\d+,\s?)*(\d+)$/,
          {message: "Must be comma separated list of numbers"}),
        flagsPromotedTags4: Yup.string().matches(/^(\d+,\s?)*(\d+)$/,
          {message: "Must be comma separated list of numbers"}),
        flagsRedirect: Yup.boolean(),
        flagsQuotaReached: Yup.boolean(),
        flagsQuotaReachedNum: Yup.number().typeError("Must be a number").positive("Must be a positive number")
      })}
      onSubmit={(values, { setSubmitting }) => {
        const payload = {testing: true,
                         path: !isNaN(parseInt(values.pathnum)) ? parseInt(values.pathnum) : null,
                         step: !isNaN(parseInt(values.stepnum)) ? parseInt(values.stepnum) : null,
                         new_user: values.flagsFreshUser,
                         location: values.location,
                         set_blocks: assembleTestBlocks(values)}
        console.log(payload);
        const myStepData = getPromptData(payload).then(mydata => {
          setStepData(mydata);
          history.push(`/${urlBase}/walk/${values.location}/${values.stepnum}`);
          setSubmitting(false);
        });
      }}
    >
      {formik => (
      <Form className="dev-tools-test-path-form"
        onSubmit={formik.handleSubmit}
      >
        <Row>
          <Col>
            <Form.Control name="pathnum" placeholder="Path number"
              {...formik.getFieldProps("pathnum")}
              className={formik.touched.pathnum && formik.errors.pathnum ? "error" : null}
            />
            <FormErrorMessage component="span" name="pathnum" />
          </Col>
          <Col>
            <Form.Control name="stepnum" placeholder="Step number"
              {...formik.getFieldProps("stepnum")}
            />
            <FormErrorMessage component="span" name="stepnum" />
          </Col>
        </Row>

        <Row>
          <Col>
            <Form.Group className="" controlId="testPathFormLocation">
              <Form.Select name="location"
                aria-label="Dev tools path testing location"
                {...formik.getFieldProps("location")}
              >
                <option>Choose a specific location for the test</option>
                <option value="domus_A">Οἰκος Σιμωνος</option>
                <option value="agora">Ἀγορα (Πανδοκειον Ἀλεξανδρου)</option>
                <option value="synagogue">Συναγωγη</option>
                <option value="ne_stoa">Στοα</option>
                <option value="gymnasion">Γυμνασιον</option>
                <option value="bath">Βαλανειον</option>
              </Form.Select>
            </Form.Group>
            <FormErrorMessage component="span" name="location" />
          </Col>
        </Row>

        <Row className="encapsulated">
          <Col>
            <Form.Check name="flagsFreshUser" type="checkbox"
              label="force a fresh user record"
              {...formik.getFieldProps("flagsFreshUser")}
            />
          </Col>
        </Row>

        <Row className="encapsulated">
          <Col>
            <Form.Check name="flagsViewLessons" type="checkbox"
              label="view lessons for these tags"
              {...formik.getFieldProps("flagsViewLessons")}
            />
            <Form.Control name="flagsViewLessonsTags"
              placeholder="tags for the lessons to be viewed"
              {...formik.getFieldProps("flagsViewLessonsTags")}
              />
            <FormErrorMessage component="span" name="flagsViewLessonsTags" />
          </Col>
        </Row>

        <Row className="encapsulated">
          <Col>
            <Form.Check name="flagsNewBadges" type="checkbox"
              label="new badges to begin"
              {...formik.getFieldProps("flagsNewBadges")}
            />
            <Form.Control name="flagsNewBadgesTags"
              placeholder="the new badges to be begun"
              {...formik.getFieldProps("flagsNewBadgesTags")}
              />
            <FormErrorMessage component="span" name="flagsNewBadgesTags" />
          </Col>
        </Row>

        <Row className="encapsulated">
          <Col>
            <Form.Check xs={12} name="flagsPromoted" type="checkbox"
              label="newly promoted badges"
              {...formik.getFieldProps("flagsPromoted")}
            />
            <Form.Control xs={12} name="flagsPromotedTags2"
              placeholder="the badges newly promoted to level 2"
              {...formik.getFieldProps("flagsPromotedTags2")}
              />
            <FormErrorMessage component="span" name="flagsPromotedTags2" />
            <Form.Control xs={12} name="flagsPromotedTags3"
              placeholder="the badges newly promoted to level 3"
              {...formik.getFieldProps("flagsPromotedTags3")}
              />
            <FormErrorMessage component="span" name="flagsPromotedTags3" />
            <Form.Control xs={12} name="flagsPromotedTags4"
              placeholder="the badges newly promoted to level 4"
              {...formik.getFieldProps("flagsPromotedTags4")}
              />
            <FormErrorMessage component="span" name="flagsPromotedTags4" />
          </Col>
        </Row>

        <Row className="encapsulated">
          <Form.Group as={Col}>
            <Form.Check name="flagsRedirect" type="checkbox"
              label="redirect to a location"
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
        </Row>

        <Row className="encapsulated">
          <Form.Group as={Col}>
            <Form.Check name="flagsQuotaReached" type="checkbox"
              label="quota reached"
              {...formik.getFieldProps("flagsQuotaReached")}
            />
            <Form.Control name="flagsQuotaReachedNum"
              placeholder="number of paths for quota"
              {...formik.getFieldProps("flagsQuotaReachedNum")}
              />
            <FormErrorMessage component="span" name="flagsQuotaReachedNum" />
          </Form.Group>
        </Row>

        <Button variant="primary" type="submit">Go</Button>
      </Form>
    )}
    </Formik>
  )
}

const DevPanel = ({setStepData, ...props}) => {
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
        <Offcanvas.Title><h2>Dev Tools</h2></Offcanvas.Title>
      </Offcanvas.Header>
      <Offcanvas.Body>
        <h3>Test path</h3>
        <PathTestForm setStepData={setStepData} />

        <h3>Impersonate</h3>
      </Offcanvas.Body>
    </Offcanvas>
  </>)
}

export default DevPanel;