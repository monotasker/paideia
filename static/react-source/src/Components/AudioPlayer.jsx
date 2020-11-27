import React, { useState } from 'react';
import { Button } from "react-bootstrap";
import ReactCSSTransitionReplace from "react-css-transition-replace";
import { CSSTransition, TransitionGroup } from "react-transition-group";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faPlayCircle,
  faPauseCircle,
  faSpinner
} from '@fortawesome/free-solid-svg-icons';

const AudioPlayer = (props) => {
  const [ playing, setPlaying ] = useState('loading');

  const clickAction = (event) => {
    let myaudio = document.getElementById("prompt-audio");
    if ( ["ended"].includes(event.type) ) {
      myaudio.pause();
      setPlaying('paused');
    } else if ( ["canplaythrough"].includes(event.type) ) {
      myaudio.play();
      setPlaying('playing');
    } else if ( ["click"].includes(event.type) ) {
      if (playing === "playing") {
        myaudio.pause();
        setPlaying('paused');
      } else {
        myaudio.play();
        setPlaying('playing');
      }
    }
    event.preventDefault();
  }

  const myComponents = {
      'playing': ["pause", faPauseCircle, ""],
      'loading': ["play", faSpinner, "fa-pulse"],
      'paused': ["play", faPlayCircle, ""]
  }

  return (
    <span id="audio-player-component" className="audio-player-component">
        <Button className="audio-play-control"
        onClick={clickAction}
        >
          <TransitionGroup>
            <CSSTransition
              key={`audio-button-${myComponents[playing][0]}`}
              classNames="cross-fade"
              timeout={500}
            >
                <FontAwesomeIcon
                icon={myComponents[playing][1]}
                className={`${myComponents[playing][0]}-circle cross-fade
                            ${myComponents[playing][2]}`}
                size="2x"
                />
            </CSSTransition>
            </TransitionGroup>
        </Button>
        <audio
        id='prompt-audio'
        autoPlay={false}
        onEnded={clickAction}
        onCanPlayThrough={clickAction}
        >
          {!!props.mp3Source && <source src={props.mp3Source} type="audio/mpeg" />}
          {!!props.m4aSource && <source src={props.m4aSource} type="audio/mp4" />}
          {!!props.ogaSource && <source src={props.ogaSource} type="audio/ogg" />}
        </audio>
    </span>
  )
}

export default AudioPlayer;