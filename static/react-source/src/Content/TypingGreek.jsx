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

class TypingGreekContent extends Component {

  render() {
    return(
      <ContentPage
        title="How Do I Type Greek Letters?"
        backFunc={this.props.backFunc}
      >
        <p>
          To answer the questions in Paideia you will need to type Greek letters. But don't worry. It's not hard. You just have to set up a Greek keyboard on your device and switch to it when you want to type Greek letters. Here are some instructions to help you get set up, whatever device you're using.
        </p>
        <Collapsible
          linkText="How Do I Switch to a Greek Keyboard?"
          linkIcon="keyboard"
        >
          <p>To answer questions in Greek you will just need to switch your keyboard to "Polytonic Greek." Note that the "Polytonic" part here is important. Modern Greek keyboards don't include all of the accents and marks you need to type ancient Greek. So you need to be able to switch your input language to Greek <i>and</i> enable the polytonic keyboard.</p>

          <Collapsible
            linkText="On a laptop or desktop computer"
            linkElement="h4"
            linkIcon="laptop"
          >
            <p>If you're using a laptop or desktop computer there are some good tutorials available online. The process just varies a bit depending on your operating system:</p>

            <h5>MacOS (iMac, Macbook)</h5>
            <ul>
              <li>
                <a href="http://www.quia.com/files/quia/users/lukeionregan/LANG-Greek/MacPolytonicGreek.pdf">PDF document</a>
              </li>
              <li>
                <a href="http://www.dramata.com/Ancient%20polytonic%20Greek%20on%20Macintosh.pdf">Diagram showing position of letters</a>
              </li>
              <li>
                <a href="https://www.youtube.com/watch?v=M4PHmMjMjVo">Video</a>
              </li>
            </ul>

            <h5>Windows</h5>
            <ul>
              <li>
                <a href="https://www.youtube.com/watch?v=M49k3DTsBlM">Windows 11 video (instructions start at 4:40)</a>
              </li>
              <li>
                <a href="https://www.youtube.com/watch?v=9ketasaCpOY">Windows 10 video (including optional installation of SBLGreek font)</a> (<a href="https://www.ctsfw.edu/wp-content/uploads/2016/02/Greek-Unicode-Keyboard-Input-Windows-10.pdf">text-based instructions</a>)
              </li>
              <li>
                <a href="http://www.youtube.com/watch?v=UkcHC3aVcsc&feature=share&list=PLThwDZhkt_VeRDppYmwlQRUI2ekaU4zSo">Windows 7 video</a>
              </li>
              <li>
                <a href="http://www.youtube.com/watch?v=1sZtLxFNILw&feature=share&list=PLThwDZhkt_VeRDppYmwlQRUI2ekaU4zSo">Windows Vista video</a>
              </li>
              <li>
                <a href="http://www.dramata.com/Ancient%20polytonic%20Greek%20in%20Windows.pdf">Diagram showing position of letters</a>
              </li>
              <li>
                <a href="http://www.ellopos.net/elpenor/greek-texts/gr-pol-keys/greek-keyboard.asp">Interactive page showing how to type different accent combinations</a>
              </li>
            </ul>
          </Collapsible>

          <Collapsible
            linkText="On a mobile device"
            linkElement="h4"
            linkIcon="mobile"
          >
            <p>On mobile devices you'll need a special keyboard app to type Polytonic Greek. Fortunately there's a very nice free one available for both iOS and Android devices, and it works well on both phones and tablets:</p>

            <ul>
              <li>
                <a href="https://itunes.apple.com/us/app/hoplite-greek-keyboard/id1200319047?mt=8">Hoplite Greek Keyboard on iTunes</a>
              </li>
              <li>
                <a href="https://play.google.com/store/apps/details?id=com.philolog.hoplitekeyboard">Android Hoplite Greek Keyboard on Google Play</a>
              </li>
            </ul>
          </Collapsible>

          <p>If you have any trouble after you've followed these instructions, just post a query and ask.</p>

        </Collapsible>

        <Collapsible
          linkText="Typing Breathing Marks and Accents"
          linkIcon="wind"
        >
          <p>As people get started with Paideia they are often confused about how to type the breathing marks and accents that appear above the characters. First you need to make sure that you're using a polytonic Greek keyboard. The modern Greek keyboard won't include all of these characters. Then the method will depend on whether you're using a desktop or laptop computer, or whether you're using a mobile device.</p>

          <Collapsible
            linkText="Desktop and laptop computers"
            linkElement="h4"
            linkIcon="laptop"
          >
            <p>On computers running MacOS, Windows, or Linux, the breathing marks and accents are produced using "dead keys." You first press a dead key (which does nothing immediately) and then press the key for the letter the mark or accent should accompany. Note that this isn't a <i>key combination</i>, like with many keyboard shortcuts. You don't hold down the dead key while typing the letter key. Instead press the dead key, release it, and then type the letter key.</p>

            <p>The trick is knowing which "dead key" to use. Each operating system uses slightly different dead keys. The instructions here on Paideia for activating your Greek keyboard include links to keyboard layout charts for most operating systems. These should show you which dead key to use for each accent mark.</p>

            <p>Usually the dead key for the breathing marks is either the ; or ' key. Try each one unshifted, and then try holding shift with each of them. The other accent mark you will have to type is the acute accent (rises to the right). It is also usually typed with either ; or ' (shifted or unshifted) as the dead key. So experiment with those keys. If you can't find the acute accent there, try each of the punctuation keys (anything other than a letter) with a vowel to see whether it acts as a dead key and what it produces. It may take a bit of trial and error but you should find the acute accent in short order.</p>

            <ul>
              <li>
                <a href="http://patristica.net/graeca/how-to-type-in-greek/">Diagrams showing dead key combinations for each accent (Windows)</a>
              </li>
              <li>
                <a href="http://www.dramata.com/Ancient%20polytonic%20Greek%20in%20Windows.pdf">Alternate keyboard diagram and list of dead key combinations (Windows)</a>
              </li>
            </ul>
          </Collapsible>
          <Collapsible
            linkText="iOS and Android mobile devices"
            linkElement="h4"
            linkIcon="mobile"
          >
            <p>Most mobile operating systems don't yet have good support for typing polytonic Greek. So you'll have to use the Hoplite Greek Keyboard. (The links to download it are included in the instructions above for activating a Greek keyboard.)</p>

            <p>The nice thing about this keyboard is that (unlike the desktop Greek keyboards) the breathing marks and accents all have their own dedicated keys. No using "dead keys"! Note, too, that with the Hoplite keyboard you type the mark or accent <i>after</i> you type the letter.</p>
          </Collapsible>
        </Collapsible>
    </ContentPage>
    )
  }
}

export default TypingGreekContent;
