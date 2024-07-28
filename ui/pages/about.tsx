import React from 'react';
import ContentSection from '../components/generic/layout/ContentSection/contentSection';

  export default function About(){

  

    return (
        <ContentSection heading="About" tag='h1' centered={false} readingWidth={true}>
          <ContentSection heading="Simplifying Access to Community Radio Content" tag='h2' centered={false} readingWidth={true}>
            
            <p>
              Dissapointed it wasn&apos;t possible to subscribe to the local community radio shows I listen to in podcast format, I created this website.
            </p>
            <p>
              Please note, I just made this website for fun, and I&apos;m not affiliated with any of the radio stations or shows listed here.
            </p>
          </ContentSection>
          <ContentSection heading="Get involved" tag='h2' centered={false} readingWidth={true}>
            <p>
              Compodio is an open source project. If you have ideas for improvements, or would like to contribute, please visit the <a href="https://github.com/shawnCaza/compodio" target='_blank' rel="noreferrer noopener">GitHub repo</a>.
            </p>
          </ContentSection>
        </ContentSection>
      );
}