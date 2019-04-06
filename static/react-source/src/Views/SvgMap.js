import React, { Component } from "react";
import styled from "styled-components";
import { Row } from "react-bootstrap";

import { make_map_pan } from "../Services/mapNavService";
import mapImageSvg from "../Images/town_map.svg";

const MapRow = styled(Row)`
`;

const MapObject = styled.object`
  width: 100%;
  margin:0 auto;
  cursor: move;
  svg {
    cursor: move;
  }
`;


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
      objectStyles: {height: divheight, width: "100%"}
    })
  }


  componentDidMount() {
    this.setHeight();
    window.addEventListener('resize', this.setHeight);
    make_map_pan("town_map", this.props.navFunction);
  }

  componentWillUnmount() {
    window.removeEventListener('resize', this.setHeight);
  }

  render() {
    return(
      <MapRow className="svgMapPane">
        <MapObject id={this.props.id}
          data={mapImageSvg}
          type='image/svg+xml'
          style={this.state.objectStyles}
        >
        </MapObject>
      </MapRow>
  )}
}

export default SvgMap;
