import { useShowsQuery, getShows } from '../../../hooks/queries/shows';
import Card from '../../layout/cardElements/card/Card';
import Heading from '../../layout/cardElements/heading/Heading';
import EpDate from '../epDate';
import CardDesc from '../../layout/cardElements/desc/CardDesc';
import FeedUrl from '../showFeed';

import styles from './Container.module.scss';

function Container() {

    const shows = useShowsQuery();

    if (!shows){
      return null;
    } 
    // console.log(shows[0]);

    return (
      <>
        <div className={styles.cardContainer}>
          {shows.map((show) =>
            <Card key={show.id }>

              <Heading>
                <EpDate dtStr={show.newestEpDate} />
                <h3>{show.showName}</h3>
              </Heading>

              <div>Play button</div>
              <FeedUrl showId={show.id} source={show.source} slug={show.slug} />
              <CardDesc desc={show.desc} />
              
            </Card>
          )}
        </div>
      </>
    )
} 

export default Container;