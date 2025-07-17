document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('edit_or_edit_article_text_btn').addEventListener('click',compose_article_text_form);
    document.getElementById('close_article_text_form_btn').addEventListener('click',close_article_text_form);
});


function compose_article_text_form() {
    document.getElementById('file_buttons_container').hidden = true;
    document.getElementById('add_article_text_form_wrapper').hidden = false;
}


function close_article_text_form() {
    document.getElementById('add_article_text_form_wrapper').hidden = true;
    document.getElementById('file_buttons_container').hidden = false;
}

