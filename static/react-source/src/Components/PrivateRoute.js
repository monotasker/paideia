import React, { Component } from 'react';
import {
  Route, 
  Redirect
} from 'react-router-dom';
import { userContext } from '../Contexts'

const PrivateRoute = ({ component: Component, ...rest }) => (
  <Route {...rest} render={(props) => (
    fakeAuth.isAuthenticated === true
      ? <Component {...props} />
      : <Redirect to='/login' />
  )} />
)