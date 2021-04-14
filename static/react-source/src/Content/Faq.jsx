import React, { Component } from "react";
// import {
//    Container,
//  } from "react-bootstrap";
// import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
// import {
//   faChevronLeft,
// } from '@fortawesome/free-solid-svg-icons';

import ContentPage from '../Components/ContentPage';
import Collapsible from '../Components/Collapsible';

class FaqContent extends Component {

  render() {
    return(
        <ContentPage
          title="Frequently Asked Questions"
          backFunc={this.props.backFunc}
        >
          <Collapsible linkText="Basic concepts in Paideia">
            <Collapsible linkText='What are "paths" and "steps"?'
              linkElement="h4"
            >
              <p>
                A "step" is one interaction, in which a character in the town says something to you and you respond. A path is one "task" which can consist of a single step or it can involve multiple steps, as when you are sent by one person to talk to someone else. Paideia uses these terms instead of "question" and "answer" to help get away from a test mentality. Paideia is not a test—it's a learning process.
              </p>
            </Collapsible>
            <Collapsible linkText='Are "paths" the locations on the map?'
              linkElement="h4"
            >
              <p>
                No. Paths are the interactions you engage in. You will complete many paths in a given location, and a given path might require you to visit several locations before it is finished.
              </p>
            </Collapsible>
          </Collapsible>

          <Collapsible linkText="Finding Your Way around the App">
            <Collapsible linkText="I'm using Paideia in a credit course. Where is the schedule of topics to learn?"
              linkElement="h4"
            >
              <p>Unless your instructor has told you otherwise, there isn't a set schedule! Paideia is designed to be entirely self-paced. But your grade in the course may depend on how quickly you move through the badge sets in the app. If you're not sure, look at the course syllabus provided by your instructor.</p>
            </Collapsible>
            <Collapsible linkText="Am I supposed to be typing answers in Greek or in English?"
              linkElement="h4"
            >
              <p>
                It depends on the step. Often you will be typing Greek, but other questions ask for English translations. When you want to answer, look at the row of symbols just above the box where you type your response. If there's a big "A" there, you should answer in English. If there's a Greek letter gamma (Γ) you have to answer in Greek.
              </p>
            </Collapsible>
            <Collapsible linkText="How do I know which video lessons to watch?"
              linkElement="h4"
            >
              <p>
                There are three ways.
              </p>
              <ul>
                <li>
                First, whenever you are asked a question there is a "slides" button right below. If you click it, that will open a pop-up with direct links to the slide sets that are relevant to this question.
                </li>
                <li>
                Second, if you look at the list of slide sets (on the main slides page) you will see a list of badges following the title of each slide deck. You can simply look for the slide decks that deal with the badges you're currently working on.
                </li>
                <li>
                Third, the program should tell you whenever it's time to view some more slides (i.e., when you start into a new set of badges).
                </li>
              </ul>
            </Collapsible>
          </Collapsible>
          <Collapsible linkText="Tracking Your Progress">
            <Collapsible linkText="How do I know how many paths I've done?"
              linkElement="h4"
            >
              <p>
                When you're answering a question, look underneath the box (or set of options to choose from) where you provide your answer. You'll see a message telling you how many paths you've done today.
              </p>
              <p>
                You can also look on your user profile, under the "My Activity" heading. The calendar there shows the number of recorded paths you completed on each day. Although you only see one month at a time, you can use the arrow buttons beside the month name to move through the months.
              </p>
              <p>
                If there's ever a discrepancy between these two numbers (under the answer field and on your profile calendar) the profile calendar numbers represent most reliably what the app has recorded.
              </p>
            </Collapsible>
            <Collapsible linkText="How do I know how I'm progressing?"
              linkElement="h4"
            >
              <p>
                Your progress is marked out by your achieving different badges, corresponding with different aspects of the Greek language. These badges are organized into sets. Once the program thinks you have mastered a set of badges, it will automatically introduce the next one and you will begin to be asked questions that involve new parts of the language.
              </p>
            </Collapsible>
            <Collapsible linkText="Where can I see my badges?"
              linkElement="h4"
            >
              <p>
                Your badge progress is displayed on the second tab of your user profile page. To access your profile, click on the "Hello" popup menu at the right-hand of the top menu bar. Then click on "profile".
              </p>
            </Collapsible>
          </Collapsible>
          <Collapsible linkText="Succeeding with Paideia">
            <Collapsible linkText="Do mistakes really not matter?"
              linkElement="h4"
            >
              <p>
                Yes and no. You are not simply graded based on the number of mistakes you've made. But the program won't move you along to the next set of badges until you are getting your current batch of interactions right most of the time. So you don't get "marked down" for mistakes. They won't hurt you. A lot of them just mean that you're not ready to move ahead yet.
              </p>
              <p>
                But that does mean that making a lot of absent-minded errors, or continuing to submit guesses when you don't know how to answer a question properly, will slow down your progress. It's important to take your time, answer carefully, and ask for help when you don't understand.
              </p>
            </Collapsible>
            <Collapsible linkText='How do I move from "beginner" to "apprentice" level in a badge?'
              linkElement="h4"
            >
              <p>
                To have a badge promoted to "apprentice" level, you first have to give correct responses for at least 20 paths related to the badge in question.
              </p>
              <p>
                Once you've given 20 correct answers related to a badge, there are two basic ways to move it up to "apprentice" level.
              </p>
              <ul>
                <li>
                  First, if you go for <b>a full day (24 hours) without making any mistakes</b> on a particular badge, that badge will be promoted to "apprentice" level on the following day.
                </li>
                <li>
                  Second, if <b>8/10 of your responses for that badge have been right over the past week</b> have been correct, you'll also be promoted (even if you're still making a few mistakes).
                </li>
              </ul>
              <p>
                Note that even if you cross one of these thresholds in the middle of your day's activity on Paideia, you often won't actually see the badge promoted until the next day.
              </p>
            </Collapsible>
            <Collapsible linkText={`I'm supposed to be doing some Paideia "paths" on 5 different days per week. Does it matter which days?`}
              linkElement="h4"
            >
              <p>
                Unless your instructor has told you otherwise, no it doesn't matter which days you choose as long as they fall within the same week. Each week is measured from Sunday to Saturday, and you're welcome to do some "paths" on weekend days if you like.
              </p>
            </Collapsible>
            <Collapsible linkText='Does it matter what time of day I do the "paths"?'
              linkElement="h4"
            >
              <p>
                No, time of day doesn't matter as long as they're all on the same day. You can even log on several times over the day and spread out your paths if you like.
              </p>
              <p>
                The one thing to watch, though, is that if you are doing paths late at night you must finish the day's quota by 12:00 midnight. After that, the program will start counting your paths toward the next day's count. Also, make sure when you register that you choose the correct time zone for your location.
              </p>
              <p>
                If you know you're going to be doing your paths late at night on a regular basis, you can change your time zone so that your "day" better fits when you're going to be active on the app.
              </p>
            </Collapsible>
            <Collapsible linkText="What if I miss some days? Can I make them up later by doing more paths another day?"
              linkElement="h4"
            >
              <p>
                Not really. The program doesn't allow making up for missed days once a week is over. It also doesn't let one day's paths offset a shortfall on another day.
              </p>
              <p>
                Why not? Because the best way to learn a language is to work at it for short periods of time, frequently. Long hours of study are actually a very poor way to learn a language, since you quickly stop retaining very much. So Paideia is geared to get you using Greek for shorter times, but doing it often and consistently. Too many gaps (even for a few days) and you take a lot longer to learn the material. If there are extenuating circumstances (like illness) your instructor may sometimes exempt you from a day, but only if the reason is compelling.
              </p>
            </Collapsible>
          </Collapsible>
        </ContentPage>
    )
  }
}

export default FaqContent;
