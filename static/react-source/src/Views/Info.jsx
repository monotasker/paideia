import React from 'react';
import {
  useHistory
} from "react-router-dom";

import Endpoint from "../Components/Endpoint";
import TypingGreekContent from "../Content/TypingGreek";
import HowItWorksContent from "../Content/HowItWorks";
import FaqContent from "../Content/Faq";
import KnownBugsContent from "../Content/KnownBugs";
import PrivacyPolicy from '../Content/PrivacyPolicy';
import { urlBase } from "../variables";

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
    },
    { slug: "privacy-policy",
      component: <PrivacyPolicy backFunc={history.goBack} />
    }
  ];

  return (
    <Endpoint path={`/${urlBase}/info/`} branches={branches} />
  );
}

export default Info;
