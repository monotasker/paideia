import createGlobalStyle from "styled-components";

const GlobalStyle = createGlobalStyle`
  @import url('https://fonts.googleapis.com/css?family=Amatic+SC|Open+Sans');

  @font-face {
      font-family: 'Glyphicons Halflings';
      src: url('../Fonts/glyphicons-halflings-regular.eot');
      src: url('../Fonts/glyphicons-halflings-regular.eot?#iefix') format('embedded-opentype'), url('../Fonts/glyphicons-halflings-regular.woff') format('woff'), url('../Fonts/glyphicons-halflings-regular.ttf') format('truetype'), url('../Fonts/glyphicons-halflings-regular.svg#glyphicons_halflingsregular') format('svg');
      font-weight: normal;
      font-style: normal;
  }

  @font-face {
      font-family: 'SBLGreekRegular';
      src: url('../Fonts/sbl_grk-webfont.eot');
      src: local('☺'),
      url('../Fonts/sbl_grk-webfont.woff') format('woff'),
      url('../Fonts/sbl_grk-webfont.ttf') format('truetype'),
      url('../Fonts/sbl_grk-webfont.svg#webfontRelj09Wi') format('svg');
      font-weight: normal;
      font-style: normal;
  }

  .svg-inline--fa               {margin-right: 0.5rem;
  }
`;

const images = {
  $mapPng: "../Images/town_map.png",
}

const breakpoints = {
  $breakpointSm: "576px"
}

const colors = {
  $blue:                  '#049cdb',
  $blueDark:              '#1c7f99', // #006699;
  $cranberry:             '#852625',
  $cinnamon:              '#845852',
  $cream:                 '#F8F0E5',
  // $green:                 '#5BA917',
  $green:                 '#96BC44',
  $greenDark:             '#809240',
  $neutralLight:          '#f2eed5',
  $orange:                '#f89406',
  $putty:                 '#d8d3b3',
  $red:                   '#B10808',
  $tapioca:               '#F2E5D4',
  $warning:               '#a40000',
  $wine:                  '#701',
  $white:                 '#fff',
  $yellow:                '#ffc40d',
}

const palleteColors = {
  $palletteBG:            colors.$white,
  $pallette1:             colors.$neutralLight,
  $pallette2:             colors.$putty,
  $pallette3:             colors.$green,
  $pallette4:             colors.$greenDark,
  $accent1:               colors.$red,
  $accent2:               colors.$blueDark,
  $accent3:               colors.$orange,
  $textColor:             '#333',
  $linkColor:             colors.$pallette2,
  $navbarLinkColor:       colors.$pallette2,
}

const semanticColors = {
  $dangerBg:        '#fcf2f2',
  $danger:          '#bd362f', // #a84f4c; // default #dFb5b4;
  $infoBg:          '#f0f7fd', //#d0e3f0;
  $info:            '#5bc0de',
  $infoDark:        '#2f96b4', // #5387B2;
  $warningBg:       '#fefbed',
  $warning:         colors.$orange, // #f1e7bc;
  $error:           colors.$red,
  $successBg:       '#dff0d8',
  $success:         colors.$pallette3,  // #d6e9c6;
  $successDark:     colors.$pallette4, // #d6e9c6;
}

const typography = {
  $fontSizeBase:               '1rem',
  $fontSizeLg:                 '1.25rem',
  $sansFonts:                   '"Open Sans", sans-serif',
}

div.maria-bubble,
div.maria-bubble-mobile        {background-color: white;
                                padding:2rem;
    h1                         {font-family: 'Amatic SC', cursive;
                                font-weight: regular;
                                font-size: 3rem;
                                color: darken($pallette1, 30%);
    }
    button                     {background-color: $pallette4;
                                border: 1px solid $palletteBG;
                                margin-top: 0.5rem;
    }
    p.index-openmessage         {font-size: $font-size-base;
                                color: #888;
    }
}

div.warning.row                {background-color: $danger;
                                color: $warning;
                                padding: 1.25rem 0;
    p                          {text-align: center;
    }
}


div.modal-set.row              {color: #efefef;
                                background-color: $pallette3;
                                text-align: center;
                                padding-top: 3rem;
                                padding-bottom: 3rem;
    @media (max-width: map-get($grid-breakpoints, md))  {padding: 0;
                                         text-align: left;
                                         padding-left: 2rem;
                                         padding-right: 2rem;
    }
    .info-pane                 {
      .info-illustration-wrapper          {//text-align: center;
                                           // width:100%;
          @media (max-width: map-get($grid-breakpoints, md)) {text-align: left;
          }
          .info-pane-illustration {width:12rem;
                                   background-color: rgba(255, 255, 255, 0.3);
                                   border-radius: 50%;
                                   padding: 0.5rem;
                                   // margin: 0px auto;
              @media (max-width: $breakpoint-sm) {float: right;
                                                  width: 3rem;
                                                  padding: 1rem;
              }
          }
          h4 a                                   {color: $white;
                                                  margin-top: 2rem;
                                                  font-size: $font-size-base;
              @media (max-width: $breakpoint-sm) {line-height: 3em;
                                                  height: 3em;
              }
              &:hover                            {text-decoration: dotted;
              }
          }
      }
    }
    p                       {hyphens: auto;
                            -moz-hyphens: auto;
                            -webkit-hyphens: auto;
                            -ms-hyphens: auto;
    }
}

// walk interface---------------------------------------

div.content > .walk-container                 {
  div#exploring-mask                          {display: block;
                                               position: absolute;
                                               background-color: rgba(255,255,255,1.0);
                                               width: 100%;
                                               height: 100%;
                                               text-align: center;
      img                                     {position: absolute;
      }
  }
  object#town_map                             {width: 100%;
                                               margin:0 auto;
                                               cursor: move;
                                               opacity: 0;
    svg                                       {cursor: move;
    }
  }
}
