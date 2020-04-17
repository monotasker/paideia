import React from 'react';
import {
  useHistory
} from "react-router-dom";

import Endpoint from "../Components/Endpoint";
import TypingGreekContent from "../Content/TypingGreek";
import HowItWorksContent from "../Content/HowItWorks";
import FaqContent from "../Content/Faq";
import KnownBugsContent from "../Content/KnownBugs";

const Info = () => {
  let history = useHistory();

  const branches = [
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
    <Endpoint path="/info/" branches={branches} />
  );
}

export default Info;
