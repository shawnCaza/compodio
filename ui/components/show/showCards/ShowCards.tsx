
import { useShowsQuery, getShows, Show } from '../../../hooks/queries/shows';
import Container from '../../layout/cardElements/container/Container';
import Card from '../../layout/cardElements/card/Card';
import Heading from '../../layout/cardElements/heading/Heading';
import EpDate from '../epDate/EpDate';
import Desc from '../../layout/cardElements/desc/Desc';
import FeedUrl from '../showFeed/ShowFeed';
import ShowLink from '../ShowLink';
import GradientBg from '../../commonElements/gradientBG';

import styles from "./showCards.module.scss";

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

              <Heading>
                <div className={styles.epDate}>
                  <EpDate dtStr={show.newestEpDate} />
                </div>
                <ShowLink slug={show.slug} >
                  <h3>{show.showName}</h3>
                </ShowLink>
              </Heading>

              <GradientBg colours={show.dom_colours}>

                <div style={{height:"124px", maxWidth:"222px", width:"fit-content", display: "block", margin:"auto", padding:"12px"}}>
                  <img src={process.env.NEXT_PUBLIC_image_server_URI+"shows/"+show.slug+"/"+show.slug+"_250.jpg"} style={{height:"100%", width:"100%"}}/>
                </div>
              </GradientBg>

              {/* <a href={show.mp3} download>download</a> */}
              {/* <div>Play button</div> */}
              {/* <audio controls>
              
               
              <source src={show.mp3} type="audio/mpeg"/>
              Your browser does not support the audio element.
              </audio>  */}
              <FeedUrl showId={show.id} slug={show.slug} />
              <Desc desc={show.desc} approxLength={65} />
              
            </Card>
          )}
        </Container>
      </>
    )
} 

export default ShowCards;