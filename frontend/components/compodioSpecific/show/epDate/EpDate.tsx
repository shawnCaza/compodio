
interface epDate{
    dtStr:string
}

function EpDate({dtStr}:epDate) {
    // sanitize dtStr for ios
    const ios_valid_dtStr = dtStr.replace(/-/g, '/');
    var dt:Date = new Date(ios_valid_dtStr);
    const opts: Intl.DateTimeFormatOptions = { weekday: 'long', year: 'numeric', month: 'short', day: 'numeric' };
    const dtFormated = dt.toLocaleDateString('en-US', opts);

    return (
        <>
            {dtFormated}
        </>
    )
} 

export default EpDate;