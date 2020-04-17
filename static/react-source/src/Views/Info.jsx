import React from 'react';
import {
  Row,
} from "react-bootstrap";
import {
  Switch,
  Route,
  useHistory
} from "react-router-dom";
import { CSSTransition } from "react-transition-group";

import TypingGreekContent from "../Content/TypingGreek";
import HowItWorksContent from "../Content/HowItWorks";
import FaqContent from "../Content/Faq";
import KnownBugsContent from "../Content/KnownBugs";

const Info = () => {
  let history = useHistory();


  const content = [
    { slug: "faq",
      component: <FaqContent backFunc={history.goBack} />
    },
    { slug: "how-it-works",
      component: <HowItWorksContent backFunc={history.goBack} />
    },
    { slug: "typing-greek",
      component: <TypingGreekContent backFunc={history.goBack} />
    },
    { slug: "known-bugs",
      component: <KnownBugsContent backFunc={history.goBack} />
    }
  ];

  return (
    <Row className="content-view info-component justify-content-sm-center">
      <Switch>
        {content.map(({ slug, component }) => (
          <Route key={slug} exact={true} path={`/info/${slug}`}>
            {( { match } ) => (
              <CSSTransition
                classNames="content-view"
                key={slug}
                in={match != null}
                appear={true}
                timeout={300}
                unmountOnExit
              >
                { component }
              </CSSTransition>
            )}
          </Route>
        ))}
      </Switch>
    </Row>
  );
}

export default Info;
