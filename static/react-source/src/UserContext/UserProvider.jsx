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
  currentLocation: window.localStorage.getItem('currentLocation') || null,
  currentLocationBG: window.localStorage.getItem('currentLocationBG') || null,
  currentNpc: window.localStorage.getItem('currentNpc') || null,
  currentNpcImage: window.localStorage.getItem('currentNpcImage') || null,
  currentPath: window.localStorage.getItem('currentPath') || null,
  currentStep: window.localStorage.getItem('currentStep') || null,
  currentAnswer: window.localStorage.getItem('currentAnswer') || null,
  currentScore: window.localStorage.getItem('currentScore') || null,
  currentLogID: window.localStorage.getItem('currentLogID') || null
}


function userReducer(state, action) {
  switch (action.type) {
    case 'initializeUser': {
      window.localStorage.setItem('userId', action.payload.userId);
      window.localStorage.setItem('firstName', action.payload.firstName);
      window.localStorage.setItem('lastName', action.payload.lastName);
      window.localStorage.setItem('userEmail', action.payload.email);
      window.localStorage.setItem('userRoles', action.payload.userRoles);
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
        currentPath: null,
      })
    }
    case 'setCurrentLoc': {
      return({
        ...state,
        currentLocation: action.payload,
        currentLocationBG: locationBackgrounds[action.payload]
      })
    }
    case 'setCurrentNpc': {
      return({
        ...state,
        currentNpc: action.payload,
        currentNpcImage: speakerImages[action.payload]
      })
    }
    case 'setPaths': {
      return {...state, availablePaths: samplePaths}
    }
    case 'setCurrentPath': {
      return {...state, currentPath: state.availablePaths[0]}
    }
    case 'setCurrentStep': {
      return {...state,
        currentStep: action.payload.step,
        currentPath: action.payload.path
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
