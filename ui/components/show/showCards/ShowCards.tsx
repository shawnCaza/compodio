import { useShowsQuery, getShows } from '../../../hooks/queries/shows';
import Container from '../../layout/cardElements/container/Container';
import Card from '../../layout/cardElements/card/Card';
import Heading from '../../layout/cardElements/heading/Heading';
import EpDate from '../epDate';
import CardDesc from '../../layout/cardElements/desc/CardDesc';
import FeedUrl from '../showFeed/showFeed';


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
              <CardDesc desc={show.desc} />
              
            </Card>
          )}
        </Container>
      </>
    )
} 

export default ShowCards;