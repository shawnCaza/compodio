import { useRouter } from 'next/router'
import { dehydrate, QueryClient} from 'react-query';
import ShowCards from '../../components/show/showCards/ShowCards';
import { useShowsQuery, getShows } from '../../hooks/queries/shows';



export async function getServerSideProps() {
    const queryClient = new QueryClient();
  
    await queryClient.prefetchQuery('shows', getShows);
  
    return {
      props: {
        dehydratedState: dehydrate(queryClient),
      },
    }
  }

export default function CommentPage() {
  const router = useRouter()
  const querySlug = router.query.slug as string
  const shows = useShowsQuery();
  const show = shows?.find(show => show.slug === querySlug);
  
  return (
    <>
      <h1>{show?.showName}</h1>
      
    </>
  )
}