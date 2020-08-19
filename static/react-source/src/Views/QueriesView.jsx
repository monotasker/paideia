import React, { useContext, useState, useEffect } from "react";
import {
    Badge,
    Button,
    Col,
    Collapse,
    Form,
    Row,
    Spinner,
    Table,
} from "react-bootstrap";
import { SwitchTransition, CSSTransition } from "react-transition-group";
import marked from "marked";
import DOMPurify from 'dompurify';
import TextareaAutosize from 'react-textarea-autosize';

import { UserContext } from "../UserContext/UserProvider";
import { getStepQueries,
         submitNewQuery,
         addQueryPost,
         updateQueryPost,
         addQueryComment,
         updateQueryComment
 } from "../Services/stepFetchService";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { findIndex } from "core-js/es/array";
import { readableDateAndTime } from "../Services/dateTimeService";

const NewQueryForm = ({answer, score, action}) => {
  const [queryText, setQueryText] = useState(" ");
  const [showPublic, setShowPublic] = useState(true);
  return (
    <Form onSubmit={() => action(queryText, showPublic)}>
      <Form.Group controlId="newQueryFormAnswer">
        {!!answer && answer !== "null" ? <React.Fragment>
          <Form.Label>You said</Form.Label>
          <p>{answer}</p>
          <Form.Label>Awarded</Form.Label>
          <span>{score}</span>
          </React.Fragment>
        :
          <Form.Label>You haven't answered this question yet</Form.Label>
        }
      </Form.Group>
      <Form.Group controlId="newQueryFormTextarea">
        <Form.Label>Your question or comment</Form.Label>
        <Form.Control as="textarea" rows="3"
          defaultValue={queryText}
          onChange={e => setQueryText(e.target.value)}
        />
      </Form.Group>

      <Form.Group controlId={`addQueryPrivateCheckbox`}>
        <Form.Check type="checkbox" label="Keep this question or comment private."
          defaultValue={!showPublic}
          onChange={e => setShowPublic(!e.target.value)}
          />
      </Form.Group>
      <Button variant="primary" type="submit"
      >Submit my query</Button>
    </Form>
  );
}

const PostRow = ({queryId, postId, posterId, postText, posterNameFirst,
                  posterNameLast, postDate, postEditedDate, posterRole, hidden,
                  deleted, flagged, showPublic,
                  updatePostAction, newCommentAction, updateCommentAction,
                  classId
                }) => {
  const {user, dispatch} = useContext(UserContext);
  const [ showAdder, setShowAdder ] = useState(false);
  const [ editing, setEditing ] = useState(false);
  const showEditingForm = (e) => {
    e.preventDefault();
    setEditing(true);
  }
  const myRoles = !!posterRole ? posterRole.map(r => `${r}`).join(" ") : "";
  console.log(postId);
  return (
    <li key={`${classId}_${queryId}_${postId}`}>
      <div className={`post-display-info ${myRoles}`}>
        <FontAwesomeIcon icon="user-circle" size="3x" /><br />
        <span className={`post-display-name ${myRoles}`}>
          {`${posterNameFirst} ${posterNameLast}`}
        </span><br />
        {posterRole.map(r =>
          <React.Fragment key={r}>
            <span className={`post-display-role ${r}`}>{r}</span><br />
          </React.Fragment>
        )}
        <span className={`post-display-date`}>
          {readableDateAndTime(postDate)}
        </span>
        {!!postEditedDate &&
          <span className={`post-display-edited-date`}>
            last edited {readableDateAndTime(postEditedDate)}
          </span>
        }
      </div>
      <div className={`post-display-body ${myRoles}`}>
        {!!editing ?
          <UpdatePostForm postId={postId}
            queryId={queryId}
            updatePostAction={updatePostAction}
            currentText={postText ? DOMPurify.sanitize(postText) : ""}
            setEditing={setEditing}
          />
          :
          <div
            dangerouslySetInnerHTML={{
              __html: postText ? DOMPurify.sanitize(marked(postText)) : ""}}
          />
        }
        <div className="control-row">
          <span className="comment-button-container">
            <Button variant="outline-secondary"
              onClick={() => setShowAdder(!showAdder)}
              aria-controls="add-comment-form-wrapper"
              aria-expanded={showAdder}
            >
              <FontAwesomeIcon icon="comment" />
              Add a comment
            </Button>
          </span>
          {user.userId === posterId &&
            <Button variant="outline-secondary"
              onClick={e => showEditingForm(e)}
            >
              <FontAwesomeIcon icon="pencil-alt" />
            </Button>
          }
          {user.userId === posterId &&
            <Button variant="outline-secondary">
              <FontAwesomeIcon icon="trash-alt" />
            </Button>
          }
          {user.userId !== posterId &&
            <Button variant="outline-secondary">
              <FontAwesomeIcon icon="thumbs-up" />
            </Button>
          }
          {(user.userRoles.includes("administrators") || user.userRoles.includes("instructors") && user.instructing.find(c => c.id == classId)) &&
            <Button variant="outline-secondary">
              <FontAwesomeIcon icon="thumbtack" />
            </Button>
          }
          {(user.userRoles.includes("administrators") || user.userRoles.includes("instructors")) &&
            <Button variant="outline-secondary">
              <FontAwesomeIcon icon="lightbulb" />
            </Button>
          }
        </div>
        <Collapse in={showAdder}>
          <div className="add-comment-form-wrapper">
            <AddCommentForm className="add-comment-form"
              queryId={queryId}
              postId={postId}
              newCommentAction={newCommentAction}
            />
          </div>
        </Collapse>
      </div>
    </li>
  )
}

const AddCommentForm = ({queryId, postId, newCommentAction}) => {
  const [commentText, setCommentText] = useState("");
  const [isPrivate, setIsPrivate] = useState(false);
  return (
    <Form id={`add-comment-form-${queryId}-${postId}`}
       className="add-comment-form"
    >
        <Form.Group controlId={`addCommentPrivateCheckbox-${queryId}-${postId}`}
        >
          <Form.Check type="checkbox" label="Keep my comment private."
            defaultValue={isPrivate}
            onChange={e => setIsPrivate(e.target.value)}
            />
        </Form.Group>
        <Form.Group controlId={`addCommentTextarea-${queryId}-${postId}`}>
          <Form.Control as="textarea"
            onChange={e => setCommentText(e.target.value)}
          />
        </Form.Group>
        <Button variant="primary"
          type="submit"
          onClick={e => newCommentAction(postId, commentText, !isPrivate, e)}
        >Submit comment</Button>
    </Form>
  )
}

const UpdatePostForm = ({postId, queryId, updatePostAction, currentText,
                         setEditing}) => {
  const [postText, setPostText] = useState("");
  const sendUpdate = e => {
    updatePostAction({postId: postId, queryId: queryId,
                      postText: postText, event: e});
    setEditing(false);
  }
  return (
    <Form id={`update-post-form-${postId}`} className="update-post-form">
        <Form.Group controlId={`updatePostTextarea-${postId}`}>
          <TextareaAutosize
            defaultValue={currentText}
            onChange={e => setPostText(e.target.value)}
          />
        </Form.Group>
        <Button variant="primary"
          type="submit"
          onClick={e => sendUpdate(e)}
        >Update</Button>
    </Form>
  )
}

const AddPostForm = ({queryId, newPostAction}) => {
  const [postText, setPostText] = useState("");
  const [isPrivate, setIsPrivate] = useState(false);
  return (
    <Form id={`add-post-form-${queryId}`} className="add-post-form">
        <Form.Group controlId={`addPostPrivateCheckbox-${queryId}`}>
          <Form.Check type="checkbox" label="Keep my answer private."
            defaultValue={isPrivate}
            onChange={e => setIsPrivate(e.target.value)}
            />
        </Form.Group>
        <Form.Group controlId={`addPostTextarea-${queryId}`}>
          <Form.Control as="textarea" onChange={e => setPostText(e.target.value)} />
        </Form.Group>
        <Button variant="primary"
          type="submit"
          onClick={e => newPostAction(queryId, postText, !isPrivate, e)}
        >Submit reply</Button>
    </Form>
  )
}

const DisplayRow = ({newPostAction, newCommentAction, updatePostAction,
                     updateCommentAction, classId, queryId, opNameFirst,
                     opNameLast, posts, dateSubmitted, queryStatus, opResponse,
                     opQueryText, hidden, showPublic, flagged, deleted,
                     queryStep, queryPath
                    }) => {
  const [ showAdder, setShowAdder ] = useState(false);

  return (
      <tr key={queryId}>
        <td key={`${queryId}_cell`}>
          <p className="query-display-op">
            <span className="query-display-op-name">
              {`${opNameFirst} ${opNameLast}`}
            </span> answered...<br />
            <FontAwesomeIcon icon="user-circle" size="3x" /><br />
            <span className="query-display-op-date">
              {readableDateAndTime(dateSubmitted)}
            </span><br />
            <span className="query-display-op-status">{queryStatus}</span>
          </p>
          <p className="query-display-response"
            dangerouslySetInnerHTML={{
              __html: opResponse ? DOMPurify.sanitize(marked(opResponse)) : ""
            }} />
          <p className="query-display-op-question"
            dangerouslySetInnerHTML={{
              __html: opQueryText ? DOMPurify.sanitize(marked(opQueryText)) : ""
            }} />
          <ul className="query-display-replies">
          {!!posts && posts.map(p =>
            <PostRow key={`${classId}_${queryId}_${p.postId}`}
              queryId={queryId}
              {...p}
              updatePostAction={updatePostAction}
              newCommentAction={newCommentAction}
              updateCommentAction={updateCommentAction}
              classId={classId}
            />)}
          </ul>

          <span className="query-display-add-post">
            <a className="label"
              onClick={() => setShowAdder(!showAdder)}
              aria-controls="add-post-form-wrapper"
              aria-expanded={showAdder}
            >
              <FontAwesomeIcon icon="reply" />Reply
            </a>
            <Collapse in={showAdder}>
              <div className="add-post-form-wrapper">
                <AddPostForm className="add-post-form" queryId={queryId} newPostAction={newPostAction} />
              </div>
            </Collapse>
          </span>
        </td>
      </tr>
    )
}


const DisplayTable = ({queries, newPostAction, newCommentAction,
                       updatePostAction, updateCommentAction}) => {
  if (!!queries && !!queries[0] && !queries[0].section) {
    return (<Table>
            <tbody>
              {queries.map(
                q => <DisplayRow key={q.queryId}
                       newPostAction={newPostAction}
                       newCommentAction={newCommentAction}
                       updatePostAction={updatePostAction}
                       updateCommentAction={updateCommentAction}
                       classId={null}
                       {...q}
                     />
              )}
            </tbody>
            </Table>
      )
  } else if (!!queries && !!queries[0] && !!queries[0].section) {
    return (
        <Table>
        <tbody>
          {queries != [] && queries.map(({classId, institution, year, section, queries}) =>
            <tr key={`${institution}_${year}_${section}`} >
              <td>
                <span className="query-display-class-header">
                  {`${institution}, ${year}, ${section}`}
                </span>
                <Table>
                  <tbody>
                  {!!queries.length && queries.map(
                    q => <DisplayRow key={`${classId}_${q.queryId}`}
                           newPostAction={newPostAction}
                           newCommentAction={newCommentAction}
                           updatePostAction={updatePostAction}
                           updateCommentAction={updateCommentAction}
                           classId={classId}
                           {...q}
                         />
                  )}
                  </tbody>
                </Table>
              </td>
            </tr>
          )}
        </tbody>
        </Table>
    )
  } else {
    return <Table />
  }
}

const QueriesView = () => {

    const {user, dispatch} = useContext(UserContext);
    const [queries, setQueries] = useState(null);
    const [userQueries, setUserQueries] = useState(null);
    const [classQueries, setClassQueries] = useState(null);
    const [otherQueries, setOtherQueries] = useState(null);
    const [viewScope, setViewScope] = useState('public');
    const [onStep, setOnStep] = useState(!!user.currentStep);

    const _formatPostData = p => {
      return ({postId: p.bug_posts.id,
                posterId: p.bug_posts.poster,
                postText: p.bug_posts.post_body,
                posterNameFirst: p.auth_user.first_name,
                posterNameLast: p.auth_user.last_name,
                postDate: p.bug_posts.dt_posted,
                postEditedDate: p.bug_posts.modified_on,
                posterRole: p.bug_posts.poster_role,
                hidden: p.bug_posts.hidden,
                deleted: p.bug_posts.deleted || false,
                flagged: p.bug_posts.flagged || false,
                pinned: p.bug_posts.pinned || false,
                showPublic: p.bug_posts.public || true,
                threadIndex: p.bug_posts.thread_index,
                comments: p.comments
              }
      )
    }

    const _formatQueryData = q => {
      let formattedPosts = q.posts.map(p => _formatPostData(p));
      if ( !!q.bugs.admin_comment ) {
        formattedPosts.unshift({
          postId: undefined,
          posterId: 19,
          postText: q.bugs.admin_comment,
          posterNameFirst: "Ian",
          posterNameLast: "Scott",
          postDate: "",
          postEditedDate: "",
          posterRole: ["administrators", "instructors"],
          hidden: false,
          deleted: false,
          flagged: false,
          showPublic: true,
          threadIndex: 0,
          comments: []
        });
      }
      return ({queryId: q.bugs.id,
                opId: q.auth_user.id,
                opNameFirst: q.auth_user.first_name,
                opNameLast: q.auth_user.last_name,
                posts: formattedPosts,
                dateSubmitted: q.bugs.date_submitted,
                queryStatus: q.bugs.bug_status,
                opResponse: q.bugs.user_response,
                opQueryText: q.bugs.user_comment,
                hidden: q.bugs.hidden,
                showPublic: q.bugs.public,
                flagged: q.bugs.flagged,
                deleted: q.bugs.deleted,
                queryStep: q.bugs.step,
                queryPath: q.bugs.in_path,
              }
      )
    }

    const _formatClassData = ({id, institution, section, year, queries}) => {
      return ({classId: id,
               institution: institution,
               section: section,
               year: year,
               queries: queries.map(q => _formatQueryData(q))
              }
      )
    }

    const _findAndUpdatePost = (mylist, newPost) => {
      const myQueryId = newPost.bug_posts.on_bug;
      const queryIndex = qList.findIndex(q => q.queryId==myQueryId);
      if ( mylist.length && !!mylist[0].classId ) {

      } else {

        qList[queryIndex].posts.push(_formatPostData(newPost));
      }
    }

    const fetchAction = () => {

      getStepQueries({step_id: user.currentStep,
                      user_id: user.userId})
      .then(queryfetch => {
        console.log(queryfetch);

        setQueries(queryfetch);
        setUserQueries(queryfetch.user_queries.map(
          q => _formatQueryData(q)
        ));
        setClassQueries(queryfetch.class_queries.map(
          c => _formatClassData(c)
        ));
        setOtherQueries(queryfetch.other_queries.slice(0, 20).map(
          q => _formatQueryData(q)
        ));
      });
    }

    useEffect(() => fetchAction(), [user.currentStep]);

    const newQueryAction = (myComment, showPublic) => {
      event.preventDefault();
      const myscore = !!user.currentScore && user.currentScore != 'null' ?
        user.currentScore : null;
      submitNewQuery({step_id: user.currentStep,
                      path_id: user.currentPath,
                      user_id: user.userId,
                      loc_name: user.currentLocation,
                      answer: user.currentAnswer,
                      log_id: user.currentLogID,
                      score: myscore,
                      user_comment: myComment,
                      show_public: showPublic})
      .then(myresponse => {
        setUserQueries(myresponse.map(
          q => _formatQueryData(q)
        ));
      });
    }

    const newPostAction = (queryId, postText, isPublic, event) => {
      event.preventDefault();
      addQueryPost({user_id: user.userId,
                    query_id: queryId,
                    post_text: postText,
                    showPublic: isPublic
                    })
      .then(myresponse => {
        for (i=0, i < myScopes.length, i++) {
          let qList = [...myScopes[i].list];
          const newPost = myresponse.new_post;
          const newQList;
          if ( mylist.length && !!mylist[0].classId ) {
            newQList = qList.map(myClass => {
              myClass.queries = _findAndUpdatePost(myClass.queries, newPost);
              return myClass;
            })
          } else if ( mylist.length ) {
            newQList = _findAndUpdatePost(qList, newPost);
          }
          myScopes[i].action(newQList);
        }
      });
    }

    const newCommentAction = () => {
      event.preventDefault();
      addQueryComment({user_id: user.userId,
                       post_id: queryId,
                       comment_text: postText,
                       showPublic: isPublic
                       })
      .then(myresponse => {
          setUserQueries(myresponse);
      });
    }

    const updatePostAction = ({postId=null,
                               queryId=null,
                               postText=null,
                               isPublic=null,
                               hidden=null,
                               flagged=null,
                               pinned=null,
                               popular=null,
                               helpfulness=null,
                               deleted=null,
                               event=null
                              }) => {
      event.preventDefault();
      console.log("postId");
      console.log(postId);
      updateQueryPost({user_id: user.userId,
                       post_id: postId,
                       query_id: queryId,
                       post_text: postText,
                       show_public: isPublic,
                       hidden: hidden,
                       flagged: flagged,
                       pinned: pinned,
                       popuar: popular,
                       helpulness: helpfulness,
                       deleted: deleted
                       })
      .then(myresponse => {
        console.log(myresponse.bug_post_list);
        console.log(myresponse.new_post);
      });
    }

    const updateCommentAction = () => {
      event.preventDefault();
      updateQueryComment({user_id: user.userId,
                          comment_id: queryId,
                          comment_text: postText,
                          showPublic: isPublic,
                          hidden: hidden,
                          flagged: flagged,
                          pinned: pinned,
                          popuar: popular,
                          helpfulness: helpfulness
                          })
      .then(myresponse => {
          setUserQueries(myresponse);
      });
    }

    const LoadingContent = () => (
      <Spinner animation="grow" variant="secondary"
        className="align-self-center map-spinner" />
    );

    console.log("class queries");
    console.log(classQueries);
    console.log("user queries");
    console.log(userQueries);
    console.log("other queries");
    console.log(otherQueries);
    const myScopes = [
      {scope: 'user',
       list: userQueries,
       action: setUserQueries},
      {scope: 'class',
       list: classQueries,
       action: setClassQueries},
      {scope: 'public',
       list: otherQueries,
       action: setOtherQueries}
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
              {scope === 'user' ? <NewQueryForm answer={user.currentAnswer} score={user.currentScore} action={newQueryAction} /> : ''}
              <DisplayTable
                queries={list}
                newPostAction={newPostAction}
                updatePostAction={updatePostAction}
                newCommentAction={newCommentAction}
                updateCommentAction={updateCommentAction}
              />
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