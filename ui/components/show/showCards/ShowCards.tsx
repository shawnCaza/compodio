import { useShowsQuery, getShows } from '../../../hooks/queries/shows';
import Container from '../../layout/cardElements/container/Container';
import Card from '../../layout/cardElements/card/Card';
import Heading from '../../layout/cardElements/heading/Heading';
import EpDate from '../epDate';
import Desc from '../../layout/cardElements/desc/Desc';
import FeedUrl from '../showFeed/ShowFeed';

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
                <EpDate dtStr={show.newestEpDate} />
                <h3>{show.showName}</h3>
              </Heading>

              <div>Play button</div>
              <FeedUrl showId={show.id} slug={show.slug} />
              <Desc desc={show.desc} approxLength={125} />
              
            </Card>
          )}
        </Container>
      </>
    )
} 

export default ShowCards;