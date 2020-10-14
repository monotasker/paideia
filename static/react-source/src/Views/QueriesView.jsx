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
         addQuery,
         updateQuery,
         addQueryReply,
         updateQueryReply,
         addReplyComment,
         updateReplyComment
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

const AdderButton = ({level, showAdderValue, showAdderAction, label, icon}) => {
  return (
    <span className={`${level}-button-container`}>
      <Button variant="outline-secondary"
        onClick={() => showAdderAction(!showAdderValue)}
        aria-controls={`add-${level}-form-wrapper`}
        aria-expanded={showAdderValue}
      >
        <FontAwesomeIcon icon={icon} />
        {label}
      </Button>
    </span>
  )
}

const ControlRow = ({userId, opId, level, icon, showAdderValue,
                     showAdderAction=None,
                     showEditorAction, updateAction, defaultUpdateArgs,
                     userRoles, instructing, showPublic,
                     flagged, pinned, popularity, helpfulness
                    }) => {
  const labelLevel = level === "query" ? "reply" : "comment";
  return(
    <div className={`control-row-${level}`}>
      {level !== "comment" ?
        <AdderButton level={level}
          showAdderValue={showAdderValue}
          showAdderAction={showAdderAction}
          label={`Add your ${labelLevel}`}
          icon={icon}
        />
        :
        ""
      }
      {userId === opId &&
        <Button variant="outline-secondary"
          onClick={e => showEditorAction(e)}
        >
          <FontAwesomeIcon icon="pencil-alt" />
        </Button>
      }
      {userId === opId &&
        <Button variant="outline-secondary"
          onClick={e =>
            updateAction({...defaultUpdateArgs,
                              deleted: true, event: e})
          }
        >
          <FontAwesomeIcon icon="trash-alt" />
        </Button>
      }
      {userId !== opId &&
        <Button variant="outline-secondary"
          onClick={e =>
            updateAction({...defaultUpdateArgs,
                              popularity: popularity + 1, event: e})
          }
        >
          <FontAwesomeIcon icon="thumbs-up" />
        </Button>
      }
      {(userRoles.includes("administrators") || userRoles.includes("instructors") && instructing.find(c => c.id == classId)) &&
        <Button variant="outline-secondary"
          onClick={e =>
            updateAction({...defaultUpdateArgs,
                              pinned: !pinned, event: e})
          }
        >
          <FontAwesomeIcon icon="thumbtack" />
        </Button>
      }
      {(userRoles.includes("administrators") || userRoles.includes("instructors")) &&
        <Button variant="outline-secondary"
          onClick={e =>
            updateAction({...defaultUpdateArgs,
                          helpfulness: helpfulness + 1, event: e})
          }
        >
          <FontAwesomeIcon icon="lightbulb" />
        </Button>
      }
    </div>
  )
}

const UpdateForm = ({level, idArgs, opId, updateAction, currentText,
                     setEditingAction
                    }) => {
  const [myText, setMyText] = useState(currentText);
  const idString = Object.values(idArgs).join("-");
  const sendUpdate = e => {
    e.preventDefault();
    updateAction({...idArgs, opId: opId, opText: myText});
    setEditingAction(false);
  }
  return (
    <Form id={`update-${level}-form-${idString}`}
      className={`update-${level}-form`}
    >
        <Form.Group controlId={`update${level}Textarea-${idString}`}>
          <TextareaAutosize
            defaultValue={currentText}
            onChange={e => setMyText(e.target.value)}
          />
        </Form.Group>
        <Button variant="primary"
          type="submit"
          onClick={e => sendUpdate(e)}
        >Update {level}</Button>
    </Form>
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

const AddChildForm = ({level, classId, queryId, replyId=null,
                       addChildAction, setShowAdder
                      }) => {
  // FIXME: Handling legacy data here
  if ( level=="reply" && replyId==undefined ) { replyId="null" };
  const [childText, setChildText] = useState("");
  const [isPrivate, setIsPrivate] = useState(false);
  const uid = [classId, queryId, replyId].join("_");
  const createChild = e => {
    e.preventDefault();
    console.log({replyId: replyId, queryId: queryId,
                    childText: childText,
                    isPublic: !isPrivate,
                    event: e,
                    addChildAction: addChildAction,
                    setShowAdder: setShowAdder
                    });
    addChildAction({replyId: replyId, queryId: queryId,
                    opText: childText,
                    isPublic: !isPrivate
                    });
    setShowAdder(false);
  }
  return (
    <Form id={`add-child-form-${uid}`}
      className={`add-child-form add-${level}-form`}
    >
      <Form.Group controlId={`addChildPrivateCheckbox-${uid}`}>
        <Form.Check type="checkbox"
          label={`Keep my ${level} private`}
          defaultValue={isPrivate}
          onChange={e => setIsPrivate(e.target.value)}
        />
      </Form.Group>
      <Form.Group controlId={`addChildTextarea-${uid}`}>
        <TextareaAutosize
          onChange={e => setChildText(e.target.value)}
        />
      </Form.Group>
      <Button variant="primary" type="submit"
        onClick={e => createChild(e)}
      >
        Submit {level}
      </Button>
    </Form>
  )
}

const DisplayRow = ({level, newReplyAction, newCommentAction,
                     updateReplyAction, updateCommentAction, updateQueryAction, queryId, opId, opNameFirst, opNameLast, opRole,
                     dateSubmitted, dateUpdated, opText,
                     hidden, showPublic, flagged, deleted,
                     popularity, helpfulness, pinned,
                     classId=null, replyId=null, commentId=null,
                     queryStatus=null, opResponseText=null, stepPrompt=null,
                     queryStep=null, queryPath=null,
                     children=null, threadIndex=0
                    }) => {
  const myRoles = !!opRole && opRole != null ?
    opRole.map(r => `${r}`).join(" ") : "";
  const {user, dispatch} = useContext(UserContext);
  const [ showAdder, setShowAdder ] = useState(false);
  const [ editing, setEditing ] = useState(false);
  const showEditingForm = (e) => {
    e.preventDefault();
    setEditing(true);
  }
  const uid = [classId, queryId, replyId, commentId].join('_');
  const levels = ["query", "reply", "comment"];
  const childLevel = levels[levels.indexOf(level) + 1];
  const updateArgs = {query: {pathId: queryPath, stepId: queryStep,
                              opId: opId, queryId: queryId},
                      reply: {opId: opId, replyId: replyId,
                              queryId: queryId},
                      comment: {opId: opId, commentId: commentId,
                                replyId: replyId, queryId: queryId}
  };
  const updateThisAction = {query: updateQueryAction,
                            reply: updateReplyAction,
                            comment: updateCommentAction
  };
  const addChildAction = {query: newReplyAction,
                          reply: newCommentAction,
                          comment: null
  };

  return (
    <li key={`${uid}-display-row ${level}-display-row ${myRoles}`}>
      <Row className={`${level}-display-op-wrapper`} >
        <Col xs={3} className={`${level}-display-op`}>
          <span className={`${level}-display-op-name`}>
            {`${opNameFirst} ${opNameLast}`}
          </span><br />
          <span className={`${level}-display-op-date`}>
            {readableDateAndTime(dateSubmitted)}
          </span><br />
          {level != "comment" ?
            <FontAwesomeIcon icon="user-circle"
              size={level == "query" ? "3x" : "1x"}
            /> : ""
          }
          {!!opRole && opRole.map(r =>
            <RoleIcon className={`role-icon ${r}`}
              key={`${uid}-${r}`} icon={r}
            />
          )}
          {!!queryStatus ?
            <span className={`${level}-display-op-status`}>{
              ["", "confirmed",	"fixed",	"not_a_bug",
              "duplicate",	"awaiting review",	"allowance_given",
              "question_answered"][queryStatus].replace("_", " ")}
            </span>
            : ""
          }
        </Col>
        <Col xs={9} className={`${level}-display-body-wrapper`}>
          {!!queryStep &&
            <React.Fragment>
              The step asked...
              <p className="query-display-prompt"
                dangerouslySetInnerHTML={{
                  __html: !!stepPrompt ? DOMPurify.sanitize(marked(stepPrompt)) : ""}}
              />
            </React.Fragment>
          }
          {!!opResponseText &&
            <React.Fragment>
              And I responded...
              <p className="query-display-response"
                dangerouslySetInnerHTML={{
                  __html: !!opResponseText ? DOMPurify.sanitize(marked(opResponseText)) : ""}}
              />
            </React.Fragment>
          }
          <SwitchTransition>
            <CSSTransition
              key={!!editing ? `${level}-display-body-editor` : `${level}-display-body-text`}
              classNames={`${level}-display-body-wrapper`}
              unmountOnExit={false}
              timeout={200}
            >
              {!!editing ?
                <div className={`${level}-display-body-wrapper`}>
                  <UpdateForm level={level}
                    idArgs={updateArgs[level]}
                    updateAction={updateThisAction[level]}
                    currentText={opText ? DOMPurify.sanitize(opText) : ""}
                    setEditingAction={setEditing}
                  />
                </div>
                :
                <div className={`${level}-display-body-wrapper`}>
                  <p className={`${level}-display-op-question`}
                    dangerouslySetInnerHTML={{
                      __html: opText ? DOMPurify.sanitize(marked(opText)) : ""}}
                  />
                  <span className={`${level}-display-date`}>
                    <FontAwesomeIcon icon="clock" size="sm" />{readableDateAndTime(dateSubmitted)}
                  </span>
                  {!!dateUpdated && (dateUpdated !== dateSubmitted) &&
                    <span className={`${level}-display-edited-date`}>
                      <FontAwesomeIcon icon="clock" size="sm" />last edited {readableDateAndTime(dateUpdated)}
                    </span>
                  }
                  <ControlRow
                    userId={user.userId}
                    opId={opId}
                    level={level}
                    icon={level == "comment" ? null : childLevel}
                    showAdderValue={level == "comment" ? null : showAdder}
                    showAdderAction={level == "comment" ? null : setShowAdder}
                    showEditorAction={showEditingForm}
                    updateAction={updateThisAction[level]}
                    defaultUpdateArgs={updateArgs[level]}
                    userRoles={user.userRoles}
                    instructing={user.instructing}
                    showPublic={showPublic}
                    flagged={flagged}
                    pinned={pinned}
                    popularity={popularity}
                    helpfulness={helpfulness}
                    userRoles={user.userRoles}
                    instructing={user.instructing}
                  />
                </div>
              }
              </CSSTransition>
              </SwitchTransition>
            </Col>
          </Row>

          {level != "comment" &&
            <span className={`${level}-display-add-child`}>
              <a className="label"
                onClick={() => setShowAdder(!showAdder)}
                aria-controls={`${uid}-add-child-form-wrapper`}
                aria-expanded={showAdder}
              >
                <FontAwesomeIcon icon={childLevel} />{childLevel.toUpperCase()}
              </a>
              <Collapse in={showAdder}>
                <div className={`${uid}-add-child-form-wrapper`}>
                  <AddChildForm className="add-child-form"
                    level={childLevel}
                    classId={classId}
                    queryId={queryId}
                    replyId={replyId}
                    addChildAction={addChildAction[level]}
                    setShowAdder={setShowAdder}
                  />
                </div>
              </Collapse>
            </span>
          }

          <ul className={`${level}-display-children`}>
          {!!children && children.map(c =>
            <DisplayRow key={`${classId}_${queryId}_${!!replyId ? `${replyId}_${c.commentId}` : c.replyId}`}
              level={childLevel}
              classId={classId}
              queryId={queryId}
              replyId={!!replyId ? replyId : c.replyId}
              commentId={!!replyId ? c.commentId: null}
              {...c}
              updateQueryAction={updateQueryAction}
              newReplyAction={newReplyAction}
              updateReplyAction={updateReplyAction}
              newCommentAction={newCommentAction}
              updateCommentAction={updateCommentAction}
            />)}
          </ul>

      </li>
    )
}


const DisplayTable = ({queries, updateQueryAction, newReplyAction,
                       newCommentAction, updateReplyAction,
                       updateCommentAction}) => {
  if (!!queries && !!queries[0] && !queries[0].section) {
    return (<ul>
              {queries.map(
                q => <DisplayRow key={`query-row-${q.queryId}`}
                       level="query"
                       updateQueryAction={updateQueryAction}
                       newReplyAction={newReplyAction}
                       newCommentAction={newCommentAction}
                       updateReplyAction={updateReplyAction}
                       updateCommentAction={updateCommentAction}
                       classId={null}
                       {...q}
                     />
              )}
            </ul>
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
                <ul>
                  {!!queries.length && queries.map(
                    q => <DisplayRow key={`${classId}_${q.queryId}`}
                           level="query"
                           updateQueryAction={updateQueryAction}
                           newReplyAction={newReplyAction}
                           newCommentAction={newCommentAction}
                           updateReplyAction={updateReplyAction}
                           updateCommentAction={updateCommentAction}
                           classId={classId}
                           {...q}
                         />
                  )}
                  </ul>
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
      return ({level: "comment",
               replyId: c.bug_post_comments.on_post,
               commentId: c.bug_post_comments.id,
               opId: c.bug_post_comments.commenter,
               opFirstName: c.auth_user.first_name,
               opLastName: c.auth_user.last_name,
               opText: c.bug_post_comments.comment_body,
               dateSubmitted: c.bug_post_comments.dt_posted,
               dateUpdated: c.bug_post_comments.modified_on,
               opRole: c.bug_post_comments.commenter_role,
               hidden: c.bug_post_comments.hidden,
               deleted: c.bug_post_comments.deleted,
               flagged: c.bug_post_comments.flagged,
               pinned: c.bug_post_comments.pinned,
               popularity: c.bug_post_comments.popularity,
               helpfulness: c.bug_post_comments.helpfulness,
               showPublic: c.bug_post_comments.public,
               threadIndex: c.bug_post_comments.thread_index
              })
    }

    const _formatReplyData = p => {
      let formattedComments = p.comments.map(c => _formatCommentData(c));
      return ({level: "reply",
               replyId: p.bug_posts.id,
               opId: p.bug_posts.poster,
               opNameFirst: p.auth_user.first_name,
               opNameLast: p.auth_user.last_name,
               opText: p.bug_posts.post_body,
               dateSubmitted: p.bug_posts.dt_posted,
               dateUpdated: p.bug_posts.modified_on,
               opRole: p.bug_posts.poster_role,
               hidden: p.bug_posts.hidden,
               deleted: p.bug_posts.deleted || false,
               flagged: p.bug_posts.flagged || false,
               pinned: p.bug_posts.pinned || false,
               popularity: 0,
               helpfulness: 0,
               showPublic: p.bug_posts.public || true,
               threadIndex: p.bug_posts.thread_index,
               children: formattedComments
              }
      )
    }

    const _formatQueryData = q => {
      let formattedReplies = q.posts.map(p => _formatReplyData(p));
      if ( !!q.bugs.admin_comment ) {
        formattedReplies.unshift({
          level: "reply",
          replyId: undefined,
          opId: 19,
          opNameFirst: "Ian",
          opNameLast: "Scott",
          opText: q.bugs.admin_comment,
          dateSubmitted: q.bugs.date_submitted,
          dateUpdated: q.bugs.modified_on,
          opRole: ["administrators", "instructors"],
          hidden: false,
          deleted: false,
          flagged: false,
          pinned: false,
          popularity: 0,
          helpfulness: 0,
          showPublic: true,
          threadIndex: 0,
          children: []
        });
      }
      let myPrompt = q.bugs.prompt;
      if ( !!q.bugs.step_options && q.bugs.step_options.length ) {
        const optString = q.bugs.step_options.join("\n- ");
        myPrompt = `${myPrompt}\n\n- ${optString}`;
      }
      return ({level: "query",
               queryId: q.bugs.id,
               opId: q.auth_user.id,
               opNameFirst: q.auth_user.first_name,
               opNameLast: q.auth_user.last_name,
               children: formattedReplies,
               dateSubmitted: q.bugs.date_submitted,
               dateUpdated: q.bugs.modified_on,
               queryStatus: q.bugs.bug_status,
               opResponseText: q.bugs.user_response,
               opText: q.bugs.user_comment,
               stepPrompt: myPrompt,
               hidden: q.bugs.hidden,
               showPublic: q.bugs.public,
               flagged: q.bugs.flagged,
               deleted: q.bugs.deleted,
               pinned: q.bugs.pinned,
               helpfulness: q.bugs.helpfulness,
               popularity: q.bugs.popularity,
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

    // finds and updates a post in a list of queries in state
    // doesn't assume query or post already exist
    // creates new post if specified doesn't exist
    // returns the modified version of the supplied query list
    // if the new post has deleted: true it is removed
    const _findAndUpdateReply = (mylist, newReply) => {
      const myQueryId = newReply.bug_posts.on_bug;
      console.log(myQueryId);
      const myReplyId = newReply.bug_posts.id;
      console.log(myReplyId);
      const queryIndex = mylist.findIndex(q => q.queryId==myQueryId);
      console.log(queryIndex);
      console.log(mylist[queryIndex]);
      if ( queryIndex > -1 ) {
        const replyIndex = mylist[queryIndex].children.findIndex(p => p.postId==myReplyId);
        if ( replyIndex > -1 ) {
          if ( newReply.bug_posts.deleted ) {
            mylist[queryIndex].children.splice(replyIndex, 1);
          } else {
            mylist[queryIndex].children[replyIndex] = _formatReplyData(newReply);
          }
        } else {
          mylist[queryIndex].children.push(_formatReplyData(newReply));
        }
      }
      return mylist;
    }


    const _updateQueryInState = () => {

    }

    // Non-returning function to properly update state with one post
    // expects myresponse to have keys "post_list" and "new_post"
    const _updateReplyInState = (myresponse, myscopes) => {
      for (let i=0; i < myscopes.length; i++) {
        let qList = [...myscopes[i].list];
        const newReply = myresponse.new_post;
        const newQList = [];
        if ( qList.length && !!qList[0].classId ) {
          newQList = qList.map(myClass => {
            myClass.queries = _findAndUpdateReply(myClass.queries, newReply);
            return myClass;
          })
        } else if ( qList.length ) {
          newQList = _findAndUpdateReply(qList, newReply);
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
      const myReplyId = newComment.bug_post_comments.on_post;
      const myCommentId = newComment.bug_post_comments.id;
      const queryIndex = mylist.findIndex(q => q.queryId==queryId);
      if ( queryIndex > -1 ) {
        const replyIndex = mylist[queryIndex].children.findIndex(p => p.postId==myReplyId);
        if ( replyIndex > -1 ) {
          const commIndex = mylist[queryIndex].children[replyIndex].children.findIndex(c => c.commentId==myCommentId);
          if ( commIndex > -1 ) {
            if ( newComment.bug_post_comments.deleted ) {
              mylist[queryIndex].children[replyIndex].children.splice(commIndex, 1);
            } else {
              mylist[queryIndex].children[replyIndex].children[commIndex] = _formatCommentData(newComment);
            }
          } else {
            mylist[queryIndex].children[replyIndex].children.push(_formatCommentData(newComment));
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
      addQuery({step_id: user.currentStep,
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

    const newReplyAction = ({replyId,
                             queryId,
                             opText,
                             isPublic
                             }) => {
      addQueryReply({user_id: user.userId,
                    query_id: queryId,
                    post_text: opText,
                    showPublic: isPublic
                    })
      .then(myresponse => {
        _updateReplyInState(myresponse, myScopes);
      });
    }

    const newCommentAction = ({replyId=null,
                               queryId=null,
                               opText=null,
                               isPublic=null,
                              }) => {
      addReplyComment({user_id: user.userId,
                      post_id: replyId,
                      query_id: queryId,
                      comment_text: opText,
                      showPublic: isPublic
                      })
      .then(myresponse => {
        console.log(myresponse);
        _updateCommentInState(myresponse, myScopes, queryId);
      });
    }

    const updateQueryAction = ({opId=null,
                                queryId=null,
                                opText=null,
                                isPublic=null,
                                hidden=null,
                                flagged=null,
                                pinned=null,
                                popularity=null,
                                helpfulness=null,
                                deleted=null
                               }) => {
      updateQuery({user_id: opId,
                       query_id: queryId,
                       query_text: opText,
                       show_public: isPublic,
                       hidden: hidden,
                       flagged: flagged,
                       pinned: pinned,
                       popularity: popularity,
                       helpulness: helpfulness,
                       deleted: deleted
                       })
      .then(myresponse => {
        _updateQueryInState(myresponse, myScopes);
      });
    }

    const updateReplyAction = ({opId,
                               replyId,
                               queryId,
                               opText=null,
                               showPublic=null,
                               hidden=null,
                               flagged=null,
                               pinned=null,
                               popularity=null,
                               helpfulness=null,
                               deleted=null
                              }) => {
      updateQueryReply({user_id: opId,
                       post_id: replyId,
                       query_id: queryId,
                       post_text: opText,
                       show_public: showPublic,
                       hidden: hidden,
                       flagged: flagged,
                       pinned: pinned,
                       popularity: popularity,
                       helpulness: helpfulness,
                       deleted: deleted
                       })
      .then(myresponse => {
        _updateReplyInState(myresponse, myScopes);
      });
    }

    const updateCommentAction = ({opId=null,
                                  commentId=null,
                                  replyId=null,
                                  queryId=null,
                                  opText=null,
                                  showPublic=null,
                                  hidden=null,
                                  flagged=null,
                                  pinned=null,
                                  popularity=null,
                                  helpfulness=null,
                                  deleted=null
                                  }) => {
      updateReplyComment({user_id: opId,
                         comment_id: commentId,
                         post_id: replyId,
                         bug_id: queryId,
                         comment_text: opText,
                         showPublic: showPublic,
                         deleted: deleted,
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
                updateQueryAction={updateQueryAction}
                newReplyAction={newReplyAction}
                updateReplyAction={updateReplyAction}
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