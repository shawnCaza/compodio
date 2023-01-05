
interface epDate{
    dtStr:string
}

function EpDate({dtStr}:epDate) {
    var dt:Date = new Date(dtStr);
    const opts: Intl.DateTimeFormatOptions = { weekday: 'long', year: 'numeric', month: 'short', day: 'numeric' };
    const dtFormated = dt.toLocaleDateString('en-US', opts);
    
    return (
        <>
            {dtFormated}
        </>
    )
} 

export default EpDate;