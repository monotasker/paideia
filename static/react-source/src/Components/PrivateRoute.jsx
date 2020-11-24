import React, { useContext, useState, useEffect } from 'react';
import {
  Route,
  Redirect,
  useHistory
} from 'react-router-dom';
import { UserContext } from '../UserContext/UserProvider';
import { urlBase } from '../variables';
import { checkLogin } from '../Services/authService';


const PrivateRoute = ({ ...options }) => {
  const { user, dispatch } = useContext(UserContext);
  const [ loggedIn, setLoggedIn ] = useState(user.userLoggedIn);
  let history = useHistory();

  useEffect(() => {
    if (!loggedIn) { history.push(`/${urlBase}/login`); }
  }, [loggedIn, user.userLoggedIn]);

  useEffect(() => {
    setLoggedIn(checkLogin(user, dispatch));
  });

  return(
    <Route {...options} />
  )
}

export default PrivateRoute;