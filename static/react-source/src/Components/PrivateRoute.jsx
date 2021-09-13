import React, { useContext, useState, useEffect } from 'react';
import {
  Route,
  Redirect,
  useHistory,
  useLocation
} from 'react-router-dom';
import { UserContext } from '../UserContext/UserProvider';
import { urlBase } from '../variables';
import { checkLogin } from '../Services/authService';


const PrivateRoute = ({ ...options }) => {
  const { user, dispatch } = useContext(UserContext);
  const [ loggedIn, setLoggedIn ] = useState(user.userLoggedIn);
  let history = useHistory();
  const location = useLocation();

  useEffect(() => {
    if (!loggedIn) { history.push(`/${urlBase}/login`); }
  }, [loggedIn, user.userLoggedIn]);

  useEffect(() => {
    console.log('***********');
    console.log('Checking login in private route');
    setLoggedIn(checkLogin(user, dispatch));
  }, [history, location]);

  return(
    <Route {...options} />
  )
}

export default PrivateRoute;