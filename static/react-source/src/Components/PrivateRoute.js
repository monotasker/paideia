import React from 'react';
import {
  Route, 
  Redirect
} from 'react-router-dom';
import { userContext } from '../UserContext/UserProvidera';

const PrivateRoute = ({ component: Component, ...rest }) => (
  <Route {...rest} render={(props) => (
    fakeAuth.isAuthenticated === true
      ? <Component {...props} />
      : <Redirect to='/login' />
  )} />
)