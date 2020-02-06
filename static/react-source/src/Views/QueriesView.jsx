import React, { useContext } from "react";
import {
    Row,
    Col
} from "react-bootstrap";

import { UserContext } from "../UserContext/UserProvider";

const QueriesView = () => {

    const {user, dispatch} = useContext(UserContext);

    return(
       <Row key="QueriesView" className="queriesview-component panel-view">
           <Col>
                <h2>Queries</h2>

                {user.currentStep}
           </Col>
       </Row>
    )
}

export default QueriesView;