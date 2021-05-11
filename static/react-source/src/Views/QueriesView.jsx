import React, { useContext, useState, useEffect } from "react";
import { Alert,
         Badge,
         Button,
         Col,
         Collapse,
         Form,
         FormControl,
         FormLabel,
         OverlayTrigger,
         Row,
         Spinner,
         Table,
         Tooltip,
} from "react-bootstrap";
import { useLocation,
         useParams
} from "react-router-dom";
import { SwitchTransition, CSSTransition } from "react-transition-group";
import marked from "marked";
import DOMPurify from 'dompurify';
import TextareaAutosize from 'react-textarea-autosize';

import UserProvider, { UserContext } from "../UserContext/UserProvider";
import { getQueries,
         addQuery,
         updateQuery,
         addQueryReply,
         updateQueryReply,
         addReplyComment,
         updateReplyComment,
         updateReadStatus
 } from "../Services/stepFetchService";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { findIndex } from "core-js/es/array";
import { readableDateAndTime } from "../Services/dateTimeService";
import Collapsible from '../Components/Collapsible';


const roles = {instructors: "chalkboard-teacher",
               administrators: "hard-hat",
               students: "graduation-cap"
               }

const RoleIcon = ({icon}) => {
  return ( <OverlayTrigger placement="top"
             className={`role-icon-${icon}`}
             overlay={
               <Tooltip id={`tooltip-role-${icon}`}>{icon.slice(0, -1)}</Tooltip>
             }
           >
             <FontAwesomeIcon icon={roles[icon]} />
             {/* <span>{icon}</span> */}
           </OverlayTrigger>
  )
}

const AdderButton = ({level, showAdderValue, showAdderAction, label, icon}) => {
  return (
    <span className={`adder-button-container`}>
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

const ControlRow = ({userId, opId, level, classId, icon, showAdderValue,
                     showAdderAction=null,
                     showEditorAction, updateAction, defaultUpdateArgs,
                     userRoles, instructing, showPublic,
                     flagged, pinned, popularity, helpfulness, userLoggedIn
                    }) => {
  const labelLevel = level === "query" ? "reply" : "comment";
  let myPop = Array.isArray(popularity) ? popularity : [];
  let myHelp = Array.isArray(helpfulness) ? helpfulness : [];
  // console.log(`logged in (control): ${userLoggedIn}`);
  return(
    <div className={`control-row control-row-${level}`}>
      { level !== "comment" && (
        !!userLoggedIn ?
        <AdderButton level={level}
          showAdderValue={showAdderValue}
          showAdderAction={showAdderAction}
          label={`Add your ${labelLevel}`}
          icon={icon}
        />
        :
        <span className={`control-row-login-msg`}>Log in to add your {labelLevel}</span>
        )
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
          onClick={e => {
            if (myPop.includes(userId)) {
              const i = myPop.indexOf(userId);
              myPop.splice(i, 1);
            } else {
              myPop.push(userId);
            }
            updateAction({...defaultUpdateArgs, popularity: myPop, event: e})
          }}
        >
          <FontAwesomeIcon icon="thumbs-up" /> {myPop.length}
        </Button>
      }
      {((userRoles.includes("administrators") || userRoles.includes("instructors")) && !!classId && instructing.find(c => c.id===classId)) &&
        <Button variant="outline-secondary"
          onClick={e =>
            updateAction({...defaultUpdateArgs, pinned: !pinned, event: e})
          }
        >
          <FontAwesomeIcon icon="thumbtack" />
        </Button>
      }
      {(userRoles.includes("administrators") || userRoles.includes("instructors")) &&
        <Button variant="outline-secondary"
          onClick={e => {
            if (myHelp.includes(userId)) {
              const i = myHelp.indexOf(userId);
              myHelp.splice(i, 1);
            } else {
              myHelp.push(userId);
            }
            updateAction({...defaultUpdateArgs, helpfulness: myHelp, event: e})
          }}
        >
          <FontAwesomeIcon icon="lightbulb" />
          {myHelp.length}
        </Button>
      }
    </div>
  )
}

const UpdateForm = ({level, idArgs, updateAction, updateField="opText",
                     currentText, setEditingAction,
                     autosize=true, optionList=null,
                     submitButton=true, labels=false, inline=false
                    }) => {
  const [myText, setMyText] = useState();
  const idString = Object.values(idArgs).join("-");
  const FormComponent = !!autosize ? TextareaAutosize : FormControl;
  // const [changing, setChanging] = useState(false);
  const sendUpdate = e => {
    e.preventDefault();
    updateAction({...idArgs,
      [updateField]: updateField==="score" ? parseFloat(myText) : myText});
    // console.log(`firing with myText: ${myText}`);
    setEditingAction(false);
  }
  useEffect(() => {
    if ( !!optionList && !!myText ) {
      // console.log(`myText: ${myText}`);
      sendUpdate(new Event('dummy'));
    }
  }, [myText, optionList]);

  return (
    <Form id={`update-${level}-${updateField}-form-${idString}`}
      className={`update-${level}-${updateField}-form update-form`}
      inline={inline}
    >
        <Form.Group controlId={`update-${level}-${updateField}-input-${idString}`}>
          {!!labels && <FormLabel>{updateField}</FormLabel>}
          <FormComponent
            as={!autosize ? (!!optionList ? "select" : "input") : undefined }
            defaultValue={!optionList ? currentText : parseInt(currentText) }
            onChange={e => setMyText(e.target.value)}
            onSubmit={sendUpdate}
            size="sm"
          >
            {!!optionList ?
              optionList.map((label, index) =>
                <option value={index} key={label}
                  // selected={index===parseInt(currentText) ? "selected" : false}
                >
                  {label.replace("_", " ")}
                </option>)
              : null
            }
          </FormComponent>
        </Form.Group>
        {!!submitButton &&
          <Button variant="primary"
            type="submit"
            onClick={e => sendUpdate(e)}
          >Update {level}</Button>
        }
    </Form>
  )
}

const NewQueryForm = ({answer, score, action, nonStep, singleStep}) => {
  const [queryText, setQueryText] = useState(" ");
  const [showPublic, setShowPublic] = useState(true);
  const [showForm, setShowForm] = useState(false);
  return (
    <React.Fragment>
    <Button variant="outline-success"
      onClick={() => setShowForm(!showForm)}
      aria-controls={`add-query-form`}
      aria-expanded={showForm}
      className="add-query-form-toggle"
    >
      <FontAwesomeIcon icon="plus" />
      {"Ask a new question or make a comment!"}
    </Button>
    <Collapse in={showForm}>
      <Form
        onSubmit={(event) => action(queryText, showPublic, event)}
        className="add-query-form"
      >
        {(!nonStep && !!singleStep) &&
          <Form.Group controlId="newQueryFormAnswer"
            className="alert alert-info"
          >
            {!!answer && answer !== "null" ?
              <React.Fragment>
                <Form.Label>You said</Form.Label>
                <Alert variant="light">{answer}</Alert>
                <Form.Label>and that was counted for {score} {score===1 ? "point" : (score===0 ? "points" : "of a point")}</Form.Label>
              </React.Fragment>
            :
              <Form.Label>You haven't answered this question yet</Form.Label>
            }
          </Form.Group>
        }
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
    </Collapse>
    </React.Fragment>
  );
}

const AddChildForm = ({level, classId, queryId, replyId=null,
                       addChildAction, setShowAdder
                      }) => {
  // FIXME: Handling legacy data here
  if ( level==="reply" && replyId===undefined ) { replyId="null" };
  const [childText, setChildText] = useState("");
  const [isPrivate, setIsPrivate] = useState(false);
  const uid = [classId, queryId, replyId].join("_");
  const createChild = e => {
    e.preventDefault();
    addChildAction({replyId: replyId, queryId: queryId,
                    opText: childText,
                    showPublic: !isPrivate
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
                     updateReplyAction, updateCommentAction, updateQueryAction, setReadStatusAction,
                     viewingAsAdmin, viewingAsInstructor,
                     queryId, opId, opNameFirst, opNameLast, opRole,
                     dateSubmitted, dateUpdated, opText,
                     hidden, showPublic, flagged, deleted,
                     popularity, helpfulness, pinned, read,
                     classId=null, replyId=null, commentId=null,
                     queryStatus=null, opResponseText=null, stepPrompt=null,
                     sampleAnswers=null,
                     queryStep=null, queryPath=null,
                     score=null, adjustedScore=null,
                     children=null, threadIndex=0
                    }) => {
  console.log('starting display row');
  const myRoles = !!opRole && opRole != null ?
    opRole.map(r => `${r}`).join(" ") : "";
  // console.log(`DisplayRow: read: ${read}`);
  const readClass = read===true ? "read" : (read===false ? "unread" : "");
  const {user, } = useContext(UserContext);
  const [ showAdder, setShowAdder ] = useState(false);
  const [ editing, setEditing ] = useState(false);
  const [ isPublic, setIsPublic ] = useState(showPublic);
  const [ activeScore, ] =
    useState(adjustedScore!=null ? adjustedScore : score)
  const showEditingForm = (e) => {
    e.preventDefault();
    setEditing(true);
  }

  let SampleList;
  if ( !!sampleAnswers ) {
    let sampleAnswerList = sampleAnswers.split("|");
    SampleList = <ul>{sampleAnswerList.map(a => <li key={a}>{a}</li>)}</ul>
  }
  const uid = [classId, queryId, replyId, commentId].join('_');
  const levels = ["query", "reply", "comment"];
  const childLevel = levels[levels.indexOf(level) + 1];
  // console.log(`query ${uid}`);
  // console.log(`opId: ${opId}`);
  // console.log(`score: ${score}`);
  // console.log(`adjusted_score: ${adjustedScore}`);
  const iconSize = level==="query" ? "3x" : "1x";
  const queryStatusList = ["",
                           "confirmed",
                           "fixed",
                           "not_a_bug",
                           "duplicate",
                           "awaiting_review",
                           "allowance_given",
                           "question_answered"];
  const queryStatusIcons = {placeholder: "",
                           confirmed: "exclamation-circle",
                           fixed: "thumbs-up",
                           not_a_bug: "circle",
                           duplicate: "copy",
                           awaiting_review: "question-circle",
                           allowance_given: "hand-holding-heart",
                           question_answered: "check-circle"};
  const queryStatusVariants = {placeholder: "",
                               confirmed: "success",
                               fixed: "success",
                               not_a_bug: "warning",
                               duplicate: "warning",
                               awaiting_review: "secondary",
                               allowance_given: "warning",
                               question_answered: "info"};
  const updateArgs = {query: {pathId: queryPath, stepId: queryStep,
                              opId: opId, userId: user.userId, queryId: queryId
                             },
                      reply: {opId: opId, userId: user.userId, replyId: replyId,
                              queryId: queryId},
                      comment: {opId: opId, userId: user.userId,
                                commentId: commentId,
                                replyId: replyId, queryId: queryId}
  };
  const idArgs = updateArgs[level];  // for building unique keys
  idArgs['classId'] = classId;
  const updateThisAction = {query: updateQueryAction,
                            reply: updateReplyAction,
                            comment: updateCommentAction
  };
  const addChildAction = {query: newReplyAction,
                          reply: newCommentAction,
                          comment: null
  };
  const togglePublic = () => {
    updateThisAction[level]({showPublic: !isPublic, ...updateArgs[level]});
    setIsPublic(!isPublic);
  };
  const toggleRead = () => {
    let myIds = {query: queryId,
                 reply: replyId,
                 comment: commentId}
    setReadStatusAction({postLevel: level,
                         postId: myIds[level],
                         userId: user.userId,
                         readStatus: !read});
  }

  return (
    <li key={`${uid}-display-row`}
      className={`${level}-display-row`}
    >
      <Row className={`${level}-display-wrapper display-wrapper ${readClass} ${myRoles}`} >
        <Col xs={3} className={`${level}-display-op display-op`}>
          <span className={`${level}-display-op-name display-op-name`}>
            {`${opNameFirst} ${opNameLast}`}
          </span><br />
          {level!=="comment" ?
            <FontAwesomeIcon icon="user-circle" size={iconSize}
              className="display-op-avatar"
            /> : ""
          }
          {!!opRole && opRole.map(r =>
            <RoleIcon className={`role-icon ${r}`}
              key={`${uid}-${r}`} icon={r}
            />
          )}
          <br />
          {/* {level==="query" &&
            <React.Fragment>
            <span className={`${level}-display-op-date display-op-date`}>
              {readableDateAndTime(dateSubmitted)}
            </span><br />
            </React.Fragment>
          } */}
          {!!queryStatus ? (
            (!!viewingAsAdmin || !!viewingAsInstructor) ?
              <UpdateForm level={level}
                idArgs={idArgs}
                updateAction={updateThisAction[level]}
                updateField="queryStatus"
                currentText={queryStatus}
                // currentText={DOMPurify.sanitize(queryStatus)}
                setEditingAction={setEditing}
                autosize={false}
                optionList={queryStatusList}
                submitButton={false}
              />
            : <Badge pill
                variant={queryStatusVariants[queryStatusList[queryStatus]]}
                className={`${level}-display-op-status display-op-status`}
              >
                <FontAwesomeIcon size="sm"
                  icon={queryStatusIcons[queryStatusList[queryStatus]]}
                />
              {queryStatusList[queryStatus].replace("_", " ")}
              </Badge>
            )
            : ""
          }
          {level==="query" &&
           (user.userId===opId || !!viewingAsAdmin || !!viewingAsInstructor) &&
            score !== null &&
            <div className={`${level}-display-op-privateinfo display-op-privateinfo instructor-view`}>
              {(!!viewingAsAdmin || !!viewingAsInstructor) ?
                <span className={`${level}-display-op-points display-op-points`}>
                  <UpdateForm level={level}
                    idArgs={idArgs}
                    updateAction={updateThisAction[level]}
                    updateField="score"
                    labels={true}
                    currentText={!activeScore==="0" ? activeScore : activeScore}
                    // currentText={!activeScore==="0" ? DOMPurify.sanitize(activeScore) : activeScore}
                    setEditingAction={setEditing}
                    autosize={false}
                    inline={true}
                    // submitButton={false}
                  />
                  {!!adjustedScore && `(previously ${score})`}
                </span>
              :
                <span className={`${level}-display-op-points display-op-points badge`}>
                  {!!adjustedScore ? `${adjustedScore} point(s) (was ${score})`: `${score} point(s)`}
                </span>
              }
              <span className={`${level}-display-op-privatemessage display-op-privatemessage`}>
                <FontAwesomeIcon icon="eye-slash" />
                this score is private
              </span>
            </div>
          }
          {user.userId===opId ?
            <Button className={`${level}-display-op-public display-op-public`}
              onClick={togglePublic}
              variant="link"
            >
                <FontAwesomeIcon icon={!!isPublic ? "eye" : "eye-slash"}
                  size="1x" />
                {!!isPublic ? "public" : "private"}
            </Button>
            :
            <span className={`${level}-display-op-public display-op-public`} >
                <FontAwesomeIcon icon={!!isPublic ? "eye" : "eye-slash"}
                  size="1x" />
                {!!isPublic ? "public" : "private"}
            </span>
          }
        </Col>
        <Col xs={9}
          className={`${level}-display-body-wrapper ${readClass}  display-body-wrapper`}
        >
          {!!user.userLoggedIn &&
            <Button onClick={toggleRead}
              size="sm" variant="link" className="read-link"
            >
              <FontAwesomeIcon size="sm"
                icon={!!read ? "envelope-open" : "envelope" } />
              Mark as {!!read ? `unread` : `read`}
            </Button>
          }
          <div className={`${level}-display-inner-wrapper ${readClass} display-inner-wrapper`}>
          {!!queryStep &&
            <React.Fragment>
              The step asked...
              <p className="query-display-prompt"
                // FIXME: do I need sanitize in all the places it's commented out?
                // dangerouslySetInnerHTML={{
                //   __html: !!stepPrompt ? DOMPurify.sanitize(marked(stepPrompt)) : ""}}
                dangerouslySetInnerHTML={{
                  __html: !!stepPrompt ? marked(stepPrompt) : ""}}
              />
            </React.Fragment>
          }
          {!!opResponseText &&
            <React.Fragment>
              And I responded...
              <p className="query-display-response"
                // dangerouslySetInnerHTML={{
                  // __html: !!opResponseText ? DOMPurify.sanitize(marked(opResponseText)) : ""}}
                dangerouslySetInnerHTML={{
                  __html: !!opResponseText ? marked(opResponseText) : ""}}
              />
            </React.Fragment>
          }
          {!!sampleAnswers &&
            <React.Fragment>
              Good answers could include these...
              <div className="query-display-samples">{SampleList}</div>
            </React.Fragment>
          }
          <SwitchTransition>
            <CSSTransition
              key={!!editing ? `${level}-display-body-editor` : `${level}-display-body-text`}
              classNames={`${level}-display-body-text`}
              unmountOnExit={false}
              timeout={200}
            >
              {!!editing ?
                <div className={`${level}-display-body-text display-body-text`}>
                  <UpdateForm level={level}
                    idArgs={idArgs}
                    updateAction={updateThisAction[level]}
                    // currentText={opText ? DOMPurify.sanitize(opText) : ""}
                    currentText={opText ? opText : ""}
                    setEditingAction={setEditing}
                  />
                </div>
                :
                <React.Fragment>
                <div className={`${level}-display-body-text display-body-text`}>
                  <p className={`${level}-display-op-question display-op-question`}
                    // dangerouslySetInnerHTML={{
                    //   __html: opText ? DOMPurify.sanitize(marked(opText)) : ""}}
                    dangerouslySetInnerHTML={{
                      __html: opText ? marked(opText) : ""}}
                  />
                </div>
                <span className={`${level}-display-date display-date`}>
                  <FontAwesomeIcon icon="clock" size="sm" />{readableDateAndTime(dateSubmitted)}
                </span>
                {!!dateUpdated && (dateUpdated !== dateSubmitted) &&
                  <span className={`${level}-display-edited-date display-edited-date`}>
                    <FontAwesomeIcon icon="clock" size="sm" />
                    last edited {readableDateAndTime(dateUpdated)}
                  </span>
                }
                {!!queryStep && (!!viewingAsAdmin || !!viewingAsInstructor) &&
                  <span className={`${level}-display-query-step dispay-query-step`}>
                    <FontAwesomeIcon icon="shoe-prints" size="sm" />
                    for step {queryStep} in path {queryPath}
                  </span>
                }
                <ControlRow
                  userId={user.userId}
                  opId={opId}
                  level={level}
                  classId={classId}
                  icon={level==="comment" ? null : childLevel}
                  showAdderValue={level==="comment" ? null : showAdder}
                  showAdderAction={(level==="comment" || !user.userLoggedIn) ? null : setShowAdder}
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
                  userLoggedIn={user.userLoggedIn}
                />
                </React.Fragment>
              }
              </CSSTransition>
              </SwitchTransition>
              </div>
            </Col>
          </Row>

          {level !== "comment" && !!user.userLoggedIn &&
            <span className={`${level}-display-add-child display-add-child`}>
              {/* <a className="label"
                onClick={() => setShowAdder(!showAdder)}
                aria-controls={`${uid}-add-child-form-wrapper`}
                aria-expanded={showAdder}
              >
                <FontAwesomeIcon icon={childLevel} />{childLevel.toUpperCase()}
              </a> */}
              <Collapse in={showAdder}>
                <div className={`${uid}-add-child-form-wrapper add-child-form-wrapper`}>
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

          <ul className={`${level}-display-children display-children`}>
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
              setReadStatusAction={setReadStatusAction}
            />)}
          </ul>

      </li>
    )
}


const QueriesList = ({queryArray, updateQueryAction, newReplyAction,
                       newCommentAction, updateReplyAction,
                       updateCommentAction, setReadStatusAction, viewingAsAdmin, scope, byClass, viewGroup}) => {
  const { user, } = useContext(UserContext);
  console.log("in QueriesList:");
  console.log(`byClass: ${byClass}`);
  console.log("queryArray");
  console.log(queryArray);
  const instructorState = scope==="students" ?
    user.instructing.find(c => c.id === viewGroup) : false;


  return (<>
    {!!byClass && !!queryArray && <Badge>{queryArray.length}</Badge>}
    {( !!queryArray && queryArray!==[] ) ?
          <ul className="query-list">
            {queryArray.map(
              q => <DisplayRow key={`query-row-${q.queryId}`}
                      level="query"
                      updateQueryAction={updateQueryAction}
                      newReplyAction={newReplyAction}
                      newCommentAction={newCommentAction}
                      updateReplyAction={updateReplyAction}
                      updateCommentAction={updateCommentAction}
                      setReadStatusAction={setReadStatusAction}
                      viewingAsAdmin={viewingAsAdmin}
                      viewingAsInstructor={instructorState}
                      classId={!!byClass ? viewGroup : 0}
                      {...q}
                    />
            )}
          </ul>
    :
    <ul />
    }
  </>)
}

const ScopeView = ({scope, nonStep, singleStep,
                    newQueryAction,
                    updateQueryAction,
                    newReplyAction,
                    updateReplyAction,
                    newCommentAction,
                    updateCommentAction,
                    setReadStatusAction,
                    viewingAsAdmin,
                    viewCourse,
                    viewStudents,
                    courseChangeFunctions, list}) => {

  const {user, } = useContext(UserContext);
  console.log("in ScopeView:");
  console.log(`viewCourse: ${viewCourse}`);
  console.log(`viewStudents: ${viewStudents}`);
  console.log(`list:`);
  console.log(list);
  const byClass = ["class", "students"].includes(scope);
  const viewGroup = scope==="class" ? viewCourse :
    (scope==="students" ? viewStudents : null);

  useEffect(() => {
    if (!!byClass && !viewGroup) {
      courseChangeFunctions[scope](list[0].classId);
    }
  }, [byClass, viewGroup, scope, list]);


  let queryArray = list;
  if (!!byClass) {
    const myClass = list.find(c => c.classId===parseInt(viewGroup));
    queryArray = !!myClass ? myClass.queries : [];
  }

  return (
    <div className="queries-view-pane" key={scope}>
      {scope==='user' ? (
        !!user.userLoggedIn ? (
          (nonStep===false && singleStep===false) ?
            <Alert variant="warning" className="me-new-query-info">
              <p>{"Asking a question that's not about a specific path or step? Select 'General' at top."}</p>
              <p>To ask about a specific step you must be attempting that step when you submit your question.</p>
            </Alert>
          :
            <NewQueryForm
              answer={user.currentAnswer}
              score={user.currentScore}
              action={newQueryAction}
              nonStep={nonStep}
              singleStep={singleStep}
            />
        )
        : <span className="queries-view-login-message">
          Log in to ask a question or offer a comment.
        </span>
      )
      : ''}
      {['class', 'students'].includes(scope) ?
        <Form>
          <Form.Control
              id={`${scope}SelectorForm`}
              as="select"
              onChange={e => courseChangeFunctions[scope](e.target.value)}
          >
              {list.map( c =>
                  <option key={c.classId}
                    value={c.classId}
                  >
                    {`${c.institution}, ${c.year}, ${c.term}, ${c.section}, ${c.instructor}`}
                  </option>
              )}
          </Form.Control>
        </Form>
        :
        " "
      }
      <QueriesList
        queryArray={queryArray}
        updateQueryAction={updateQueryAction}
        newReplyAction={newReplyAction}
        updateReplyAction={updateReplyAction}
        newCommentAction={newCommentAction}
        updateCommentAction={updateCommentAction}
        setReadStatusAction={setReadStatusAction}
        viewingAsAdmin={viewingAsAdmin}
        viewCourse={viewCourse}
        viewStudents={viewStudents}
        viewGroup={viewGroup}
        byClass={byClass}
        scope={scope}
      />
    </div>
  )
}

const LoadingContent = () => {
  return (
    <Spinner animation="grow" variant="secondary"
      className="align-self-center map-spinner" />
  )
}

const ScopesFrame = ({viewScope,
                      nonStep,
                      singleStep,
                      viewingAsAdmin,
                      viewCourse,
                      viewStudents,
                      courseChangeFunctions,
                      userQueries,
                      userUnreadCount,
                      setUserQueries,
                      classQueries,
                      classTotalCount,
                      classUnreadCount,
                      setClassQueries,
                      setViewScope,
                      studentsQueries,
                      studentsTotalCount,
                      studentsUnreadCount,
                      setStudentsQueries,
                      otherQueries,
                      otherUnreadCount,
                      setOtherQueries,
                      newQueryAction,
                      updateQueryAction,
                      newReplyAction,
                      updateReplyAction,
                      newCommentAction,
                      updateCommentAction,
                      setReadStatusAction,
                      myScopes
                      }) => {

  const {user,} = useContext(UserContext);

  return (
    <React.Fragment>
      <div className="queries-view-changer-wrapper">
        <Button
          className={`queries-view-changer ${viewScope==='user' ? "in" : "out"}`}
          variant="outline-secondary"
          onClick={() => setViewScope('user')}
        >
          <FontAwesomeIcon icon="user" />Me
          <Badge variant="secondary">{userQueries ? userQueries.length : "0"}</Badge>
          {!!userUnreadCount &&
            <Badge variant="success"><FontAwesomeIcon icon="envelope" size="sm" /> {userUnreadCount}</Badge>
          }
        </Button>
        {!!user.userLoggedIn && !!user.classInfo &&
        <Button
          className={`queries-view-changer ${viewScope==='class' ? "in" : "out"}`}
          variant="outline-secondary"
          onClick={() => setViewScope('class')}
        >
          <FontAwesomeIcon icon="users" />Classmates
          <Badge variant="secondary">{classTotalCount}</Badge>
          {!!classUnreadCount &&
            <Badge variant="success"><FontAwesomeIcon icon="envelope" size="sm" /> {classUnreadCount}</Badge>
          }
        </Button>
        }
        {!!user.userRoles.some(v => ["instructors", "administrators"].includes(v)) &&
          <Button
            className={`queries-view-changer ${viewScope==='students' ? "in" : "out"}`}
            variant="outline-secondary"
            onClick={() => setViewScope('students')}
          >
            <FontAwesomeIcon icon="users" />Students
            <Badge variant="secondary">{studentsTotalCount}</Badge>
            {!!studentsUnreadCount &&
              <Badge variant="success"><FontAwesomeIcon icon="envelope" size="sm" /> {studentsUnreadCount}</Badge>
            }
          </Button>
        }
        <Button
          className={`queries-view-changer ${viewScope==='public' ? "in" : "out"}`}
          variant="outline-secondary"
          onClick={() => setViewScope('public')}
        >
          <FontAwesomeIcon icon="globe-americas" />Others
          <Badge variant="secondary">{otherQueries ? otherQueries.length : "0"}</Badge>
          {!!otherUnreadCount &&
            <Badge variant="success"><FontAwesomeIcon icon="envelope" size="sm" /> {otherUnreadCount}</Badge>
          }
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
          <ScopeView
            scope={scope}
            nonStep={nonStep}
            singleStep={singleStep}
            newQueryAction={newQueryAction}
            updateQueryAction={updateQueryAction}
            newReplyAction={newReplyAction}
            updateReplyAction={updateReplyAction}
            newCommentAction={newCommentAction}
            updateCommentAction={updateCommentAction}
            setReadStatusAction={setReadStatusAction}
            viewingAsAdmin={viewingAsAdmin}
            viewCourse={viewCourse}
            viewStudents={viewStudents}
            courseChangeFunctions ={courseChangeFunctions}
            list={list}
          />

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
  )
}

const QueriesView = () => {

    const {user, } = useContext(UserContext);
    const [queries, setQueries] = useState(null);
    const [userQueries, setUserQueries] = useState(null);
    const [userUnreadCount, setUserUnreadCount] = useState(null);
    const [classQueries, setClassQueries] = useState(null);
    const [classTotalCount, setClassTotalCount] = useState(0);
    const [classUnreadCount, setClassUnreadCount] = useState(null);
    const [studentsQueries, setStudentsQueries] = useState(null);
    const [studentsTotalCount, setStudentsTotalCount] = useState(0);
    const [studentsUnreadCount, setStudentsUnreadCount] = useState(null);
    const [otherQueries, setOtherQueries] = useState(null);
    const [otherUnreadCount, setOtherUnreadCount] = useState(null);
    console.log("QueriesView top----------------------");
    console.log("otherQueries");
    console.log(otherQueries);
    console.log("userQueries");
    console.log(userQueries);
    console.log("classQueries");
    console.log(classQueries);
    console.log("studentsQueries");
    console.log(studentsQueries);

    const myScopes = [
      {scope: 'user',
       list: userQueries,
       action: setUserQueries},
      {scope: 'class',
       list: classQueries,
       action: setClassQueries},
      {scope: 'students',
       list: studentsQueries,
       action: setStudentsQueries},
      {scope: 'public',
       list: otherQueries,
       action: setOtherQueries}
    ];

    const [loading, setLoading] = useState(!queries ? true : false);

    const location = useLocation();
    const urlParams = useParams();
    const pathArray = location.pathname.split('/');
    const [onStep, setOnStep] = useState(pathArray[2]==="walk" &&
      !["map", undefined].includes(urlParams.walkPage) &&
      !!user.currentStep);

    const [singleStep, setSingleStep] = useState(!onStep ? false : true);
    const [nonStep, setNonStep] = useState(true);
    const [viewScope, setViewScope] = useState('public');
    const [viewCourse, setViewCourse] = useState();
    console.log('viewCourse');
    console.log(viewCourse);
    const [viewStudents, setViewStudents] = useState();
    console.log('viewStudents');
    console.log(viewStudents);
    const courseChangeFunctions = {class: setViewCourse,
                                  students: setViewStudents};
    const [filterUnanswered, setFilterUnanswered] = useState(false);
    const [filterUnread, setFilterUnread] = useState(false);
    const [viewingAsAdmin, ] = useState(
      user.userRoles.includes("administrators"));

    const setScopeSingleStep = () => {
      setNonStep(false);
      setSingleStep(true);
    }

    const setScopeAllSteps = () => {
            setNonStep(false);
            setSingleStep(false)
    }

    useEffect(() => {
      let amOnStep = pathArray[2]==="walk" &&
                      !["map", undefined].includes(urlParams.walkPage) &&
                      !!user.currentStep;
      setOnStep(amOnStep);
      if (!nonStep) {
        !!amOnStep ? setScopeSingleStep() : setScopeAllSteps();
      }
    }, [location]);

    const _formatCommentData = c => {
      return ({level: "comment",
               replyId: c.bug_post_comments.on_post,
               commentId: c.bug_post_comments.id,
               opId: c.bug_post_comments.commenter,
               opNameFirst: c.auth_user.first_name,
               opNameLast: c.auth_user.last_name,
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
               threadIndex: c.bug_post_comments.thread_index,
               read: c.read
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
               deleted: p.bug_posts.deleted,
               flagged: p.bug_posts.flagged,
               pinned: p.bug_posts.pinned,
               popularity: 0,
               helpfulness: 0,
               showPublic: p.bug_posts.public,
               threadIndex: p.bug_posts.thread_index,
               read: p.read,
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
          sampleAnswers: q.bugs.sample_answers,
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
          children: [],
          score: q.bugs.score,
          adjustedScore: q.bugs.adjusted_score,
          read: false
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
               sampleAnswers: q.bugs.sample_answers,
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
               score: q.bugs.score,
               adjustedScore: q.bugs.adjusted_score,
               read: q.read
              }
      )
    }

    const _formatClassData = ({id, institution, section, year, term, instructor, queries}) => {
      return ({classId: id,
               institution: institution,
               section: section,
               year: year,
               term: term,
               instructor: instructor,
               queries: queries.map(q => _formatQueryData(q))
              }
      )
    }


    // finds and updates an item in a list in state
    // DOES NOT create new query if specified doesn't exist
    // DOES create new post if specified doesn't exist
    // returns the modified version of the supplied query list
    // if the new query has deleted: true it is removed
    const _findAndUpdateItem = (mylist, newItem, itemLevel, queryId=0) => {
      // TODO: mark children read when marked read
      console.log("_findAndUpdateItem-------------------------------------");
      const dbTableFields = {'query': 'bugs',
                             'reply': 'bug_posts',
                             'comment': 'bug_post_comments'}
      const itemTableField = dbTableFields[itemLevel];
      const markingRead = !!newItem[itemTableField] ? false : true;
      const deleting = !!markingRead ? false
        : newItem[itemTableField].deleted;

      const myItemId = !!markingRead ? newItem.read_item_id
        : newItem[itemTableField].id;

      let myQueryId = myItemId;
      let myReplyId = 0;
      let myCommentId = 0;
      if ( itemLevel==='reply' ) {
        myQueryId = !!markingRead ? newItem.on_bug
          : newItem[itemTableField].on_bug;
        myReplyId = myItemId;
      } else if ( itemLevel ==='comment' ) {
        myQueryId = !!markingRead ? newItem.on_bug : queryId;
        myReplyId = !!markingRead ? newItem.on_bug_post : newItem[itemTableField].on_post;
        myCommentId = myItemId;
      }
      const queryIndex = mylist.findIndex(q => q.queryId===myQueryId);

      const _innerFindAndUpdate = (i_itemIndex, i_itemlist, formatAction, i_newItem
                            ) => {
        console.log("inner find and update..........");
        console.log(i_itemIndex);
        console.log(i_itemlist);
        console.log(`markingRead: ${markingRead}`);
        if ( !!markingRead ) {
          i_itemlist[i_itemIndex].read = i_newItem.read_status;
        } else if ( !!deleting ) {
          i_itemlist.splice(i_itemIndex, 1);
        } else {
          i_itemlist[i_itemIndex] = formatAction(i_newItem);
        }
        console.log("returning from inner:");
        console.log(i_itemlist);
        return i_itemlist
      }

      const _markChildrenRead = (i_mylist, myIndex) => {
        console.log("marking children read********");
        console.log(i_mylist);
        console.log(myIndex);
        let myReplyList = i_mylist[myIndex].children;
        for (let i=0; i<myReplyList.length; i++) {
          if ( myReplyList[i].read===false ) {
            console.log("marking item");
            console.log(i);
            myReplyList = _innerFindAndUpdate(i, myReplyList, _formatReplyData,
                                      {read_status: true})
            if ( myReplyList[i].hasOwnProperty('children') &&
                myReplyList[i].children !== undefined &&
                myReplyList[i].children.length>0 )
              {
              console.log("marking grandchildren read below========");
              let myCommentList = myReplyList[i].children;
              for (let x=0; x<myCommentList.length; x++) {
                if ( myCommentList[x].read===false ) {
                  console.log(myCommentList);
                  console.log(x);
                  myCommentList = _innerFindAndUpdate(x,
                    myCommentList, _formatCommentData, {read_status: true})
                  console.log("grandchild result");
                  console.log(myCommentList);
                }
              }
              myReplyList[i].children = myCommentList;
            }
            i_mylist[myIndex].children = myReplyList;
          }
        }
        return i_mylist;
      }

      if ( queryIndex > -1 ) {
        // update at query level
        if (itemLevel==='query') {
          mylist = _innerFindAndUpdate(queryIndex, mylist, _formatQueryData, newItem);
          if ( !!markingRead && newItem.read_status===true) {
            mylist = _markChildrenRead(mylist, queryIndex);
            console.log('returned from marking children read======');
            console.log(mylist);
          }
        } else {
          // update either reply or comment level...
          let myReplyList = mylist[queryIndex].children;
          const replyIndex = myReplyList.findIndex(p => p.replyId===myReplyId);
          if (replyIndex > -1) {
            if ( itemLevel==='reply') {
              // update at reply level
              mylist[queryIndex].children = _innerFindAndUpdate(replyIndex,
                                                         myReplyList,
                                                         _formatReplyData, newItem);
              if ( !!markingRead && newItem.read_status===false ) {
                mylist = _innerFindAndUpdate(queryIndex, mylist, _formatQueryData,
                                      {read_status: false});
              } else if ( !!markingRead && newItem.read_status===true ) {
                mylist[queryIndex].children = _markChildrenRead(
                  mylist[queryIndex].children, replyIndex);
                console.log('returned from marking children read======');
                console.log(mylist[queryIndex].children);
              }
            } else {
              // update at comment level
              const commentIndex = mylist[queryIndex].children[replyIndex]
                .children.findIndex(p => p.commentId===myCommentId);
              if ( commentIndex > -1 ) {
                let myCommentList = mylist[queryIndex].children[replyIndex]
                  .children;
                mylist[queryIndex].children[replyIndex]
                  .children = _innerFindAndUpdate(commentIndex, myCommentList,
                                           _formatCommentData, newItem);

                if ( !!markingRead && newItem.read_status===false ) {
                  mylist = _innerFindAndUpdate(queryIndex, mylist, _formatQueryData,
                                        {read_status: false});
                  mylist[queryIndex].children = _innerFindAndUpdate(replyIndex,
                    myReplyList, _formatReplyData, {read_status: false});
                }
              } else {
                // or create comment
                mylist[queryIndex].children[replyIndex].children
                  .push(_formatCommentData(newItem));
              }
            }
          } else {
            // or create reply
            mylist[queryIndex].children.push(_formatReplyData(newItem));
          }
        }
      }
      return mylist;
    }

    // Non-returning function to properly update state with one post
    // expects myresponse to have keys "auth_user", "bugs", and "posts"
    const _updateItemInState = (newItem, itemLevel, myscopes, queryId) => {

      const extraArg = itemLevel==="comment" ? [queryId] : [];

      const innerUpdate = (qList, updateAction) => {
        return new Promise((resolve, reject) => {
          console.log("innerUpdate: qList");
          console.log(qList);
          let newQList = [];
          if ( qList.length && !!qList[0].classId ) {
            newQList = qList.map(myClass => {
              myClass.queries = _findAndUpdateItem(myClass.queries, newItem,
                                                   itemLevel, ...extraArg);
              return myClass;
            })
          } else if ( qList.length ) {
            console.log(`updating ${itemLevel}`);
            newQList = _findAndUpdateItem(qList, newItem, itemLevel,
                                          ...extraArg);
            // console.log('inner_update*********************');
            // console.log(newQList);
          }
          console.log("innerUpdate: newQList");
          console.log(newQList);
          console.log(`sending to:`);
          console.log(updateAction);
          updateAction(newQList);
          resolve(newQList);
        })
      }

      for (let i=0; i < myscopes.length; i++) {
        let scopeLabel = myscopes[i].scope!=="public" ? myscopes[i].scope
          : "other";
        let levelLabel = itemLevel==="query" ? "querie" : itemLevel;
        scopeLabel = `${scopeLabel}_${levelLabel}s`;
        console.log('scope');
        console.log(myscopes[i]);
        let myPromise = innerUpdate([ ...myscopes[i].list ],
                                    myscopes[i].action);
        myPromise.then(
          result => {
            console.log(`**scope ${scopeLabel}`);
            console.log('**result');
            console.log(result);
            _setCounts({[scopeLabel]: result});
          },
          result => {
            console.log('I broke!!!!!!!!!!!');
            console.log(result);
            console.log(scopeLabel);
          }
        )
      }
    }

    // expects four lists of queries in internal formatted form (not raw server response)
    const _setCounts = ({user_queries=null, other_queries=null,
                         class_queries=null, students_queries=null}) => {

      if ( !!user_queries ) {
        setUserUnreadCount(
          user_queries.filter(q => q.read===false).length
        );
      }
      if ( !!other_queries ) {
        setOtherUnreadCount(
          other_queries.filter(q => q.read===false).length
        );
      }

      if ( !!class_queries ) {
        // console.log('---class_queries');
        // console.log(class_queries);
        let classUnreadList = [];
        let classTotalList = [];
        class_queries.forEach(myClass => {
          let unreadInClass = myClass.queries.filter(q =>
            q.read===false && classUnreadList.indexOf(q.queryId)===-1
          );
          classUnreadList = classUnreadList.concat(unreadInClass.map(i => i.queryId));
          classTotalList = classTotalList.concat(myClass.queries
            .filter(q => classTotalList.indexOf(q.queryId)===-1)
            .map(i => i.queryId)
          );
          // console.log(classTotalList);
          // console.log(classUnreadList);
        });

        setClassUnreadCount(classUnreadList.length);
        setClassTotalCount(classTotalList.length);
      }

      if ( !!students_queries ) {
        // console.log('---students_queries');
        // console.log(students_queries);
        let studentsUnreadList = [];
        let studentsTotalList = [];
        students_queries.forEach(myCourse => {
          let unreadInCourse = myCourse.queries.filter(q =>
            q.read===false && studentsUnreadList.indexOf(q.queryId)===-1
          );
          studentsUnreadList = studentsUnreadList.concat(unreadInCourse.map(i => i.queryId));
          studentsTotalList = studentsTotalList.concat(myCourse.queries
            .filter(q => studentsTotalList.indexOf(q.queryId)===-1)
            .map(i => i.queryId)
          );
        });
        // console.log(studentsTotalList);
        // console.log(studentsUnreadList);
        setStudentsUnreadCount(studentsUnreadList.length);
        setStudentsTotalCount(studentsTotalList.length);
      }
    }

    const fetchAction = () => {
      setLoading(true);
      getQueries({step_id: !!singleStep && !!onStep ? user.currentStep : 0,
                  user_id: user.userId,
                  nonstep: nonStep,
                  unread: filterUnread,
                  unanswered: filterUnanswered,
                  pagesize: 20,
                  page: 0,
                  orderby: "modified_on"
                })
      .then(queryfetch => {
        setQueries(queryfetch);
        const formattedUserQueries = queryfetch.user_queries.map(
          q => _formatQueryData(q)
        );
        setUserQueries(formattedUserQueries);
        const formattedClassQueries = queryfetch.class_queries.map(
          c => _formatClassData(c)
        );
        setClassQueries(formattedClassQueries);
        const formattedStudentsQueries = queryfetch.course_queries.map(
          s => _formatClassData(s)
        );
        setStudentsQueries(formattedStudentsQueries);
        const formattedOtherQueries = queryfetch.other_queries
          .slice(0, 20).map(q => _formatQueryData(q));
        setOtherQueries(formattedOtherQueries);
        _setCounts({user_queries: formattedUserQueries,
                    other_queries: formattedOtherQueries,
                    class_queries: formattedClassQueries,
                    students_queries: formattedStudentsQueries});
        setLoading(false);
      });
    }

    useEffect(() => fetchAction(),
              [user.currentStep, onStep, singleStep, nonStep, filterUnread, filterUnanswered]);

    const newQueryAction = (myComment, showPublic, event) => {
      event.preventDefault();
      const myscore = !['null', undefined].includes(user.currentScore) ?
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
        // console.log('QueriesView: after newQueryAction======');
        // console.log(myresponse.read_status_updates);
        setUserQueries(myresponse.queries.map(
          q => _formatQueryData(q)
        ));
      });
    }

    const setReadStatusAction = ({postLevel,
                                  userId,
                                  postId,
                                  readStatus}) => {
      updateReadStatus({postLevel: postLevel,
                        userId: userId,
                        postId: postId,
                        readStatus: readStatus})
      .then(myresponse => {
          if (myresponse.status_code===200) {
            _updateItemInState(myresponse.result, postLevel, myScopes, 0);
          } else {
            console.log(myresponse);
          }
      });
    }

    const newReplyAction = ({replyId=null,
                             queryId=null,
                             opText=null,
                             showPublic=true
                             }) => {
      addQueryReply({user_id: user.userId,
                     query_id: queryId,
                     post_text: opText,
                     show_public: showPublic
                     })
      .then(myresponse => {
        _updateItemInState(myresponse.new_post, 'reply', myScopes, 0);
      });
    }

    const newCommentAction = ({replyId=null,
                               queryId=null,
                               opText=null,
                               showPublic=true,
                              }) => {
      addReplyComment({user_id: user.userId,
                      post_id: replyId,
                      query_id: queryId,
                      comment_text: opText,
                      show_public: showPublic
                      })
      .then(myresponse => {
        _updateItemInState(myresponse.new_comment, "comment", myScopes, queryId);
      });
    }

    const updateQueryAction = ({userId=null,
                                queryId=null,
                                opText=null,
                                showPublic=null,
                                flagged=null,
                                pinned=null,
                                popularity=null,
                                helpfulness=null,
                                deleted=null,
                                score=null,
                                queryStatus=null
                                // hidden=null,
                               }) => {
      updateQuery({user_id: userId,
                   query_id: queryId,
                   query_text: opText,
                   show_public: showPublic,
                   //  hidden: hidden,
                   flagged: flagged,
                   pinned: pinned,
                   popularity: popularity,
                   helpfulness: helpfulness,
                   deleted: deleted,
                   score: score,
                   queryStatus: queryStatus
                   })
      .then(myresponse => {
        _updateItemInState(myresponse.new_item, "query", myScopes, 0);
      });
    }

    const updateReplyAction = ({userId,
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

      updateQueryReply({user_id: userId,
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
        _updateItemInState(myresponse.new_post, "reply", myScopes, 0);
      });
    }

    const updateCommentAction = ({userId=null,
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
      updateReplyComment({user_id: userId,
                         post_id: replyId,
                         comment_id: commentId,
                         comment_text: opText,
                         show_public: showPublic,
                         deleted: deleted,
                         hidden: hidden,
                         flagged: flagged,
                         pinned: pinned,
                         popularity: popularity,
                         helpfulness: helpfulness
                        })
      .then(myresponse => {
        _updateItemInState(myresponse.new_comment, "comment", myScopes, queryId);
      });
    }

    return(
      <Row key="QueriesView" className="queriesview-component panel-view">
        <Col>
          <h2>Questions about
            {!!onStep &&
              <Button
                className={!!onStep && !!singleStep && !nonStep ? "active" : ""}
                onClick={() => setScopeSingleStep()}
              >
                This Step
              </Button>
            }
            <Button
              className={!singleStep && !nonStep ? "active" : ""}
              onClick={() => setScopeAllSteps()}
            >
              All Steps
            </Button>
            <Button
              className={!!nonStep ? "active" : ""}
              onClick={() => setNonStep(true)}
            >
              General
            </Button>
          </h2>

          <Form id={`filterUnansweredCheckbox`}
            inline
            className="query-filter-form"
          >
            <Form.Check inline label="Only unread"
              id="only-unread-checkbox"
              type="switch"
              // defaultValue={filterUnread}
              isSelected={filterUnread}
              onChange={e => setFilterUnread(!filterUnread)}
              />
            <Form.Check inline label="Only unanswered"
              id="only-unanswered-checkbox"
              type="switch"
              // defaultValue={filterUnanswered}
              isSelected={filterUnanswered}
              onChange={e => setFilterUnanswered(!filterUnanswered)}
              />
          </Form>

          <div className="queries-view-wrapper">
            <SwitchTransition>
              <CSSTransition
                key={!!queries ? "loaded" : "loading"}
                timeout={250}
                unmountOnExit
                mountOnEnter
              >
                { !!loading ?
                  <LoadingContent />
                  :
                  <ScopesFrame
                      viewScope={viewScope}
                      nonStep={nonStep}
                      singleStep={singleStep}
                      viewingAsAdmin={viewingAsAdmin}
                      viewCourse={viewCourse}
                      viewStudents={viewStudents}
                      courseChangeFunctions={courseChangeFunctions}
                      userQueries={userQueries}
                      userUnreadCount={userUnreadCount}
                      setUserQueries={setUserQueries}
                      classQueries={classQueries}
                      classTotalCount={classTotalCount}
                      classUnreadCount={classUnreadCount}
                      setClassQueries={setClassQueries}
                      setViewScope={setViewScope}
                      studentsQueries={studentsQueries}
                      studentsTotalCount={studentsTotalCount}
                      studentsUnreadCount={studentsUnreadCount}
                      setStudentsQueries={setStudentsQueries}
                      otherQueries={otherQueries}
                      otherUnreadCount={otherUnreadCount}
                      setOtherQueries={setOtherQueries}
                      newQueryAction={newQueryAction}
                      updateQueryAction={updateQueryAction}
                      newReplyAction={newReplyAction}
                      updateReplyAction={updateReplyAction}
                      newCommentAction={newCommentAction}
                      updateCommentAction={updateCommentAction}
                      setReadStatusAction={setReadStatusAction}
                      myScopes={myScopes}
                  />
                }
              </CSSTransition>
            </SwitchTransition>
          </div>
        </Col>
      </Row>
    )
}

export default QueriesView;