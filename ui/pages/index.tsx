import Head from 'next/head'
import styles from '../styles/Home.module.css'
import { useShowsQuery, getShows } from '../hooks/queries/shows';
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

  if (!shows){
    return;
  } 

  return (
    <>
      <Head>
        <title>compodio</title>
        <meta name="description" content="Podcast feeds for community radio" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main>
        <ContentSection heading={'Recently Updated'} tag='h2'>
          
            <ShowCards shows={shows.slice(0,200)} />         
          
        </ContentSection>    
      </main>
    </>
  )
}
