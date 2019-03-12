import React, { Component } from "react";
import UserContext from './UserContext';

class UserProvider extends Component {
  state = {
    id: '',
    firstName: "Bob",
    lastName: "Tomato",
    roles: [],
    token: '',
    timezone: '',
  };

  render() {
    return (
      <UserContext.Provider
        value={{
          id: this.state.id,
          firstName: this.state.firstName,
          lastName: this.state.lastName,
          roles: this.state.roles,
          timezone: this.state.timezone
        }}
      >
        {this.props.children}
      </UserContext.Provider>
    );
  }
}

export default UserProvider;
