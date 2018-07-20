var searchResults = document.getElementById('search-results');
var searchResultsCount = 0;
var resultIndex = -1;
var searchSpinner = document.getElementById('search-spinner');
var iconSearch = document.getElementById('search-icon');
var searchTimeout;
function callAjax(url, callback){
    var xmlhttp;
    // compatible with IE7+, Firefox, Chrome, Opera, Safari
    xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function(){
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200){
            callback(xmlhttp.responseText);
        }
    }
    xmlhttp.open("GET", url, true);
    xmlhttp.send();
}

var search_index;
var search_tokens;

function onBlur() {setTimeout(function(){searchResults.style.display = 'none';}, 100);}

function onSearch(e) {
    var query = e.value;
    if (query.length < 2) {
        searchResults.style.display = 'none';
        return;
    }
    searchResults.style.display = 'block';
    
    searchSpinner.style.display = 'block';
    iconSearch.style.display = 'none';
    if (searchTimeout) {clearTimeout(searchTimeout); searchTimeout = null;}
    searchTimeout = setTimeout(function () {searchSpinner.style.display='none';iconSearch.style.display='block'; searchTimeout=null;}, 500);
    
    if (search_index) search(query);
    else callAjax(EDC_SRC + '/index.json', function(data) {
        search_index = JSON.parse(data);
        var ts = search_index.tokens;
        search_tokens = Object.keys(ts).sort(function(a,b) {
            return ts[a].length > ts[b].length?-1:1; 
        });
        search(query);
    })
}

function onKeyUp(e) {
    if (!searchResultsCount) return;
    if (e.key=='ArrowUp' || e.key=='ArrowDown') {
        if (resultIndex >= 0) searchResults.children[resultIndex].className = 'home-link';
        if (e.key=='ArrowUp') {
            resultIndex--;
            if (resultIndex < 0) resultIndex = searchResultsCount - 1;
        }
        else {
            resultIndex++;
            if (resultIndex >= searchResultsCount) resultIndex = 0;
        }
        searchResults.children[resultIndex].className = 'home-link active';
    }
        
    if (e.key=='Enter') {
        if (resultIndex >= 0) searchResults.children[resultIndex].click();
    }
}

function search(query) {
    var terms = query.toLowerCase().split(/\s/);
    var last_term = terms.pop();
    var token_items = [];
    for (var i in terms) {
        if (search_index.tokens[terms[i]]) token_items.push(search_index.tokens[terms[i]].split(' '));
    }
    if (last_term.length > 1) {
        var last_terms = [];
        var r = new RegExp('\\s(' + last_term + '.*?)\\s', 'g');
        var glossary = ' ' + search_tokens.join(' ') + ' ';
        var suggestions = (glossary.match(r) || []).map(function (e) {
            return e.trim();
        });
        for (var i in suggestions) {
            var docs = search_index.tokens[suggestions[i]].split(' ');
            for (var j in docs) if (last_terms.indexOf(docs[j])<0) last_terms.push(docs[j]);
        }
        if (last_terms.length) token_items.push(last_terms);
    } else {
       if (search_index.tokens[last_term]) token_items.push(search_index.tokens[last_term].split(' ')); 
    }

    //intersect lists
    var longest = [];
    for (var i in token_items) {
        var docs = token_items[i];
        if (docs.length > longest.length) longest = docs;
    }
    var token_hist = {};
    for (var i in token_items) {
        var docs = token_items[i];
        for (var j in docs) token_hist[docs[j]] = (token_hist[docs[j]] || 0) + 1;
    }
    var res = [], min_matches=token_items.length;
    while (res.length < 15 && min_matches>0) {
        for (var i in longest) {
            if (token_hist[longest[i]] == min_matches) {
                var item = search_index.items[longest[i]];
                if (res.length <= 14) res.push('<a class="home-link" href="/docs/' + item.p + '">'+ item.n + "</a>");
            }
        }
        min_matches--;
    }
    searchResultsCount = res.length; resultIndex = -1;
    if (res.length) searchResults.innerHTML = res.join('');
    else searchResults.innerHTML = "<small class='search-no-results'>No results found</small>";
}