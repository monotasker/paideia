import React, { Component } from 'react';
import {
  Container,
} from "react-bootstrap";
import { LinkContainer } from "react-router-bootstrap";

import TypingGreekContent from "../Content/TypingGreek";
import HowItWorksContent from "../Content/HowItWorks";
import FaqContent from "../Content/Faq";
import KnownBugsContent from "../Content/KnownBugs";

class Info extends Component {
  constructor(props) {
    super(props);
    this.state = {
      currentPage: props.match.params.infoPage
    }
    this.goBack = this.goBack.bind(this);
  }

  goBack() {
    this.props.history.goBack();
  }

  render() {
    const content = {
      "faq": <FaqContent backFunc={this.goBack} />,
      "how-it-works": <HowItWorksContent backFunc={this.goBack} />,
      "typing-greek": <TypingGreekContent backFunc={this.goBack} />,
      "known-bugs": <KnownBugsContent backFunc={this.goBack} />
    }

    return(
      content[this.state.currentPage]
    )
  }
}

export default Info;
