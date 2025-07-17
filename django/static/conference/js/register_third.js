document.addEventListener('DOMContentLoaded', function() {
    // Появление / исчезание формы указания научного руководителя.
    const adviser_block = document.getElementById('adviser_block');
    adviser_block.addEventListener('change', (event) => {
        const wrapper = document.getElementById('adviser_wrapper');
        if (event.currentTarget.checked) {
            adviser_block.value = 'on';
            wrapper.classList.remove('hidden');
            for (let item of wrapper.getElementsByTagName('input')) {
                item.disabled = false;
                item.required = true;
            }
        } else {
            adviser_block.value = 'off';
            wrapper.classList.add('hidden');
            wrapper.getElementsByTagName('input');
            for (let item of wrapper.getElementsByTagName('input')) {
                item.disabled = true;
                item.required = false;
            }
        }
    })

    // Появление / исчезание формы указания соавторов
    const co_authorship = document.getElementById('co_authorship');
    co_authorship.dataset.state = 'off';
    co_authorship.addEventListener('change', (event) => {
        const wrapper = document.getElementById('co_authorship_container');
        if (event.currentTarget.checked) {
            co_authorship.dataset.state = 'on';
            wrapper.classList.remove('hidden');
        } else {
            co_authorship.dataset.state = 'off';
            wrapper.classList.add('hidden');
        }
    });

    // Добавление новой формы указания соавтора
    const add_co_author_btn = document.getElementById('add_co_author_btn');
    let co_author_counter = 0;
    add_co_author_btn.addEventListener('click', (event) => {
        const co_authorship_container = document.getElementById('co_authorship_container');
        if (0 === co_authorship_container.getElementsByClassName('co_author_form_wrapper').length) {
            co_author_counter++;
            document.getElementById('co_authorship').value = co_author_counter;
            compose_co_author_find(co_author_counter);
        }
    });

    // Отправка данных на проверку того, что такая статья уже существует
    document.getElementById('submit_btn').addEventListener('click', (event) => {
        if (document.getElementById('submit_error_wrapper') !== null) {
            document.getElementById('submit_error_wrapper').remove();
        }

        if (document.getElementsByName('section')[0].value === '' || document.getElementsByName('title')[0].value === '') {
            compose_errors({'errors': ['Поля «Секция» и «Тема доклада» должны быть заполнены']});
        } else {
            start_loading('submit_btn');
            fetch('/check_article_exists', {
                method: 'POST',
                mode: 'same-origin',
                headers: {
                    'X-CSRFToken': CSRFTOKEN
                },
                body: JSON.stringify({
                    'section_id': parseInt(document.getElementsByName('section')[0].value),
                    'title': document.getElementsByName('title')[0].value
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        end_loading('submit_btn');
                        if (data.errors) {
                            compose_modal_errors(data.errors, "submit_error", "errors_wrapper", "red");
                        } else {
                            compose_join_form(data.article, data.authors, data.section);
                            setup_join_article_btn(data.article);
                        }
                    } else {
                        if (validate_article()) {
                            register_article();
                            end_loading('submit_btn');
                            }
                        }
                    }
                );
        }
    });
});


function compose_co_author_find(counter) {
    const base = document.getElementById('authorship_items');

    let co_author_wrapper = document.createElement('div');
    co_author_wrapper.classList.add('co_author_wrapper', 'wrapper');
    let form_wrapper = document.createElement('div');
    form_wrapper.classList.add('co_author_form_wrapper');

    let error = document.createElement('div');
    error.classList.add('authorship_error', 'red');
    let form = document.createElement('form');
    form.onsubmit = "return false;"

    let group = document.createElement('div');
    group.classList.add('form-group');
    let top_label = document.createElement('label');
    top_label.classList.add('form-label');
    top_label.for = `co_author_email_${counter}`;
    top_label.innerHTML = 'Укажите e-mail, который соавтор использовал при регистрации. Затем нажмите кнопку «Указать соавтора»';
    let input = document.createElement('input');
    input.classList.add('form-control');
    input.id = `co_author_email_${counter}`;
    input.placeholder = 'e-mail соавтора';
    input.type = 'email';
    input.required = true;

    let form_buttons = document.createElement('div');
    form_buttons.classList.add('form-buttons');
    let close_btn = document.createElement('button');
    close_btn.classList.add('btn', 'btn-secondary');
    close_btn.type = 'button';
    close_btn.innerHTML = 'Отмена';
    close_btn.addEventListener('click', (event) => {
        co_author_wrapper.remove();
    });

    let find_btn = document.createElement('button');
    find_btn.classList.add('btn', 'btn-primary', 'margin_right');
    find_btn.innerHTML = 'Указать соавтора';
    find_btn.type = 'button';
    find_btn.addEventListener('click', (event) => {
        const email = input.value;
        fetch('/find_user', {
            method: 'POST',
            mode: 'same-origin',
            headers: {
                'X-CSRFToken': CSRFTOKEN
            },
            body: JSON.stringify({
                'email': email
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    error.innerHTML = data.error;
                } else {
                    if (document.getElementById(`co_author_id_${data.id}`) === null) {
                        let co_authorship_container = document.getElementById('co_authorship_container');
                        let add_co_author_form = co_authorship_container.getElementsByClassName('co_author_form_wrapper');
                        for (element of add_co_author_form) {
                            element.remove();
                        }
                        let co_author_data_wrapper = document.createElement('div');
                        co_author_data_wrapper.classList.add('co_author_data_wrapper');
                        let co_author_id_wrapper = document.createElement('div');
                        co_author_id_wrapper.classList.add('form-group', 'hidden');
                        let co_author_id = document.createElement('input');
                        co_author_id.classList.add('form-control');
                        co_author_id.type = 'text';
                        co_author_id.name = 'co_author_id';
                        co_author_id.value = data.id;
                        co_author_id.id = `co_author_id_${counter}`;

                        co_author_id_wrapper.append(co_author_id);
                        co_author_data_wrapper.append(co_author_id_wrapper);
                        co_author_data_wrapper.append(wrap_div(['form-control', 'mb-3'], data.last_name));
                        co_author_data_wrapper.append(wrap_div(['form-control', 'mb-3'], data.first_name));
                        if (data.middle_name) co_author_data_wrapper.append(wrap_div(['form-control', 'mb-3'], data.middle_name));

                        let co_author_remove_btn = document.createElement('button');
                        co_author_remove_btn.classList.add('btn', 'btn-secondary');
                        co_author_remove_btn.type = 'button';
                        co_author_remove_btn.innerHTML = 'Удалить соавтора';
                        co_author_remove_btn.addEventListener('click', (event) => {
                            co_author_wrapper.remove();
                        });

                        co_author_data_wrapper.append(co_author_remove_btn);
                        co_author_wrapper.append(co_author_data_wrapper);
                    }
                }
            });
    });

    group.append(top_label, input);
    form_buttons.append(find_btn, find_btn)
    form.append(group, form_buttons);


    form_wrapper.append(error, form);
    co_author_wrapper.append(form_wrapper);
    base.insertBefore(co_author_wrapper, base.firstChild);
}


function register_article() {
    let co_authors_nodes = document.getElementsByName('co_author_id');
    let co_authors_ids = [];
    for (node of co_authors_nodes) {
        co_authors_ids.push(parseInt(node.value));
    }

    fetch('/register_article', {
        method: 'POST',
        mode: 'same-origin',
        headers: {
            'X-CSRFToken': CSRFTOKEN
        },
        body: JSON.stringify({
            'section_id': parseInt(document.getElementsByName('section')[0].value),
            'title': document.getElementsByName('title')[0].value,
            'title_translation': document.getElementsByName('title_translation')[0].value,
            'abstract': document.getElementsByName('abstract')[0].value,
            'abstract_translation': document.getElementsByName('abstract_translation')[0].value,
            'keywords': document.getElementsByName('keywords')[0].value,
            'keywords_translation': document.getElementsByName('keywords_translation')[0].value,
            'grant': document.getElementsByName('grant')[0].value,

            'adviser_block': document.getElementsByName('adviser_block')[0].value,
            'adviser_first_name': document.getElementsByName('adviser_first_name')[0].value,
            'adviser_last_name': document.getElementsByName('adviser_last_name')[0].value,
            'adviser_middle_name': document.getElementsByName('adviser_middle_name')[0].value,
            'adviser_first_name_translation': document.getElementsByName('adviser_first_name_translation')[0].value,
            'adviser_last_name_translation': document.getElementsByName('adviser_last_name_translation')[0].value,
            'adviser_degree': document.getElementsByName('adviser_degree')[0].value,
            'academic_title': document.getElementsByName('academic_title')[0].value,
            'job_title': document.getElementsByName('job_title')[0].value,
            'adviser_job': document.getElementsByName('adviser_job')[0].value,


            'co_authorship': document.getElementById('co_authorship').dataset.state,
            'co_author_id': co_authors_ids
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.errors) {
                compose_errors(data);
            } else {
                location.href = '/profile';
            }
        });
}


// ФУНКЦИЯ НЕ ЗАКОНЧЕНА
function validate_article() {
    const section_id = document.getElementsByName('section')[0].value;
    const title = document.getElementsByName('title')[0].value;
    const title_translation = document.getElementsByName('title_translation')[0].value;
    const abstract = document.getElementsByName('abstract')[0].value;
    const abstract_translation = document.getElementsByName('abstract_translation')[0].value;
    const keywords = document.getElementsByName('keywords')[0].value;
    const keywords_translation = document.getElementsByName('keywords_translation')[0].value;
    const grant = document.getElementsByName('grant')[0].value;

    const adviser_block = document.getElementsByName('adviser_block')[0].value;
    const adviser_first_name = document.getElementsByName('adviser_first_name')[0].value;
    const adviser_last_name = document.getElementsByName('adviser_last_name')[0].value;
    const adviser_middle_name = document.getElementsByName('adviser_middle_name')[0].value;
    const adviser_first_name_translation = document.getElementsByName('adviser_first_name_translation')[0].value;
    const adviser_last_name_translation = document.getElementsByName('adviser_last_name_translation')[0].value;
    const adviser_degree = document.getElementsByName('adviser_degree')[0].value;
    const academic_title = document.getElementsByName('academic_title')[0].value;
    const job_title = document.getElementsByName('job_title')[0].value;
    const adviser_job = document.getElementsByName('adviser_job')[0].value;

    const co_authorship = document.getElementsByName('co_authorship')[0].value;
    const co_author_id = document.getElementsByName('co_author_id').values();

    // ВАЛИДАЦИЯ ВВЕДЁННЫХ ДАННЫХ
    return true;
}

