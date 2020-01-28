import React, { Component } from "react";
import {
  Collapse,
  Card
} from "react-bootstrap";

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faPlus,
  faMinus
} from '@fortawesome/free-solid-svg-icons';

class Collapsible extends Component {
  constructor(props, context) {
    super(props, context);

    this.state = {
      open: false,
    };
  }

  static defaultProps = {
    linkText: null,
    linkElement: "h3"
  }

  render() {
    const { open } = this.state;
    const Tag = this.props.linkElement;
    return(
      <Card>
        <Card.Body>
          <a onClick={() => this.setState({open: !open})}
            aria-controls="collapse-pane"
            aria-expanded={open}
          >
            <Tag>
              {this.props.linkText}
              <FontAwesomeIcon icon={open ? faMinus : faPlus} pull="right" />
            </Tag>
          </a>
          <Collapse in={this.state.open}>
            <div id="switching-pane">
              {this.props.children}
            </div>
          </Collapse>
        </Card.Body>
      </Card>
    )
  }
}

export default Collapsible;
