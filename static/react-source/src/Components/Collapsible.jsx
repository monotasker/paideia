import React, { Component } from "react";
import {
  Collapse,
  Card
} from "react-bootstrap";

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faPlus,
  faMinus,
  faNetworkWired
} from '@fortawesome/free-solid-svg-icons';

class Collapsible extends Component {
  constructor(props, context) {
    super(props, context);

    this.state = {
      open: this.props.open,
    };
  }

  static defaultProps = {
    linkText: null,
    linkElement: "h3",
    open: false
  }

  render() {
    const { open } = this.state;
    const Tag = this.props.linkElement;
    return(
      <Card className={this.props.styleName}>
        <Card.Body>
          <a onClick={() => this.setState({open: !open})}
            aria-controls="collapse-pane"
            aria-expanded={open}
          >
            <Tag>
              {!!this.props.linkIcon &&
                <FontAwesomeIcon icon={this.props.linkIcon} fixedWidth />
              }
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
