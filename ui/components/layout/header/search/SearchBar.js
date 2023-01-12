import { useEffect, useRef, useState } from "react";
import SearchBarRes from './SearchBarRes';
import SearchForm from './SearchForm';
import { IoSearchSharp } from "react-icons/io5";

const SearchBar = (props) => {
    
    const searchInput = useRef();
    const [searchingFor, setSearchingFor] = useState(null);
    const bodyClick = props.bodyClick;
    const setBodyClick = props.setBodyClick;
    const [mobileSearchToggled, setMobileSearchToggled] = useState(0);

    const [comboItemSelected, setComboItemSelected] = useState(0);
    const listBoxId = 'SearchListBox';
    const mainMeuOpen = props.mainMeuOpen;

    
    const submit = (e) => {
        e.preventDefault();
        setSearchingFor(prodSearch.current.value);
        toggleSearch(0);
    }
        
    const resetSearch = () => {
        setSearchingFor(null);
        prodSearch.current.value = '';
        setMobileSearchToggled(0);
    }

    useEffect(() => {
        if (bodyClick) {
            setBodyClick(0);
            if (prodSearch.current.value) {
                setSearchingFor(null);
                
                // prodSearch.current.value = '';
            }
        }
    }, [bodyClick, setBodyClick]);

    function toggleSearch() {
        
        setMobileSearchToggled(1);
        
    }

    useEffect(() => {
        if (mobileSearchToggled) {
            searchInput.current.focus(); 
        }

    }, [mobileSearchToggled])
    
    useEffect(() => {
        if (mobileSearchToggled &&  mainMeuOpen === 1) {
            resetSearch();
        }

    },[ mainMeuOpen, mobileSearchToggled])

    

    
    return (
        
        <> 
            <div className={"search-container" + (mobileSearchToggled ? " mobile-search-toggled" : "")}
                role="combobox"
                aria-haspopup="listbox"
                aria-expanded={searchingFor && searchingFor.length ? 'true' : 'false'}
                aria-owns="SearchListBox"    
            >
                <SearchForm
                    searchInput={searchInput}
                    label="Search Podcasts Shows"
                    submit={submit}
                    pHolderText={'Search...'}
                    listBoxId={listBoxId}
                    comboItemSelected={comboItemSelected}
                    setComboItemSelected = {setComboItemSelected}
                >
                    
                    <button  className="search-icon mobileSearchToggle" onClick={toggleSearch}>
                        <IoSearchSharp />
                    </button>
                    <span className='search-icon standard-search-icon'>
                        <IoSearchSharp />
                    </span>

                </SearchForm>

                <SearchBarRes
                    searchingFor = {searchingFor}
                    resetSearch = {resetSearch}
                    listBoxId = {listBoxId}
                    comboItemSelected = {comboItemSelected}
                    setComboItemSelected = {setComboItemSelected}
                />
            </div>
            </>
    )
};

export default SearchBar;