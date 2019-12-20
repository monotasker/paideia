import React, { } from "react";
import {
    Row,
    Col
} from "react-bootstrap";

const VocabView = () => {
    return(
       <Row key="VocabView" className="vocabview-component panel-view">
           <Col>
                <h2>Vocab</h2>
           </Col>
       </Row> 
    )
}

export default VocabView;