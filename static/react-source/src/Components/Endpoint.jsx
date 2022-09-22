
import React from 'react';
import {
  Row,
} from "react-bootstrap";
import {
  Switch,
  Route,
} from "react-router-dom";
import { CSSTransition } from "react-transition-group";
import { DEBUGGING } from '../variables';

const Endpoint = ({path, branches}) => {

  // console.log(path);
  // console.log(branches);


  return(
    <Row className="content-view info-component justify-content-sm-center">
    <Switch>
      {branches.map(({ slug, component }) => (
      <Route key={slug} exact={true} path={`${path}${slug}`}>
        {( { match } ) => (
        <CSSTransition
          classNames="content-page-component"
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
  )
}

export default Endpoint;