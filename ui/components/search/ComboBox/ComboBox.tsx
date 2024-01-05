
import React, {useState,  ReactNode } from "react";
import { Show } from "../../../hooks/queries/shows"; 
import { IoSearchSharp, IoCloseSharp } from "react-icons/io5";
import ResultListItem from "../ResultListItem/ResultListItem";
import SearchPageLink from "../SearchPageLink/SearchPageLink";
import { useCombobox } from 'downshift'
import ShowLink from "../../show/ShowLink";
import styles from './ComboBox.module.scss'


interface comboBoxProps {
    handleSearch: Function,
    handleSelection: Function
}

interface fuseResult{
  item: Show;
  score: number;
  refIndex: number;
}
export type {fuseResult};


//This is required for accessibility aria-live messages (e.g., after making a selection).
const itemToString = (result:fuseResult | string | null) => {
  if(!result){return ''}
  return typeof result === 'string' ? result : result.item.showName
}

const defineItemKey = (result:fuseResult | string | null) => {
  if(!result){return ''}
  return typeof result === 'string' ? 'search-all' : result.item.showName
}


function ComboBox ({handleSearch, handleSelection}:comboBoxProps) {
    
    const [inputItems, setInputItems] = useState<fuseResult[]>([])
    
    // if(!inputItems){return null}
    
    const {
    isOpen,
    getToggleButtonProps,
    getLabelProps,
    getMenuProps,
    getInputProps,
    highlightedIndex,
    getItemProps,
    selectedItem,
    selectItem,
  } = useCombobox({
    items: inputItems,
    labelId:"search-label",
    inputId:"search-input",
    menuId:"search-autocomplete-menu",
    toggleButtonId:"search-toggle-button",
    itemToString,
    onInputValueChange: ({ inputValue }) => {
      setInputItems(
        
        handleSearch(inputValue)
      )
    },
    onIsOpenChange: ({ selectedItem }) => {
      if (isOpen) {
        // If menu is closing,blur the input field,
        // so that the keyboard pop up on mobile dissapears
        const input = document.getElementById('search-input');
        input?.blur();
      }
    },
    onSelectedItemChange: ({ selectedItem }) => {

        if(selectedItem){ 
              handleSelection(selectedItem)
            };
      },
    })
    return (
      <div className={styles.container}>
        <label
          className="screen-reader-text"
          {...getLabelProps()}
        >
          Search Shows:
        </label>
        <div className={styles.searchBar}>
          {/* Search button */}
          <button
            className={styles.searchButton}
            aria-label="Search"
            data-testid="combobox-toggle-button"
            {...getToggleButtonProps()}
          >
            <IoSearchSharp/>
          </button>

          <input
            className={styles.input}
            {...getInputProps()}
            data-testid="combobox-input"
            placeholder="Search..."
          />


          {inputItems.length > 0 && 
          <button
            className={styles.searchButton}
            style={{ color:"#000"}}
            aria-label="Clear Search"
            data-testid="clear-button"
            
            onClick={() => selectItem(null)}
          >
            <IoCloseSharp/>
          </button>
          }   
        </div>
        {/* Result list */}
          
        <ul className={styles.dropdown}
          {...getMenuProps()}
        >
          {isOpen && inputItems.length > 1 &&
            inputItems.map((result, index) => (
              
              <ResultListItem 
                result={result} 
                highlightedIndex={highlightedIndex} 
                index={index} 
                getItemProps={getItemProps} 
                key={defineItemKey(result)}
              > 

              {
                // if the result is a string, it's the input value, meaning we want to link to the search result page for the input value
                typeof result === 'string' && result != '' ? 

                  <SearchPageLink searchStr={result}/>
                :

                //otherwise, it's a show, so we want to link to the show page

                  result.item.showName
                
              }
              </ResultListItem>
            ))}

        </ul>
        
      </div>
    )
}

export default ComboBox;