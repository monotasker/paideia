import React, {
  useReducer,
  createContext
} from "react";

const UserContext = createContext();
// const UserDispatchContext = createContext();

let userDefaults = {
  userId: window.localStorage.getItem('userId') || null,
  firstName: window.localStorage.getItem('firstName') || null,
  lastName: window.localStorage.getItem('lastName') || null,
  userEmail: window.localStorage.getItem('userEmail') || null,
  userRoles: window.localStorage.getItem('userRoles') || [],
  userToken: window.localStorage.getItem('userToken') || null,
  userTimezone: window.localStorage.getItem('userTimezone') || null,
  userLoggedIn: window.localStorage.getItem('userLoggedIn') || false,
  flags: window.localStorage.getItem('flags') || [],
  hideReadQueries: window.localStorage.getItem('hideReadQueries') || null,
  currentLocation: window.localStorage.getItem('currentLocation') || null,
  currentLocationBG: window.localStorage.getItem('currentLocationBG') || null,
  currentNpc: window.localStorage.getItem('currentNpc') || null,
  currentNpcImage: window.localStorage.getItem('currentNpcImage') || null,
  currentPath: window.localStorage.getItem('currentPath') || null,
  currentStep: window.localStorage.getItem('currentStep') || null,
  currentAnswer: window.localStorage.getItem('currentAnswer') || null,
  currentScore: window.localStorage.getItem('currentScore') || null,
  currentLogID: window.localStorage.getItem('currentLogID') || null,
  currentBadgeSet: window.localStorage.getItem('currentLogID') || null
}


function userReducer(state, action) {
  switch (action.type) {
    case 'initializeUser': {
      window.localStorage.setItem('userId', action.payload.userId);
      window.localStorage.setItem('firstName', action.payload.firstName);
      window.localStorage.setItem('lastName', action.payload.lastName);
      window.localStorage.setItem('userEmail', action.payload.email);
      window.localStorage.setItem('userRoles', action.payload.userRoles);
      window.localStorage.getItem('hideReadQueries', action.payload.hideReadQueries);
      window.localStorage.getItem('currentBadgeSet', action.payload.currentBadgeSet);
      window.localStorage.setItem('userLoggedIn', true);
      return({
        ...state,
        userId: action.payload.userId,
        firstName: action.payload.firstName,
        lastName: action.payload.lastName,
        userEmail: action.payload.email,
        userLoggedIn: true,
        userRoles: action.payload.userRoles,
        userToken: '',
        userTimezone: '',
        flags: [],
        currentPath: null,
        hideReadQueries: action.payload.hideReadQueries,
        currentBadgeSet: action.payload.currentBadgeSet
      })
    }
    case 'deactivateUser': {
      window.localStorage.clear();
      return({
        ...state,
        userId: null,
        firstName: null,
        lastName: null,
        userEmail: null,
        userLoggedIn: false,
        userRoles: [],
        userToken: '',
        userTimezone: '',
        flags: [],
        currentStep: null,
        currentPath: null,
        currentLocation: null,
        hideReadQueries: null,
        currentBadgeSet: null
      })
    }
    case 'setEvalResults': {
      console.log(action.payload);
      window.localStorage.setItem('currentAnswer', action.payload.answer);
      window.localStorage.setItem('currentScore', action.payload.score);
      window.localStorage.setItem('currentLogID', action.payload.logId);
      return({
        ...state,
        currentAnswer: action.payload.answer,
        currentScore: action.payload.score,
        currentLogID: action.payload.logId
      })
    }
    case 'setCurrentLoc': {
      window.localStorage.setItem('currentLocation', action.payload);
      return({
        ...state,
        currentLocation: action.payload
      })
    }
    case 'leaveCurrentLoc': {
      window.localStorage.setItem('currentLocation', null);
      return({
        ...state,
        currentLocation: null
      })
    }
    case 'setCurrentNpc': {
      window.localStorage.setItem('currentNpc', action.payload);
      return({
        ...state,
        currentNpc: action.payload
      })
    }
    case 'setCurrentStep': {
      window.localStorage.setItem('currentStep', action.payload.step);
      window.localStorage.setItem('currentPath', action.payload.path);
      window.localStorage.setItem('currentAnswer', null);
      window.localStorage.setItem('currentScore', null);
      window.localStorage.setItem('currentLogID', null);
      return {...state,
        currentStep: action.payload.step,
        currentPath: action.payload.path,
        currentAnswer: null,
        currentScore: null,
        currentLogID: null
      }
    }
    default: {
      throw new Error(`Unhandled action type: ${action.type}`)
    }
  }
}

function UserProvider({children}) {
  const [user, dispatch] = useReducer(userReducer, userDefaults);

  return (
    <UserContext.Provider value={{ user, dispatch }}>
      {children}
    </UserContext.Provider>
  );
}

export default UserProvider;
export { UserContext };
