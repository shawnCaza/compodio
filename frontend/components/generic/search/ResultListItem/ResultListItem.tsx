// Description: This component provides a result item in the search ComboBox for the purpose of linking to a search results page. Link logic in SearchContainer.tsx.

import { fuseResult } from "../ComboBox/ComboBox"; 
import styles from '../ComboBox/ComboBox.module.scss'

interface resultListItemProps {
    result: fuseResult | string;
    highlightedIndex: number;
    index: number;
    getItemProps: Function;
    children: React.ReactNode;
}


function ResultListItem({result, highlightedIndex, index, getItemProps, children}:resultListItemProps){
  
  return (
    <>

        <li 
        ref={result} 
        className={
            styles.dropdownItem
            + (highlightedIndex === index ? ' ' + styles.highlightedItem : '')
            + (typeof result === 'string' ? ' ' + styles.SearchPageLinkItem : '')
        }
        {...getItemProps({result, index, key: result})}
        > 

            {children}
        
        </li>

    </>
  )
}

export default ResultListItem;
