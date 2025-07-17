document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('add_comment_btn').addEventListener('click', () =>{
        document.getElementById('submit_comment_btn').disabled = false;
        document.getElementById('comment_form_wrapper').hidden = false;
    });

    document.getElementById('cancel_comment_btn').addEventListener('click', () =>{
        document.getElementById('submit_comment_btn').disabled = true;
        document.getElementById('comment_form_wrapper').hidden = true;
    });

    document.getElementById('submit_comment_btn').addEventListener('click', () => {
        toggle_loading('submit_comment_btn', 'loading_comment_send', 5000);
    });

    document.getElementById('submit_reject_btn').addEventListener('click', () => {
        toggle_loading('submit_reject_btn', 'loading_reject_send', 8000);
    });
})


function compose_comment_form() {
    const base = document.getElementById('add_comment_container');
    if (document.getElementById("comment_form_wrapper"))
        return;

    const wrapper = document.createElement('div');
    const form = document.createElement('form');

    const form_group = document.createElement('div');
    const label = document.createElement('label');
    const textarea = document.createElement('textarea');
    const submit_btn = document.createElement('button');
    const cancel_btn = document.createElement('button');

    wrapper.classList.add('wrapper');
    form_group.classList.add('form-group');
    label.classList.add('form-label');
    textarea.classList.add('form-control');
    submit_btn.classList.add('btn', 'btn-primary');
    cancel_btn.classList.add('btn', 'btn-outline');

    textarea.id = 'comment_content';
    textarea.name = 'comment_content';
    textarea.placeholder = 'Что у нас на уме?';

    label.for = 'comment_content';
    submit_btn.id = 'submit_comment_btn';
    cancel_btn.id = 'cancel_comment_btn';

    submit_btn.addEventListener('click', submit_comment);

    form_group.append(label, textarea);
    wrapper.append(form);
    base.append(wrapper, submit_btn, cancel_btn);
}


function submit_comment() {
    fetch('/comment', {
        method: 'POST',
        mode: 'same-origin',
        headers: {
            'X-CSRFToken': CSRFTOKEN
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.errors) {
                compose_article_errors(data.errors);
            }
        });
}