import Link from 'next/link'

import { useTagsQuery, getTags, Tag } from '../../../../hooks/queries/tags';
import { dehydrate, QueryClient} from 'react-query';

import styles from './TagsContainer.module.scss'
import { useMappedShowTags } from '../../../../hooks/useMappedShowTags';

interface TagsContainerProps {
    currentTagIds: Array<number>,
    maxTags: number | null | undefined
}


export async function getServerSideProps() {
    const queryClient = new QueryClient();
  
    await queryClient.prefetchQuery('tags', getTags);
  
    return {
      props: {
        dehydratedState: dehydrate(queryClient),
      },
    }
  }


function TagsContainer ({currentTagIds, maxTags=null}:TagsContainerProps) {

    const allTags =  useTagsQuery();
    
    if(!allTags){return null}

    const currentTags = useMappedShowTags(allTags, currentTagIds, maxTags)

    return (
        <>
          <div className={styles.tagContainer}>
                {currentTags.map((currentTag) =>
                    <Link href={`/tags/${currentTag.tag}`} key={currentTag.id}>
                      <button className={styles.tag} >
                          #{currentTag.tag}
                      </button>
                    </Link>

                )}
            </div>
        </>
    )
}

export default TagsContainer;