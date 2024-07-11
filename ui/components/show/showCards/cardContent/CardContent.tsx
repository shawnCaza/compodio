import Card from '../../../layout/cardElements/card/Card';
import Heading from '../../../layout/cardElements/heading/Heading';
import EpDate from '../../epDate/EpDate';
import Desc from '../../../layout/cardElements/desc/Desc';
import FeedLinks from '../../podcastFeedLinks/feedLinks/FeedLinks';
import ShowLink from '../../ShowLink';
import GradientBg from '../../../commonElements/GradientBg';
import CardImgContainer from '../ImgContainer/CardImgContainer';
import TagsContainer from '../../../layout/cardElements/TagsContainer/TagsContainer';
import ContentSection from '../../../layout/ContentSection/contentSection';
import styles from './CardContent.module.scss';
import { Show } from '../../../../hooks/queries/shows';
  
interface cardContentProps {
    currentShow: Show;
}

  function CardContent({currentShow}:cardContentProps){
    
    return(
    <>
      <div> 
        <Heading>
          <div className={styles.epDate}>
            <EpDate dtStr={currentShow.newestEpDate} />
          </div>
          <ShowLink slug={currentShow.slug}>
            <h3 className={styles.title}>{currentShow.showName}</h3>
          </ShowLink>
        </Heading>
        <GradientBg colours={currentShow.dom_colours}>
          <ShowLink slug={currentShow.slug}>
            <CardImgContainer show={currentShow} />
          </ShowLink>
        </GradientBg>
      </div>
      <ContentSection heading='Subscribe:' tag='h5' centered={true} spacing='tight'>
        <FeedLinks showId={currentShow.id} slug={currentShow.slug} showName={currentShow.showName} extFeeds={currentShow.extFeeds} />
      </ContentSection>
      <div className={styles.desc}>
        <Desc desc={currentShow.desc} approxLength={125} />
        <span>
          <ShowLink slug={currentShow.slug}>
            &nbsp;More.
          </ShowLink>
        </span>
      </div>
      {currentShow.tagIds && <TagsContainer currentTagIds={JSON.parse(currentShow.tagIds)} maxTags={3} />}
    </>
    )
  };

export default CardContent;
