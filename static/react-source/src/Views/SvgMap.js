import React, { Component } from "react";

import { make_map_pan } from "../Services/mapNavService";
import mapImageSvg from "../Images/town_map.svg";

class SvgMap extends Component {
  constructor(props) {
    super(props);
    this.state = {
      objectStyles: {}
    }
    this.setHeight = this.setHeight.bind(this);
  }

  setHeight() {
    const headroom = document.querySelector('.navbar').offsetHeight;
    let divheight = window.innerHeight - headroom;
    this.setState({
      objectStyles: {height: divheight}
    })
  }

  componentDidMount() {
    this.setHeight();
    window.addEventListener('resize', this.setHeight);
    make_map_pan("town_map", this.props.navFunction);
  }

  render() {
    return(
      this.props.myRoute == "map" &&
      <object id='town_map'
        data={mapImageSvg}
        type='image/svg+xml'
        style={this.state.objectStyles}
      >
      </object>
  )}
}

export default SvgMap;
