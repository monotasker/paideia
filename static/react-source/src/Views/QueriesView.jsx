import React, { useContext, useState, useEffect } from "react";
import {
    Row,
    Col,
    Table,
    Button,
    Spinner,
    Badge
} from "react-bootstrap";
import { SwitchTransition, CSSTransition } from "react-transition-group";

import { UserContext } from "../UserContext/UserProvider";
import { getStepQueries } from "../Services/stepFetchService";
import { submitNewQuery } from "../Services/stepFetchService";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

const QueriesView = () => {

    const {user, dispatch} = useContext(UserContext);
    const [queries, setQueries] = useState(null);
    const [userQueries, setUserQueries] = useState(null);
    const [classQueries, setClassQueries] = useState(null);
    const [otherQueries, setOtherQueries] = useState(null);
    const [viewScope, setViewScope] = useState('public');

    const fetchAction = () => {
        getStepQueries({step_id: user.currentStep,
                        user_id: user.userId})
        .then(queryfetch => {
          queryfetch.json().then((mydata) => {
            console.log(mydata);
            setQueries(mydata);
            setUserQueries(mydata.user_queries);
            setClassQueries(mydata.class_queries);
            setOtherQueries(mydata.other_queries.slice(0, 20));
          })
        });
    }

    useEffect(() => fetchAction(), [user.currentStep]);

    const newQueryAction = () => (
      submitNewQuery({step_id=null,
                      path_id=null,
                      user_id=null,
                      loc_id=null,
                      answer="",
                      log_id=null,
                      score=null,
                      user_comment=null})
      .then(myresponse => {

      })
    );

    const LoadingContent = () => (
      <Spinner animation="grow" variant="secondary"
        className="align-self-center map-spinner" />
    );

    const DisplayRow = (props) => (
      <tr key={props.q.bugs.id}>
        <td key={`${props.q.bugs.id}_cell`}>
          <p className="query-display-op">
            <FontAwesomeIcon icon="user-circle" size="3x" /><br />
            <span className="query-display-op-name">
              {`${props.q.auth_user.first_name} ${props.q.auth_user.last_name}`}
            </span><br />
            <span className="query-display-op-date">
              {props.q.bugs.date_submitted}
            </span><br />
            <span className="query-display-op-status">
              {props.q.bugs.bug_status}
            </span>
          </p>
          <p className="query-display-response">
            {props.q.bugs.user_response}
          </p>
          <p className="query-display-op-question">
            {props.q.bugs.user_comment}
          </p>

          <p className="query-display-admin">
            <FontAwesomeIcon icon="user-circle" size="3x" /><br />
            <span className="query-display-admin-name">
              {"Instructor"}
            </span><br />
            <span className="query-display-admin-date">
              {"mydate"}
            </span>
          </p>
          <p className="query-display-admin-comment">
            {props.q.bugs.admin_comment}
          </p>
        </td>
      </tr>
    );

    const DisplayTable = (props) => (
      props.queries != [] && !!props.queries[0] && !!props.queries[0].bugs) ?
      (
        <Table><tbody>
          {console.log("query")}
          {console.log(props.queries[0])}
          {props.queries.map(q => <DisplayRow q={q} key={q.bugs.id} />)}
        </tbody></Table>
      ) : (
        <Table><tbody>
          {props.queries != [] && props.queries.map(myclass =>
            <tr
              key={`${myclass.institution}_${myclass.year}_${myclass.section}`}
            >
              <td>
                <span className="query-display-class-header">{`${myclass.institution}, ${myclass.year}, ${myclass.section}`}</span>
                <Table><tbody>
                  {myclass && myclass.queries.map(q => {
                    if (q.bugs) { return(<DisplayRow q={q} key={q.bugs.id} />)}
                  })}
                </tbody></Table>
              </td>
            </tr>
          )}
        </tbody></Table>
    );

    const myScopes = [
      {scope: 'user',
       list: userQueries},
      {scope: 'class',
       list: classQueries},
      {scope: 'public',
       list: otherQueries}
    ];

    const DisplayContent = () => (
      <React.Fragment>
        <Button
          className={`queries-view-changer ${viewScope == 'user' ? "in" : "out"}`}
          variant="outline-secondary"
          onClick={() => setViewScope('user')}
        >
          <FontAwesomeIcon icon="user" />Me
          <Badge variant="success">{userQueries ? userQueries.length : "0"}</Badge>
        </Button>
        <Button
          className={`queries-view-changer ${viewScope == 'class' ? "in" : "out"}`}
          variant="outline-secondary"
          onClick={() => setViewScope('class')}
        >
          <FontAwesomeIcon icon="users" />My Classmates
          <Badge variant="success">{classQueries ? classQueries.reduce((sum, current) => sum + current.queries.length, 0) : "0"}</Badge>
        </Button>
        <Button
          className={`queries-view-changer ${viewScope == 'public' ? "in" : "out"}`}
          variant="outline-secondary"
          onClick={() => setViewScope('public')}
        >
          <FontAwesomeIcon icon="globe-americas" />Other Learners
          <Badge variant="success">{otherQueries ? otherQueries.length : "0"}</Badge>
        </Button>

        {myScopes.map(({scope, list}) =>
          <CSSTransition
            key={scope}
            timeout={250}
            in={scope === viewScope}
            classNames="queries-view-pane"
            appear={true}
            unmountOnExit={true}
          >
            <div className="queries-view-pane">
              <DisplayTable queries={list} />
            </div>
          </CSSTransition>
        )}

        {/* { ( !userQueries || userQueries == [] ) ? (
          "You haven\'t asked any questions yet about this step."
        ) : (
          <Table>
          </Table>
        )}

        { ( !classQueries || classQueries == {} ) ? (
          "You haven\'t asked any questions yet about this step."
        ) : (
          <Table>
          </Table>
        )}

        { ( !otherQueries || otherQueries == [] ) ? (
          "No one else has asked a question about this step. Why not be the first?"
        ) : (
        )} */}
    </React.Fragment>
    );

    return(
      <Row key="QueriesView" className="queriesview-component panel-view">
        <Col>
          <h2>Questions about This Step</h2>
          <div>
            <SwitchTransition>
              <CSSTransition
                key={!!queries ? "loaded" : "loading"}
                timeout={250}
                unmountOnExit
                mountOnEnter
              >
                { !queries ? <LoadingContent /> : <DisplayContent /> }
              </CSSTransition>
            </SwitchTransition>
          </div>
        </Col>
      </Row>
    )
}

export default QueriesView;