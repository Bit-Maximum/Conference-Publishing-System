document.addEventListener('DOMContentLoaded', function() {
    new Autocomplete('#autocomplete_title', {
        search: input => {
            if (input.length > 3) {
                const url = `/search_title?title=${input}`;
                return new Promise(resolve => {
                    fetch(url)
                        .then(response => response.json())
                        .then(data => {
                            resolve(data.data)
                        })
                })
            }
        },
        debounceTime: 500
    });

    new Autocomplete('#autocomplete_title_translation', {
        search: input => {
            if (input.length > 3) {
                const url = `/search_title_translation?title=${input}`;
                return new Promise(resolve => {
                    fetch(url)
                        .then(response => response.json())
                        .then(data => {
                            resolve(data.data)
                        })
                })
            }
        },
        debounceTime: 500
    });
});