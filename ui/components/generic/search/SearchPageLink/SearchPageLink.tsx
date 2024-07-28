// Description: This component provides a result item in the search ComboBox for the purpose of linking to a search results page. Link logic in SearchContainer.tsx.

 import { IoSearchSharp } from "react-icons/io5";
 import styles from '../ComboBox/ComboBox.module.scss'


interface searchPageLinkProps {
    searchStr: string;
}


function SearchPageLink({searchStr}:searchPageLinkProps){
  
  return (
    <>

        <span className={styles.searchListPageLinkIcon}><IoSearchSharp/></span>
        {`All Results for: "${searchStr}"`}

    </>
  )
}

export default SearchPageLink;
