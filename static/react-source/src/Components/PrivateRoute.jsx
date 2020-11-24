import React, { useContext, useState } from 'react';
import {
  Route,
  Redirect
} from 'react-router-dom';
import { UserContext } from '../UserContext/UserProvider';
import { checkLogin } from '../Services/authService';

const PrivateRoute = ({ component: Component, ...rest }) => {
  const { user, dispatch } = useContext(UserContext);
  const [ loggedIn, setLoggedIn ] = useState(checkLogin(user, dispatch));

  return(
    <Route {...rest} render={(props) => (
      loggedIn === true
        ? <Component {...props} />
        : <Redirect to='/login' />
    )} />
  )
}

export default PrivateRoute;