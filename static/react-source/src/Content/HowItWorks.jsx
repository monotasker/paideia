import React, { Component } from "react";
import {
   Container,
 } from "react-bootstrap";
// import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
// import {
//   faChevronLeft,
// } from '@fortawesome/free-solid-svg-icons';

import ContentPage from '../Components/ContentPage';
import Collapsible from '../Components/Collapsible';

class HowItWorksContent extends Component {

  render() {
    return(
      <ContentPage
        title="How Does This App Work?"
        backFunc={this.props.backFunc}
      >
        <p>
          Paideia is a bit different from your typical course in ancient Greek. So here are some of the basic ideas to help you get oriented.
        </p>
        <Collapsible linkText="Explore a first-century town"
          linkIcon="map"
        >
          <p>
            Paideia revolves around a fictional hellenized town in eastern Anatolia, on the fringe of the Roman Empire where it runs up against Parthian territory. You will take the role of a foreign slave, recently bought by a middle-class Jewish couple to serve in their house. From the start you are free to move around the town, visiting various locations by clicking them on the town map (there's always a link back to the map in the top menu.
          </p>
        </Collapsible>
        <Collapsible linkText="Talk with the people you meet"
          linkIcon="users"
        >
            <p>
              In each location you may meet one of several townspeople who will ask you questions and give you jobs to do. Each interaction is called a "path" and you can track how many "paths" you have completed each day. Some paths will only involve one "step" (one interaction), while others will require you to go from one location to another and perform a few "steps" before you are done. Along the way, though, you will be introduced to more and more of the Greek language, using it to interact with the town's colourful population.
            </p>
        </Collapsible>
        <Collapsible linkText="Learn naturally"
          linkIcon="leaf"
        >
          <p>
            Paideia is meant to give you something a little like an immersion experience, so that you learn the language naturally, by using it. You will not be asked to do much memorizing of vocabulary lists or verb charts.
          </p>
          <p>
            At the same time, some structured understanding of the language can be a real help. So, whenever you start work on a new badge (learning a new facet of the language) you will be told that it is time to go and view a few video lessons. These lessons will sketch out the grammar, new vocabulary, and new word-forms that you are about to start using in your exchanges in the town.
          </p>
          <p>
            The point of these lessons is not to spend a lot of time memorizing the details. Rather, the videos are a primer for the learning that will take place as you dive back into town life your conversations with the townspeople. If you ever start to feel lost, you can always click the "Lessons" link in the top menu and go back to view any of the videos again.
          </p>
        </Collapsible>
        <Collapsible linkText="Learn at your own pace"
          linkIcon="shoe-prints"
        >
          <p>
            We all know that some of us pick up languages more quickly than others. Many people think they can't learn a language, just because they've never been able to learn at their own pace. In a traditional course, students are forced to match the instructor's pace. That means that some people feel from day one like they're being left behind, while other people get bored.
          </p>
          <p>
            Paideia is different. Here each student is free to learn at their own pace. You don't have to keep up with anyone else, and you can take the time to really "get" one idea before you have to move on to the next.
          </p>
        </Collapsible>
        <Collapsible linkText="Mistakes are great"
          linkIcon="laugh-beam"
        >
          <p>
            The biggest thing to realize about Paideia is that in this town there is no penalty for making mistakes. This is not a giant online test. So after every interaction you will be given examples of some proper responses you could have given. You can, if you like, immediately repeat the "step" and give one of the correct responses, or try out a different response. In fact, you will often learn the most by making mistakes and then looking at the correct responses to see where you went wrong. You are free to learn at your own pace. Once you are able to use your new knowledge without making mistakes, the townspeople will know you are ready to start learning something new.
          </p>
        </Collapsible>
      </ContentPage>
    )
  }
}

export default HowItWorksContent;
