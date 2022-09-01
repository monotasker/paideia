import React, { useState } from "react";
import {
  Button,
  Form,
  Offcanvas
} from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

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
        <Form className="dev-tools-test-path-form">
          <Form.Group className="" controlId="testPathFormPathnum">
            <Form.Control placeholder="Path number"></Form.Control>
          </Form.Group>
          <Form.Group className="" controlId="testPathFormStepnum">
            <Form.Control placeholder="Step number"></Form.Control>
          </Form.Group>
          <Form.Group className="" controlId="testPathLocation">
            <Form.Select aria-label="Dev tools path testing location">
              <option>Choose a specific location for the test</option>
              <option value="1">Οἰκος Σιμωνος</option>
              <option value="6">Ἀγορα (Πανδοκειον Ἀλεξανδρου)</option>
              <option value="11">Συναγωγη</option>
              <option value="7">Στοα</option>
              <option value="14">Γυμνασιον</option>
              <option value="13">Βαλανειον</option>
            </Form.Select>
          </Form.Group>
          <Form.Group controlId="test-path-form-flags">
            <Form.Check type="checkbox" label="fresh user record" />
            <Form.Check type="checkbox" label="view lessons" />
            <Form.Check type="checkbox" label="new badges" />
          </Form.Group>
          <Button variant="primary" type="submit">Go</Button>
        </Form>
        <h5>Impersonate</h5>
      </Offcanvas.Body>
    </Offcanvas>
  </>)
}

export default DevPanel;