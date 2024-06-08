document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('add_author_btn').addEventListener('click', show_close_find_user_form);
    document.getElementById('confirm_delete_author_btn').addEventListener('click', confirm_delete_author);
    document.getElementById('refresh_page_btn').addEventListener('click', (event) => {
       location.reload();
    });

    document.getElementById('add_co_author_btn').addEventListener('click', (event) => {
        const email = document.getElementById('email_author').value;
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
                    document.getElementById('find_error').innerHTML = data.error;
                } else {
                    if (document.getElementById(`co_author_id_${data.id}`) === null) {
                        document.getElementById('find_author_container').hidden = true;
                        let co_authorship_container = document.getElementById('co_authorship_container');
                        let add_co_author_form = co_authorship_container.getElementsByClassName('co_author_form_wrapper');
                        for (element of add_co_author_form) {
                            element.remove();
                        }
                        let co_author_data_wrapper = document.createElement('div');
                        co_author_data_wrapper.classList.add('co_author_data_wrapper');
                        let co_author_id_wrapper = document.createElement('div');
                        co_author_id_wrapper.classList.add('form-group');
                        co_author_id_wrapper.hidden = true;
                        let co_author_id = document.createElement('div');
                        co_author_id.classList.add('form-control');
                        co_author_id.type = 'text';
                        co_author_id.name = 'co_author_id';
                        co_author_id.id = `co_author_id_${data.id}`;

                        co_author_id_wrapper.append(co_author_id);
                        co_author_data_wrapper.append(co_author_id_wrapper);
                        co_author_data_wrapper.append(wrap_div(['form-control', 'mb-3'], data.last_name));
                        co_author_data_wrapper.append(wrap_div(['form-control', 'mb-3'], data.first_name));
                        if (data.middle_name) co_author_data_wrapper.append(wrap_div(['form-control', 'mb-3'], data.middle_name));

                        let co_author_submit_btn = document.createElement('button');
                        co_author_submit_btn.classList.add('btn', 'btn-primary', 'margin_right');
                        co_author_submit_btn.type = 'button';
                        co_author_submit_btn.innerHTML = 'Добавить соавтора';
                        co_author_submit_btn.id = 'submit_author_btn';
                        co_author_submit_btn.addEventListener('click', (event) => {
                            start_loading('submit_author_btn', 'loading_submit');
                            const article_id = document.getElementById('find_author_container').dataset.article_id
                            fetch(`/edit_authorship/${article_id}`, {
                                method: 'PUT',
                                mode: 'same-origin',
                                headers: {
                                    'X-CSRFToken': CSRFTOKEN
                                },
                                body: JSON.stringify({
                                    'user_id': data.id
                                })
                            })
                                .then(response => response.json())
                                .then(data => {
                                    end_loading('submit_author_btn', 'loading_submit');
                                    if (!data.success) {
                                        document.getElementById('find_error').innerHTML = data.error;
                                    } else {
                                        document.getElementById('modal_add_btn').click();
                                    }
                                });
                        });

                        let load = document.createElement('div');
                        load.classList.add('spinner-border', 'm-3');
                        load.role = 'status';
                        load.id = 'loading_submit';
                        load.hidden = true;
                        let load_widget = document.createElement('span');
                        load_widget.classList.add('visually-hidden');
                        load_widget.innerHTML = 'Loading...';

                        load.append(load_widget);

                        let co_author_remove_btn = document.createElement('button');
                        co_author_remove_btn.classList.add('btn', 'btn-secondary');
                        co_author_remove_btn.type = 'button';
                        co_author_remove_btn.innerHTML = 'Отмена';
                        co_author_remove_btn.addEventListener('click', (event) => {
                            document.getElementById('find_author_container').hidden = false;
                            co_author_wrapper.remove();
                        });

                        co_author_data_wrapper.append(co_author_submit_btn, load , co_author_remove_btn);
                        document.getElementById('authorship_items').append(co_author_data_wrapper);
                    }
                }
            });
    });
});


function show_close_find_user_form() {
    if (document.getElementById('co_authorship_container').hidden) {
        document.getElementById('email_author').disabled = false;
        document.getElementById('co_authorship_container').hidden = false;
    } else {
        document.getElementById('email_author').disabled = true;
        document.getElementById('co_authorship_container').hidden = true;
    }
}


function remove_author(user_id) {
    document.getElementById('modal_full_name').innerHTML = document.getElementById(`full_name_${user_id}`).innerHTML;
    document.getElementById('delete_user_info').dataset.user_id = user_id;
}


function confirm_delete_author() {
    start_loading('confirm_delete_author_btn', 'loading_delete');
    const dataset = document.getElementById('delete_user_info').dataset;
    fetch(`/edit_authorship/${dataset.article_id}`, {
        method: 'DELETE',
        mode: 'same-origin',
        headers: {
            'X-CSRFToken': CSRFTOKEN
        },
        body: JSON.stringify({
            'user_id': dataset.user_id
        })
    })
        .then(response => response.json())
        .then(data => {
            end_loading('confirm_delete_author_btn', 'loading_delete');
            if (!data.success) {
                document.getElementById('deletion_error').innerHTML = data.error;
            } else {
                location.reload();
            }
        });
}
