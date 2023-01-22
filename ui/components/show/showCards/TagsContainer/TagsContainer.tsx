
import { useTagsQuery, getTags, Tags } from '../../../../hooks/queries/tags';
import { dehydrate, QueryClient} from 'react-query';

import styles from './TagsContainer.module.scss'
import { useShowTags } from '../../../../hooks/useShowTags';

interface TagsContainerProps {
    currentTagIds: Array<number>,
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


function TagsContainer ({currentTagIds}:TagsContainerProps) {

    const allTags =  useTagsQuery();
    
    if(!allTags){return null}

    const showTags = useShowTags(allTags, currentTagIds, 3)

    return (
        <>
          <div>
                {showTags.map((showTag) =>

                    <span key={showTag.id}>
                        {showTag.tag}
                    </span>

                )}
            </div>
        </>
    )
}

export default TagsContainer;