import { useShowsQuery, getShows } from '../../../hooks/queries/shows';
import Container from '../../layout/cardElements/container/Container';
import Card from '../../layout/cardElements/card/Card';
import Heading from '../../layout/cardElements/heading/Heading';
import EpDate from '../epDate/epDate';
import Desc from '../../layout/cardElements/desc/Desc';
import FeedUrl from '../showFeed/ShowFeed';
import styles from "./showCards.module.scss";



function ShowCards() {

    const shows = useShowsQuery();

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
                <h3>{show.showName}</h3>
              </Heading>

              {/* <div>Play button</div> */}
              <FeedUrl showId={show.id} slug={show.slug} />
              <Desc desc={show.desc} approxLength={125} />
              
            </Card>
          )}
        </Container>
      </>
    )
} 

export default ShowCards;