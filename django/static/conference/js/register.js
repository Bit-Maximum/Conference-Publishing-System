
function compose_join_form(article, authors, section, header='Такой доклад уже зарегистрирован') {
    document.getElementById('staticBackdropLabel').innerHTML = header;
    document.getElementById('modal_body_title').innerHTML = `Тема: ${article.title}`;
    document.getElementById('modal_body_section').innerHTML = `Секция: ${section.content}`;
    document.getElementById('modal_body_keywords').innerHTML = `Ключевые слова: ${article.keywords}`;

    const to_delete = document.getElementById('modal_authors_container');
    if (to_delete)
        to_delete.remove();

    const modal_authors_container = document.createElement('div');
    modal_authors_container.id = 'modal_authors_container'

    const modal_body_authors_header = document.createElement('div');
    modal_body_authors_header.classList.add('modal_body_authors_header');
    modal_body_authors_header.innerHTML = 'Авторы:';
    modal_authors_container.append(modal_body_authors_header);

    const modal_list_wrapper = document.createElement('ul');
    modal_list_wrapper.classList.add('wrapper');
    modal_authors_container.append(modal_list_wrapper);

    for (author of authors) {
        const modal_body_author_wrapper = document.createElement('li');
        const last_name = document.createElement('span');
        const first_name = document.createElement('span');
        const middle_name = document.createElement('span');

        modal_body_author_wrapper.classList.add('list_wrapper');
        last_name.classList.add('full_name');
        first_name.classList.add('full_name');
        middle_name.classList.add('full_name');

        last_name.innerHTML = author.last_name + ' ';
        first_name.innerHTML = author.first_name + ' ';
        middle_name.innerHTML = author.middle_name;

        modal_body_author_wrapper.append(last_name, first_name, middle_name);
        modal_list_wrapper.append(modal_body_author_wrapper);
        modal_authors_container.append(modal_list_wrapper);
    }
    document.getElementById('modal_body_authors').append(modal_authors_container);
    document.getElementById('modal_btn_first').click();
}


function compose_errors(data) {
    let submit_error = document.getElementById('submit_error');
    let submit_error_wrapper = document.createElement('div');
    submit_error_wrapper.classList.add('submit_error_wrapper');
    submit_error_wrapper.id = 'submit_error_wrapper';
    for (error of data.errors) {
        const x = document.createElement('div');
        x.classList.add('error_container');
        const er = document.createElement('div');
        er.classList.add('error', 'red');
        er.innerHTML = error;
        x.append(er);
        submit_error_wrapper.append(x);
        submit_error.append(submit_error_wrapper);
    }
}


function setup_join_article_btn(article) {
    let btn = document.getElementById('join_article_btn');
    btn.replaceWith(btn.cloneNode(true));
    btn = document.getElementById('join_article_btn');
    btn.addEventListener('click', (event) => {
        start_loading('join_article_btn', 'loading_modal');
        fetch('/join_article', {
            method: 'PUT',
            mode: 'same-origin',
            headers: {
                'X-CSRFToken': CSRFTOKEN
            },
            body: JSON.stringify({
                'article_id': article.id
            })
        })
            .then(response => response.json())
            .then(data => {
                end_loading('join_article_btn', 'loading_modal');
                if (!data.success) {
                    document.getElementById('join_error').innerHTML = data.error;
                } else {
                    document.getElementById('modal_btn_second').click();
                }
            });
    });
}
