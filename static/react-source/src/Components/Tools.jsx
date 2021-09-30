import React, { useState, useEffect } from 'react';
import {
    ButtonGroup,
    Button
} from "react-bootstrap";
import { useHistory
} from "react-router-dom";
import {
    TransitionGroup,
    SwitchTransition,
    CSSTransition
} from "react-transition-group";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import ReferenceView from "../Views/ReferenceView";
import VocabView from "../Views/VocabView";
import QueriesView from "../Views/QueriesView";
import SettingsView from "../Views/SettingsView";

const Tools = () => {

    const [openPanel, setOpenPanel] = useState(null);
    const myHistory = useHistory();

    useEffect(() => {
      const handleClick = (event) => {
          if ( event.target.closest('.tools-component, .tool-panels, .queries-view-changer, .vocabview-sorter-link, [class*="students-selector-form"], [class*="class-selector-form"], .queries-view-pager') === null ) {
            setOpenPanel(null);
          }
      }
      window.addEventListener("click", handleClick);
      return () => window.removeEventListener("click", handleClick);
    });

    const navigateAway = (location) => {
        setOpenPanel(null);
        myHistory.push(location);
    }

    const panels = [
        {label: 'Queries',
         icon: "comment",
         component: <QueriesView navigateAwayHandler={navigateAway} />},
        {label: 'Reference',
         icon: "bolt",
         component: <ReferenceView navigateAwayHandler={navigateAway}/>},
        {label: 'Vocab',
         icon: "sort-alpha-down",
         component: <VocabView navigateAwayHandler={navigateAway}/>},
        {label: 'Settings',
         icon: "sliders-h",
         component: <SettingsView navigateAwayHandler={navigateAway}/>},
        // {label: 'Notes',
        //  icon: faPencilAlt,
        //  component: NotesPanel},
    ]

    return(
        <React.Fragment>
            <ButtonGroup vertical className="tools-component">
                {panels.map( ({ label, icon, component }) =>
                    <Button key={label}
                        value={label}
                        onClick={() => openPanel === label ? setOpenPanel(null) : setOpenPanel(label)}>
                        <FontAwesomeIcon
                          icon={icon}
                          fixedWidth size="lg"
                        />
                        {label}
                    </Button>
                )}
            </ButtonGroup>
            <div className="tool-panels">
                {panels.map(({ label, icon, component }) =>
                    <CSSTransition
                        key={label}
                        in={label === openPanel}
                        timeout={0}
                        classNames="panel-body"
                        mountOnEnter={true}
                        appear={true}
                    >
                        <div className="panel-body">
                            {component}
                        </div>
                    </CSSTransition>
                )}
            </div>
        </React.Fragment>
    )

}

export default Tools;