import React, { Component } from "react";
import styled from "styled-components";
import { Row } from "react-bootstrap";

import { make_map_pan } from "../Services/mapNavService";
import useEventListener from "../Hooks/UseEventListener";
import mapImageSvg from "../Images/town_map.svg";

const SvgMap = (props) => {
  const [objectStyles, setObjectStyles] = useState({});

  const setHeight = () => {
    let headroom = document.querySelector('.navbar').offsetHeight;
    let divheight = window.innerHeight - headroom;
    setObjectStyles({height: divheight, width: "100%"});
  }

  useEffect(
    setHeight();
    make_map_pan("town_map", this.props.navFunction);
  );
  useEventListener('resize', setHeight);

  return(
    <Row className="svgMapPane">
      <MapObject id={this.props.id}
        data={mapImageSvg}
        type='image/svg+xml'
        style={this.state.objectStyles}
      >
      </MapObject>
    </Row>
  )
}

export default SvgMap;