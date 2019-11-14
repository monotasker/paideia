import React, {
  Component,
  useState
} from 'react';
import {
  Container,
} from "react-bootstrap";
import { LinkContainer } from "react-router-bootstrap";
import { withRouter } from "react-router";
import {
  Switch,
  Route,
  BrowserRouter,
  useParams,
  useHistory
} from "react-router-dom";

import TypingGreekContent from "../Content/TypingGreek";
import HowItWorksContent from "../Content/HowItWorks";
import FaqContent from "../Content/Faq";
import KnownBugsContent from "../Content/KnownBugs";

function goBack() {
  history.goBack();
}

function Info() {
  let { infoPage } = useParams();

  let history = useHistory();
  console.log(history);

  const content = {
    "faq": <FaqContent backFunc={history.goBack} />,
    "how-it-works": <HowItWorksContent backFunc={history.goBack} />,
    "typing-greek": <TypingGreekContent backFunc={history.goBack} />,
    "known-bugs": <KnownBugsContent backFunc={history.goBack} />
  }

  console.log(infoPage);

  return(
    <div className="info-component">
      { content[infoPage] }
    </div>
  )
}

export default withRouter(Info);
