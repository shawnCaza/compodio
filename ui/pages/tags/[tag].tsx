import Head from 'next/head'
import { useRouter } from 'next/router'
import { dehydrate, QueryClient} from 'react-query';
import ContentSection from '../../components/layout/ContentSection/contentSection';
import ShowCards from '../../components/show/showCards/ShowCards';
import { useShowsQuery, getShows } from '../../hooks/queries/shows';
import { useTagsQuery, getTags } from '../../hooks/queries/tags';



export async function getServerSideProps() {
    const queryClient = new QueryClient();
  
    await queryClient.prefetchQuery('shows', getShows);
    await queryClient.prefetchQuery('tags', getTags);
  
    return {
      props: {
        dehydratedState: dehydrate(queryClient),
      },
    }
  }

export default function CommentPage() {
  const router = useRouter()
  const queryTag = router.query.tag as string
  const allShows = useShowsQuery();
  const allTags = useTagsQuery() ?? {};

  if(!allTags && !allShows){return null}

  //Need to find ID for `queryTag` in the url.
  const pageTag = Object.values(allTags).find(tag => tag['tag'] === queryTag);
  
  if(!pageTag){return null} // TODO should throw a 404

  const tagShows = allShows?.filter(
    (show) => {
      if(show.tagIds){
        return JSON.parse(show.tagIds).includes(pageTag?.id)
      }
    }
  );

  
  return (
    <>
      <Head>
        <title>#{pageTag.tag} - compodio</title>
        <meta name="description" content="Community Radio Podcasts tagged with {pageTag.tag}" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main>
        <ContentSection heading={`Tag: #${pageTag.tag}`} tag='h1'>
            {tagShows &&
              <ShowCards shows={tagShows} />         
            }
        </ContentSection>    
      </main>
    </>
  )
}