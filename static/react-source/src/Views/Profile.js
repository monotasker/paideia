import React, { Component } from "react";

class Profile extends Component {
  render() {
    return (
      <div className="row">
        <div className="col">
        <h2>Profile</h2>
        <p>Mauris sem velit, vehicula eget sodales vitae,
        rhoncus eget sapien:</p>
        <ul>
          <li>Nulla pulvinar diam</li>
          <li>Facilisis bibendum</li>
          <li>Vestibulum vulputate</li>
          <li>Eget erat</li>
          <li>Id porttitor</li>
        </ul>
        </div>
      </div>
    );
  }
}

export default Profile;
