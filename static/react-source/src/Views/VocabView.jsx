import React, { useEffect } from "react";
import {
    Row,
    Col
} from "react-bootstrap";

import { fetchVocabulary } from "../Services/stepFetchService";

const VocabView = () => {
  useEffect(() => {
    fetchVocabulary({vocab_scope_selector: 0})
    .then(mydata => {
      console.log(mydata);
    });
  });

  return(
     <Row key="VocabView" className="vocabview-component panel-view">
         <Col>
              <h2>Vocab</h2>
         </Col>
     </Row>
  )
}

export default VocabView;