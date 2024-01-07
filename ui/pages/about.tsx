import React from 'react';
import ContentSection from "../components/layout/ContentSection/contentSection"

  export default function About(){

  

    return (
        <ContentSection heading="About" tag='h1' centered={false} readingWidth={true}>
          <ContentSection heading="Simplifying Access to Community Radio Content" tag='h2' centered={false} readingWidth={true}>
            
            <p>
              Dissapointed it wasn't possible to subscribe to the local community radio shows I listen to, I created this website as a solution to my frustration.
            </p>
            <p>
              Please note, I just made this website for fun, and I'm not affiliated with any of the radio stations or shows listed here.
            </p>
          </ContentSection>
          <ContentSection heading="Get involved" tag='h2' centered={false} readingWidth={true}>
            <p>
              Compodio is an open source project. If you have ideas for improvements, or would like to contribute, please visit the <a href="https://github.com/shawnCaza/compodio" target='_blank' rel="noopener">GitHub repo</a>.
            </p>
          </ContentSection>
        </ContentSection>
      );
}