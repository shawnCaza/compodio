import Head from 'next/head'
import styles from '../styles/Home.module.css'
import { useShowsQuery, getShows } from '../hooks/queries/shows';
import { useRecommendedShows } from '../hooks/useRecommendedShows';
import { getTags } from '../hooks/queries/tags';
import { dehydrate, QueryClient} from 'react-query';
import ContentSection from '../components/layout/ContentSection/contentSection';
import ShowCards from '../components/show/showCards/ShowCards';

export async function getServerSideProps() {
  const queryClient = new QueryClient();

  await Promise.all([
    queryClient.prefetchQuery('tags', getTags),
    queryClient.prefetchQuery('shows', getShows)
  ]);

  return {
    props: {
      dehydratedState: dehydrate(queryClient),
    },
  }
}

export default function Home() {
  const shows = useShowsQuery();

 

  const recomendedShows = useRecommendedShows();
  
  if (!shows || !recomendedShows){
    return;
  }
  console.log(recomendedShows);
  return (
    <>
      <Head>
        <title>compodio</title>
        <meta name="description" content="Podcast feeds for community radio" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main>
      <ContentSection heading={'Putting the Podcast in Community Radio'} tag='h1' centered={true} readingWidth={true}>
            
            <p>
              Compodio strives to make it easier to listen to community radio shows online. We do this by generating podcast feeds for shows that don't already have one. Our categorized, searchable database, also simplifies finding your favourite shows and discovering new ones.

            </p>         
          
        </ContentSection> 
        
        <ContentSection heading={'Recommended'} tag='h2'>
            
            <ShowCards shows={recomendedShows} />         
          
        </ContentSection> 

        <ContentSection heading={'Recently Updated'} tag='h2'>
          
            <ShowCards shows={shows.slice(0,10)} />         
          
        </ContentSection>    
      </main>
    </>
  )
}
