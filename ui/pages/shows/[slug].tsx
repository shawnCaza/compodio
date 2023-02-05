import { useRouter } from 'next/router'
import Link from 'next/link';
import { dehydrate, QueryClient} from 'react-query';
import GradientBg from '../../components/commonElements/GradientBg';
import ShowImgContainer from '../../components/show/showPage/ImgContainer/ShowImgContainer';
import ShowFeed from '../../components/show/showFeed/ShowFeed';
import EpDate from '../../components/show/epDate/EpDate';
import { useShowLength } from '../../components/show/hooks/useShowLength';
import ShowCards from '../../components/show/showCards/ShowCards';
import { useShowsQuery, getShows } from '../../hooks/queries/shows';
import styles from './showsPage.module.scss'



export async function getServerSideProps() {
    const queryClient = new QueryClient();
  
    await queryClient.prefetchQuery('shows', getShows);
  
    return {
      props: {
        dehydratedState: dehydrate(queryClient),
      },
    }
  }

export default function ShowPage() {
  const router = useRouter()
  const querySlug = router.query.slug as string
  const shows = useShowsQuery();
  const show = shows?.find(show => show.slug === querySlug);
  const showLength = useShowLength(show?.duration);
  
  if(!show){return null};

  return (
    <>
    <div className={styles.detailAndImageWrapper}>

      <div className={styles.showImgWrapper}>
        <GradientBg colours={show.dom_colours}>
          <ShowImgContainer show={show} />
        </GradientBg>
      </div> 

      <div className={styles.showDetails}>
        <h1>{show.showName}</h1>
        <ShowFeed showId={show.id} slug={show.slug} />
        <div>{show.desc}</div>
        <div>Hosted by: {show?.host}</div>
        <div>Latest Episode: <EpDate dtStr={show.newestEpDate}/></div>
        <div>
          <a href={show.internal_link} target={'_blank'} rel={"noreferrer"}>
            Official {show.source.toUpperCase()} page
          </a>
        </div>
        {showLength && <div>Episode Length: {showLength}</div>}
      </div>



    </div>
    </>
  )
}