import React from 'react';
import {
  useHistory
} from "react-router-dom";

import Endpoint from "../Components/Endpoint";
import InstructorDashboard from "../Views/InstructorDashboard";
import { urlBase } from "../variables";

const Instructors = () => {
  let history = useHistory();

  const branches = [
    { slug: "dashboard",
      component: <InstructorDashboard backFunc={history.goBack} />
    }
  ];

  return (
    <Endpoint path={`/${urlBase}/instructors/`} branches={branches} />
  );
}

export default Instructors;
