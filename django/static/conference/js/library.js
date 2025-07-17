document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('search_btn').addEventListener('click', () => {
        start_loading('search_btn');
        delay(1000).then(() => end_loading('search_btn'));
    });
});
