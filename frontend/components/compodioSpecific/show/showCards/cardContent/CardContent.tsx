import Heading from '../../../../generic/layout/cardElements/heading/Heading';
import EpDate from '../../epDate/EpDate';
import Desc from '../../../../generic/layout/cardElements/desc/Desc';
import FeedLinks from '../../podcastFeedLinks/feedLinks/FeedLinks';
import ShowLink from '../../ShowLink';
import GradientBg from '../../../../generic/commonElements/GradientBg';
import CardImgContainer from '../ImgContainer/CardImgContainer';
import TagsContainer from '../../../../generic/layout/cardElements/TagsContainer/TagsContainer';
import ContentSection from '../../../../generic/layout/ContentSection/contentSection';
import styles from './CardContent.module.scss';
import { Show } from '../../../../../hooks/queries/shows';
  
interface cardContentProps {
    currentCard: Show;
}

  function CardContent({currentCard}:cardContentProps){
    return(
    <>
      <div> 
        <Heading>
          <div className={styles.epDate}>
            <EpDate dtStr={currentCard.newestEpDate} />
          </div>
          <ShowLink slug={currentCard.slug}>
            <h3 className={styles.title}>{currentCard.showName}</h3>
          </ShowLink>
        </Heading>
        <GradientBg colours={currentCard.dom_colours}>
          <ShowLink slug={currentCard.slug}>
            <CardImgContainer show={currentCard} />
          </ShowLink>
        </GradientBg>
      </div>
      <ContentSection heading='Subscribe:' tag='h5' centered={true} spacing='tight'>
        <FeedLinks showId={currentCard.id} slug={currentCard.slug} showName={currentCard.showName} extFeeds={currentCard.extFeeds} />
      </ContentSection>
      <div className={styles.desc}>
        <Desc desc={currentCard.desc} approxLength={125} />
        <span>
          <ShowLink slug={currentCard.slug}>
            &nbsp;More.
          </ShowLink>
        </span>
      </div>
      {currentCard.tagIds && <TagsContainer currentTagIds={JSON.parse(currentCard.tagIds)} maxTags={3} />}
    </>
    )
  };

export default CardContent;
