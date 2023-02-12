
import React, {useState,  ReactNode } from "react";
import { Show } from "../../../hooks/queries/shows"; 
import { IoSearchSharp, IoCloseSharp } from "react-icons/io5";


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

const itemToString = (result:fuseResult | null) => (result ? result.item.showName : '')


function ComboBox ({handleSearch, handleSelection}:comboBoxProps) {
    
    const [inputItems, setInputItems] = useState<fuseResult[]>([])
    
    if(!inputItems){return null}
    

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
    itemToString,
    onInputValueChange: ({ inputValue }) => {
      setInputItems(
        handleSearch(inputValue)
      )
    },
    onSelectedItemChange: ({ selectedItem }) => {
      
      if(selectedItem){ handleSelection(selectedItem)};
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
          {isOpen && inputItems.length > 0 &&
            inputItems.map((result, index) => (
              <li ref={result.item.id} className={
                styles.dropdownItem 
                + (highlightedIndex === index ? ' ' + styles.highlightedItem : '')}
                {...getItemProps({result, index, key: result.item.id})}
              >

                  {result.item.showName}

              </li>
            ))}
        </ul>
        
      </div>
    )
}

export default ComboBox;