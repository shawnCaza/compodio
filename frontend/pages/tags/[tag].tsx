import Head from 'next/head'
import { useRouter } from 'next/router'
import { dehydrate, QueryClient} from 'react-query';
import ContentSection from '../../components/generic/layout/ContentSection/contentSection';
import CardCollection from '../../components/generic/layout/cardElements/cardCollection/CardCollection';
import CardContent from '../../components/compodioSpecific/show/showCards/cardContent/CardContent';
import { useShowsQuery, getShows } from '../../hooks/queries/shows';
import { useTagsQuery, getTags } from '../../hooks/queries/tags';



// export async function getServerSideProps() {
//     const queryClient = new QueryClient();
  
//     await queryClient.prefetchQuery('shows', getShows);
//     await queryClient.prefetchQuery('tags', getTags);
  
//     return {
//       props: {
//         dehydratedState: dehydrate(queryClient),
//       },
//     }
//   }

export default function TagPage() {
  const router = useRouter()
  const queryTag = router.query.tag as string
  const allShows = useShowsQuery();
  const allTags = useTagsQuery() ?? {};
  let tagShows = undefined;
  //Need to find ID for `queryTag` in the url.
  const pageTag = Object.values(allTags).find(tag => tag['tag'] === queryTag);
  
  if(pageTag) { 

    tagShows = allShows?.filter(
      (show) => {
        if(show.tagIds){
          return JSON.parse(show.tagIds).includes(pageTag?.id)
        }
      }
    )
  }

  
  return (
    <>
      <Head>
        <title>#{queryTag} - compodio</title>
        <meta name="description" content="Community Radio Podcasts tagged with {pageTag.tag}" />

      </Head>
      <main>
        <ContentSection heading={`Tag: #${queryTag}`} tag='h1'>
            {tagShows &&
              <CardCollection cardDataCollection={tagShows} CardContent={CardContent} />         
            }
             {!tagShows &&
              <p>No shows found for this tag</p>
            }

        </ContentSection>    
      </main>
    </>
  )
}