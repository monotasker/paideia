import React, { useState, useEffect, useLayoutEffect } from "react";
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
    make_map_pan("town_map", props.navFunction);
  }

  useEffect(() => { setHeight(); }, [window.innerHeight]);
  useEventListener('resize', setHeight);

  return(
    <Row className="svgMapPane">
      <object id={props.id}
        data={mapImageSvg}
        type='image/svg+xml'
        style={objectStyles}
      >
      </object>
    </Row>
  )
}

export default SvgMap;