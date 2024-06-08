document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('edit_general_info_btn').addEventListener('click', compose_general_info_edit);
    document.getElementById('submit_general_info_btn').addEventListener('click', submit_general_info);
    document.getElementById('cansel_general_info_btn').addEventListener('click', cansel_general_info);

    document.getElementById('confirm_email_btn').addEventListener('click', resend_email_verification);
});


function compose_profile_errors(errors) {
    let container = document.getElementById('edit_profile_error_container');

    for (error of errors) {
        let e = document.createElement('div');
        e.classList.add('error', 'red');
        e.innerHTML = error;
        container.append(e);
        }
}


function compose_general_info_edit() {
    const first_name = document.getElementById('first_name').innerHTML;
    const last_name = document.getElementById('last_name').innerHTML;
    const middle_name = document.getElementById('middle_name').innerHTML;

    const edit_first_name = document.getElementById('edit_first_name');
    const edit_last_name = document.getElementById('edit_last_name');
    const edit_middle_name = document.getElementById('edit_middle_name');

    edit_first_name.value = first_name;
    edit_last_name.value = last_name;
    edit_middle_name.value = middle_name;

    edit_first_name.disabled = false;
    edit_last_name.disabled = false;
    edit_middle_name.disabled = false;

    document.getElementById('general_info').hidden = true;
    document.getElementById('edit_general_info_wrapper').hidden = false;
}


function submit_general_info() {
    const edit_first_name = document.getElementById('edit_first_name');
    const edit_last_name = document.getElementById('edit_last_name');
    const edit_middle_name = document.getElementById('edit_middle_name');

    if (edit_first_name.value === '' || edit_last_name.value === '') {
        compose_profile_errors(['Поля «Имя» и «Фамилия» должны быть заполнены.']);
    } else {
        fetch('/edit_general_info', {
            method: 'PUT',
            mode: 'same-origin',
            headers: {
                'X-CSRFToken': CSRFTOKEN
            },
            body: JSON.stringify({
                'first_name': edit_first_name.value,
                'last_name': edit_last_name.value,
                'middle_name': edit_middle_name.value,
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.errors) {
                    compose_profile_errors(data.errors);
                } else {
                    compose_general_info(data.user);
                }
            });
    }
}


function compose_general_info(user) {
    document.getElementById('first_name').innerHTML = user.first_name;
    document.getElementById('last_name').innerHTML = user.last_name;
    document.getElementById('middle_name').innerHTML = user.middle_name;

    document.getElementById('edit_first_name').disabled = true;
    document.getElementById('edit_last_name').disabled = true;
    document.getElementById('edit_middle_name').disabled = true;

    document.getElementById('edit_general_info_wrapper').hidden = true;
    document.getElementById('general_info').hidden = false;
}

function cansel_general_info() {
    document.getElementById('edit_general_info_wrapper').hidden = true;
    document.getElementById('general_info').hidden = false;

    document.getElementById('edit_first_name').disabled = true;
    document.getElementById('edit_last_name').disabled = true;
    document.getElementById('edit_middle_name').disabled = true;
}


function resend_email_verification() {
    start_loading('confirm_email_btn', 'loading_email');
    fetch('/resend_email', {
        method: 'PUT',
        mode: 'same-origin',
        headers: {
            'X-CSRFToken': CSRFTOKEN
        }
    })
        .then(response => response.json())
        .then(data => {
            end_loading('confirm_email_btn', 'loading_email');
            if (data.success) {
                document.getElementById('email_alert').classList.remove('alert-danger');
                document.getElementById('email_alert').classList.add('alert-success');
                document.getElementById('email_info').innerHTML = 'На ваш e-mail отправлено письмо с инструкцией для завершения регистрации.';
                document.getElementById('confirm_email_btn_container').remove();
            } else {
                document.getElementById('email_info').innerHTML = 'Произошла ошибка при повторной отправке подтверждения. Попробуйте ещё раз позже.';
                document.getElementById('confirm_email_btn').disabled = false;
            }
        });
}
