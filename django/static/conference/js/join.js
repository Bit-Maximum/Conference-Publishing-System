document.addEventListener('DOMContentLoaded', function() {

    // Отправка данных на проверку того, что такая статья уже существует
    document.getElementById('submit_btn').addEventListener('click', (event) => {
        if (document.getElementById('submit_error_wrapper') !== null) {
            document.getElementById('submit_error_wrapper').remove();
            console.log(document.getElementById('submit_error_wrapper'));
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
                    end_loading('submit_btn');
                    if (data.success) {
                        compose_join_form(data.article, data.authors, data.section, 'Статья найдена');
                        setup_join_article_btn(data.article);
                    } else {
                        if (data.errors) {
                            compose_errors(data);
                        }
                    }
                });
        }
    });
});