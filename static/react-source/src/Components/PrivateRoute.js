import React from 'react';
import {
  Route, 
  Redirect
} from 'react-router-dom';
import { userContext } from '../UserContext/UserProvider';

const PrivateRoute = ({ component: Component, ...rest }) => {
  const { user, dispatch } = useContext(UserContext);
  return(
    <Route {...rest} render={(props) => (
      user.userLoggedIn === true
        ? <Component {...props} />
        : <Redirect to='/login' />
    )} />
  )
}