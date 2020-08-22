import React, { useContext, useState, useEffect } from "react";
import {
    Badge,
    Button,
    Col,
    Collapse,
    Form,
    OverlayTrigger,
    Row,
    Spinner,
    Table,
    Tooltip,
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
         addPostComment,
         updatePostComment
 } from "../Services/stepFetchService";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { findIndex } from "core-js/es/array";
import { readableDateAndTime } from "../Services/dateTimeService";

const RoleIcon = ({icon}) => {
  const roles = {instructors: "chalkboard-teacher",
                 administrators: "hard-hat",
                 students: "graduation-cap"
                 }
  return ( <OverlayTrigger placement="top"
             className={`role-icon-${icon}`}
             overlay={
               <Tooltip id={`tooltip-role-${icon}`}>{icon.slice(0, -1)}</Tooltip>
             }
           >
             <FontAwesomeIcon icon={roles[icon]} />
           </OverlayTrigger>
  )
}

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

const CommentRow = ({queryId, commentId, commenterId, commenterRole,
                     postId, commentDate, threadIndex, commentText,
                     showPublic, hidden, deleted, flagged, pinned,
                     popularity, helpfulness, editedDate,
                     commenterFirstName, commenterLastName,
                     updateCommentAction, classId
                   }) => {

  const {user, dispatch} = useContext(UserContext);
  const keyStr = `${classId}_${queryId}_${postId}`;
  const myRoles = !!commenterRole && commenterRole != null ? commenterRole.map(r => `${r}`).join(" ") : "";
  const showEditingForm = () => {};

  console.log("comment to display");
  console.log(commentText);

  return (
    <li key={keyStr}>
      <Row>
      <Col xs={3} className={`comment-display-info ${myRoles}`}>
        <span className={`comment-display-name ${myRoles}`}>
          {`${commenterFirstName} ${commenterLastName}`}
        </span><br />
        {commenterRole.map(r =>
          <RoleIcon className={`role-icon ${r}`}
            key={`${keyStr}-${r}`} icon={r}
          />
        )}
      </Col>
      <Col xs={9} className={`comment-display-body ${myRoles}`}>
        <div
          className="comment-display-body-text"
          dangerouslySetInnerHTML={{
            __html: commentText ? DOMPurify.sanitize(marked(commentText)) : ""}}
        />
        <span className={`comment-display-date`}>
          <FontAwesomeIcon icon="clock" size="sm" />{readableDateAndTime(commentDate)}
        </span>
        {!!editedDate && (editedDate !== commentDate) &&
          <span className={`comment-display-edited-date`}>
            <FontAwesomeIcon icon="clock" size="sm" />last edited {readableDateAndTime(editedDate)}
          </span>
        }
        <div className="comment-display-controls">
          {user.userId === commenterId &&
            <Button variant="outline-secondary"
              onClick={e => showEditingForm(e)}
            >
              <FontAwesomeIcon icon="pencil-alt" />
            </Button>
          }
          {user.userId === commenterId &&
            <Button variant="outline-secondary"
              onClick={e =>
                updateCommentAction({postId: postId, commentId: queryId,
                                  deleted: true, event: e})
              }
            >
              <FontAwesomeIcon icon="trash-alt" />
            </Button>
          }
          {user.userId !== commenterId &&
            <Button variant="outline-secondary"
              onClick={e =>
                updateCommentAction({postId: postId, commentId: commentId,
                                  popularity: popularity + 1, event: e})
              }
            >
              <FontAwesomeIcon icon="thumbs-up" />
            </Button>
          }
          {(user.userRoles.includes("administrators") || user.userRoles.includes("instructors") && user.instructing.find(c => c.id == classId)) &&
            <Button variant="outline-secondary"
              onClick={e =>
                updateCommentAction({postId: postId, commentId: commentId,
                                  pinned: true, event: e})
              }
            >
              <FontAwesomeIcon icon="thumbtack" />
            </Button>
          }
          {(user.userRoles.includes("administrators") || user.userRoles.includes("instructors")) &&
            <Button variant="outline-secondary"
              onClick={e =>
                updateCommentAction({postId: postId, commentId: commentId,
                                  helpfulness: helpfulness + 1, event: e})
              }
            >
              <FontAwesomeIcon icon="lightbulb" />
            </Button>
          }
        </div>
      </Col>
      </Row>
    </li>
  )
}

const PostRow = ({queryId, postId, posterId, postText, posterNameFirst,
                  posterNameLast, postDate, postEditedDate, posterRole, hidden,
                  deleted, flagged, showPublic, popularity, helpfulness,
                  comments,
                  updatePostAction, newCommentAction, updateCommentAction,
                  classId
                }) => {
  const {user, dispatch} = useContext(UserContext);
  const [ showAdder, setShowAdder ] = useState(false);
  const [ editing, setEditing ] = useState(false);
  const keyStr = `${classId}_${queryId}_${postId}`;
  const showEditingForm = (e) => {
    e.preventDefault();
    setEditing(true);
  }
  const myRoles = !!posterRole && posterRole != null ? posterRole.map(r => `${r}`).join(" ") : "";
  console.log(postId);
  return (
    <li key={keyStr}>
      <Row>
      <Col xs={3} className={`post-display-info ${myRoles}`}>
        <span className={`post-display-name ${myRoles}`}>
          {`${posterNameFirst} ${posterNameLast}`}
        </span><br />
        {posterRole.map(r =>
          <RoleIcon className={`role-icon ${r}`}
            key={`${keyStr}-${r}`} icon={r}
          />
        )}
        <FontAwesomeIcon icon="user-circle" size="3x" /><br />
      </Col>
      <Col xs={9} className={`post-display-body ${myRoles}`}>
        <SwitchTransition>
          <CSSTransition
            key={!!editing ? "post-display-body-editor" : "post-display-body-text"}
            classNames='post-display-body-wrapper'
            unmountOnExit={false}
            timeout={200}
          >
          {!!editing ?
            <div className="post-display-body-wrapper">
              <UpdatePostForm postId={postId}
                queryId={queryId}
                updatePostAction={updatePostAction}
                currentText={postText ? DOMPurify.sanitize(postText) : ""}
                setEditing={setEditing}
              />
            </div>
            :
            <div className="post-display-body-wrapper">
              <div
                className="post-display-body-text"
                dangerouslySetInnerHTML={{
                  __html: postText ? DOMPurify.sanitize(marked(postText)) : ""}}
              />
              <span className={`post-display-date`}>
                <FontAwesomeIcon icon="clock" size="sm" />{readableDateAndTime(postDate)}
              </span>
              {!!postEditedDate && (postEditedDate !== postDate) &&
                <span className={`post-display-edited-date`}>
                  <FontAwesomeIcon icon="clock" size="sm" />last edited {readableDateAndTime(postEditedDate)}
                </span>
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
                  <Button variant="outline-secondary"
                    onClick={e =>
                      updatePostAction({postId: postId, queryId: queryId,
                                        deleted: true, event: e})
                    }
                  >
                    <FontAwesomeIcon icon="trash-alt" />
                  </Button>
                }
                {user.userId !== posterId &&
                  <Button variant="outline-secondary"
                    onClick={e =>
                      updatePostAction({postId: postId, queryId: queryId,
                                        popularity: popularity + 1, event: e})
                    }
                  >
                    <FontAwesomeIcon icon="thumbs-up" />
                  </Button>
                }
                {(user.userRoles.includes("administrators") || user.userRoles.includes("instructors") && user.instructing.find(c => c.id == classId)) &&
                  <Button variant="outline-secondary"
                    onClick={e =>
                      updatePostAction({postId: postId, queryId: queryId,
                                        pinned: true, event: e})
                    }
                  >
                    <FontAwesomeIcon icon="thumbtack" />
                  </Button>
                }
                {(user.userRoles.includes("administrators") || user.userRoles.includes("instructors")) &&
                  <Button variant="outline-secondary"
                    onClick={e =>
                      updatePostAction({postId: postId, queryId: queryId,
                                        helpfulness: helpfulness + 1, event: e})
                    }
                  >
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
                    setShowAdder={setShowAdder}
                  />
                </div>
              </Collapse>
            </div>
          }
          </CSSTransition>
        </SwitchTransition>
      </Col>
      </Row>
      <Row>
      <ul className="post-display-comments-list">
        {!!comments.length ? comments.map(c =>
          <CommentRow key={`${keyStr}_${c.commentId}`}
            queryId={queryId}
            updateCommentAction={updateCommentAction}
            classId={classId}
            {...c}
          />)
          :
          ""
        }
      </ul>
      </Row>
    </li>
  )
}

const AddCommentForm = ({queryId, postId, newCommentAction, setShowAdder}) => {
  const [commentText, setCommentText] = useState("");
  const [isPrivate, setIsPrivate] = useState(false);
  const submitComment = e => {
    newCommentAction({postId: postId, queryId: queryId,
                      commentText: commentText,
                      isPublic: !isPrivate,
                      event: e
                     });
    setShowAdder(false);
  }
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
          onClick={e => submitComment(e)}
        >Submit comment</Button>
    </Form>
  )
}

const UpdatePostForm = ({postId, queryId, updatePostAction, currentText,
                         setEditing}) => {
  const [postText, setPostText] = useState(currentText);
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
                     opQueryText, stepPrompt, hidden, showPublic, flagged, deleted,
                     popularity, hepfulness, pinned,
                     queryStep, queryPath
                    }) => {
  const [ showAdder, setShowAdder ] = useState(false);

  return (
      <tr key={queryId}>
        <td key={`${queryId}_cell`}>
          <Row className="query-display-op-wrapper" >
            <Col xs={3} className="query-display-op">
              <span className="query-display-op-name">
                {`${opNameFirst} ${opNameLast}`}
              </span><br />
              <span className="query-display-op-date">
                {readableDateAndTime(dateSubmitted)}
              </span><br />
              <FontAwesomeIcon icon="user-circle" size="3x" /><br />
              <span className="query-display-op-status">{
                ["", "confirmed",	"fixed",	"not_a_bug",
                "duplicate",	"awaiting review",	"allowance_given",
                "question_answered"][queryStatus].replace("_", " ")
                }</span>
            </Col>
            <Col xs={9} className="query-display-body-wrapper">
              {!!queryStep &&
                <React.Fragment>
                  The step asked...
                  <p className="query-display-prompt"
                    dangerouslySetInnerHTML={{
                      __html: !!stepPrompt ? DOMPurify.sanitize(marked(stepPrompt)) : ""}}
                  />
                </React.Fragment>
              }
              {!!opResponse &&
                <React.Fragment>
                  And I responded...
                  <p className="query-display-response"
                    dangerouslySetInnerHTML={{
                      __html: !!opResponse ? DOMPurify.sanitize(marked(opResponse)) : ""}}
                  />
                </React.Fragment>
              }
              <p className="query-display-op-question"
                dangerouslySetInnerHTML={{
                  __html: opQueryText ? DOMPurify.sanitize(marked(opQueryText)) : ""
                }} />
            </Col>
          </Row>
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
    const [filterUnanswered, setFilterUnanswered] = useState('false');
    const [onStep, setOnStep] = useState(!!user.currentStep);

    const _formatCommentData = c => {
      return ({commentId: c.bug_post_comments.id,
               commenterId: c.bug_post_comments.commenter,
               commenterRole: c.bug_post_comments.commenter_role,
               postId: c.bug_post_comments.on_post,
               commentDate: c.bug_post_comments.dt_posted,
               threadIndex: c.bug_post_comments.thread_index,
               commentText: c.bug_post_comments.comment_body,
               showPublic: c.bug_post_comments.public,
               hidden: c.bug_post_comments.hidden,
               deleted: c.bug_post_comments.deleted,
               flagged: c.bug_post_comments.flagged,
               pinned: c.bug_post_comments.pinned,
               popularity: c.bug_post_comments.popularity,
               helpfulness: c.bug_post_comments.helpfulness,
               editedDate: c.bug_post_comments.modified_on,
               commenterFirstName: c.auth_user.first_name,
               commenterLastName: c.auth_user.last_name
              })
    }

    const _formatPostData = p => {
      let formattedComments = p.comments.map(c => _formatCommentData(c));
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
                comments: formattedComments
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
          postDate: q.bugs.date_submitted,
          postEditedDate: q.bugs.modified_on,
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
                stepPrompt: q.bugs.prompt,
                hidden: q.bugs.hidden,
                showPublic: q.bugs.public,
                flagged: q.bugs.flagged,
                deleted: q.bugs.deleted,
                queryStep: q.bugs.step,
                queryPath: q.bugs.in_path,
                dateUpdated: q.bugs.modified_on
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

    // finds and updates a post in a list of queries in state
    // doesn't assume query or post already exist
    // creates new post if specified doesn't exist
    // returns the modified version of the supplied query list
    // if the new post has deleted: true it is removed
    const _findAndUpdatePost = (mylist, newPost) => {
      const myQueryId = newPost.bug_posts.on_bug;
      const myPostId = newPost.bug_posts.id;
      const queryIndex = mylist.findIndex(q => q.queryId==myQueryId);
      if ( queryIndex > -1 ) {
        const postIndex = mylist[queryIndex].posts.findIndex(p => p.postId==myPostId);
        if ( postIndex > -1 ) {
          if ( newPost.bug_posts.deleted ) {
            mylist[queryIndex].posts.splice(postIndex, 1);
          } else {
            mylist[queryIndex].posts[postIndex] = _formatPostData(newPost);
          }
        } else {
          mylist[queryIndex].posts.push(_formatPostData(newPost));
        }
      }
      return mylist;
    }

    // Non-returning function to properly update state with one post
    // expects myresponse to have keys "post_list" and "new_post"
    const _updatePostInState = (myresponse, myscopes) => {
      for (let i=0; i < myscopes.length; i++) {
        let qList = [...myscopes[i].list];
        const newPost = myresponse.new_post;
        const newQList = [];
        if ( qList.length && !!qList[0].classId ) {
          newQList = qList.map(myClass => {
            myClass.queries = _findAndUpdatePost(myClass.queries, newPost);
            return myClass;
          })
        } else if ( qList.length ) {
          newQList = _findAndUpdatePost(qList, newPost);
        }
        myscopes[i].action(newQList);
      }
    }

    // finds and updates a comment in a list of queries in state
    // doesn't assume query or comment already exist
    // creates new comment if specified doesn't exist
    // returns the modified version of the supplied query list
    // if the new comment has deleted: true it is removed
    const _findAndUpdateComment = (mylist, newComment, queryId) => {
      const myPostId = newComment.bug_post_comments.on_post;
      const myCommentId = newComment.bug_post_comments.id;
      const queryIndex = mylist.findIndex(q => q.queryId==queryId);
      if ( queryIndex > -1 ) {
        const postIndex = mylist[queryIndex].posts.findIndex(p => p.postId==myPostId);
        if ( postIndex > -1 ) {
          const commIndex = mylist[queryIndex].posts[postIndex].comments.findIndex(c => c.commentId==myCommentId);
          if ( commIndex > -1 ) {
            if ( newComment.bug_post_comments.deleted ) {
              mylist[queryIndex].posts[postIndex].comments.splice(commIndex, 1);
            } else {
              mylist[queryIndex].posts[postIndex].comments[commIndex] = _formatCommentData(newComment);
            }
          } else {
            mylist[queryIndex].posts[postIndex].comments.push(_formatCommentData(newComment));
          }
        }
      }
      return mylist;
    }

    // Non-returning function to properly update state with one comment
    // expects myresponse to have keys "comment_list" and "new_comment"
    const _updateCommentInState = (myresponse, myscopes, queryId) => {
      for (let i=0; i < myscopes.length; i++) {
        let qList = [...myscopes[i].list];
        const newComment = myresponse.new_comment;
        const newQList = [];
        if ( qList.length && !!qList[0].classId ) {
          newQList = qList.map(myClass => {
            myClass.queries = _findAndUpdateComment(myClass.queries, newComment, queryId);
            return myClass;
          })
        } else if ( qList.length ) {
          newQList = _findAndUpdateComment(qList, newComment, queryId);
        }
        myScopes[i].action(newQList);
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
        _updatePostInState(myresponse, myScopes);
      });
    }

    const newCommentAction = ({postId=null,
                               queryId=null,
                               commentText=null,
                               isPublic=null,
                               event=null
                              }) => {
      event.preventDefault();
      addPostComment({user_id: user.userId,
                      post_id: postId,
                      query_id: queryId,
                      comment_text: commentText,
                      showPublic: isPublic
                      })
      .then(myresponse => {
        console.log(myresponse);
        _updateCommentInState(myresponse, myScopes, queryId);
      });
    }

    const updatePostAction = ({postId=null,
                               queryId=null,
                               postText=null,
                               isPublic=null,
                               hidden=null,
                               flagged=null,
                               pinned=null,
                               popularity=null,
                               helpfulness=null,
                               deleted=null,
                               event=null
                              }) => {
      event.preventDefault();
      updateQueryPost({user_id: user.userId,
                       post_id: postId,
                       query_id: queryId,
                       post_text: postText,
                       show_public: isPublic,
                       hidden: hidden,
                       flagged: flagged,
                       pinned: pinned,
                       popularity: popularity,
                       helpulness: helpfulness,
                       deleted: deleted
                       })
      .then(myresponse => {
        _updatePostInState(myresponse, myScopes);
      });
    }

    const updateCommentAction = ({commentId=null,
                                  postId=null,
                                  queryId=null,
                                  commentText=null,
                                  isPublic=null,
                                  hidden=null,
                                  flagged=null,
                                  pinned=null,
                                  popularity=null,
                                  helpfulness=null,
                                  deleted=null,
                                  event=null
                                  }) => {
      event.preventDefault();
      updatePostComment({user_id: user.userId,
                         comment_id: commentId,
                         post_id: postId,
                         bug_id: queryId,
                         comment_text: commentText,
                         showPublic: isPublic,
                         hidden: hidden,
                         flagged: flagged,
                         pinned: pinned,
                         popularity: popularity,
                         helpfulness: helpfulness
                        })
      .then(myresponse => {
        _updateCommentInState(myresponse, myScopes, queryId);
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
        <div className="queries-view-changer-wrapper">
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
        </div>

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
          <h2>Questions about
          <Button>This Step</Button>
          <Button>All Steps</Button>
          <Button>General</Button>
          </h2>

          <Form.Group controlId={`filterUnansweredCheckbox`}>
            <Form.Check type="checkbox" label="Only unanswered questions"
              defaultValue={filterUnanswered}
              onChange={e => setFilterUnanswered()}
              />
          </Form.Group>

          <div className="queries-view-wrapper">
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