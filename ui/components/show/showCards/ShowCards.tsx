
import { useShowsQuery, getShows, Show } from '../../../hooks/queries/shows';
import Container from '../../layout/cardElements/container/Container';
import Card from '../../layout/cardElements/card/Card';
import Heading from '../../layout/cardElements/heading/Heading';
import EpDate from '../epDate/EpDate';
import Desc from '../../layout/cardElements/desc/Desc';
import FlexRow from '../../commonElements/FlexRow/FlexRow';
import ExtLink from '../rssLink/ExtLink';
import RssLink from '../rssLink/RssLink';
import ShowLink from '../ShowLink';
import GradientBg from '../../commonElements/GradientBg';
import CardImgContainer from './ImgContainer/CardImgContainer';
import TagsContainer from '../../layout/cardElements/TagsContainer/TagsContainer';
import ContentSection from '../../layout/ContentSection/contentSection';

import styles from "./ShowCards.module.scss";

interface ShowCardsProps{
    shows: Show[]
  }


function ShowCards({shows}:ShowCardsProps) {


    if (!shows){
      return null;
    } 
    // console.log(shows[0]);
 
    return (
      <>
        <Container>
          {shows.map((show) =>
            <Card key={show.id }>
              <div>
                <Heading>
                  <div className={styles.eperDate}>
                    <EpDate dtStr={show.newestEpDate} />
                  </div>
                  <ShowLink slug={show.slug} >
                    <h4 className={styles.title}>{show.showName}</h4>
                  </ShowLink>
                </Heading>

                <GradientBg colours={show.dom_colours}>
                  <ShowLink slug={show.slug}>
                    <CardImgContainer show={show} />
                  </ShowLink>
                </GradientBg>
              </div>

              {/* <a href={show.mp3} download>download</a> */}
              {/* <div>Play button</div> */}
              {/* <audio controls>
              
               
              <source src={show.mp3} type="audio/mpeg"/>
              Your browser does not support the audio element.
              </audio>  */}
              <ContentSection heading='Subscribe:' tag='h5' centered={true} spacing='tight'>
                <FlexRow showId={show.id} slug={show.slug} showName={show.showName} extFeeds={show.extFeeds}/>
              </ContentSection>


              <div className={styles.desc}>
                <Desc desc={show.desc} approxLength={125} />
                <span> 
                  <ShowLink slug={show.slug}>
                    &nbsp;More.
                  </ShowLink>
                </span>
              </div>
              {show.tagIds &&
              <TagsContainer currentTagIds={JSON.parse(show.tagIds)} maxTags={3} />
              }
            </Card> 
          )}
        </Container>
      </>
    )
} 

export default ShowCards;