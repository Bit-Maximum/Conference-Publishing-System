document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('edit_article_info_btn').addEventListener('click', compose_article_info_edit);
    document.getElementById('submit_article_info_btn').addEventListener('click', submit_article_info);
    document.getElementById('cansel_article_edit_btn').addEventListener('click', close_article_info);

    document.getElementById('add_source_form_btn').addEventListener('click', compose_source_form);
    document.getElementById('close_source_form_btn').addEventListener('click', close_source_form);

    document.getElementById('add_or_edit_thesis_btn').addEventListener('click', compose_thesis_form);
    document.getElementById('close_thesis_form_btn').addEventListener('click', close_thesis_form);

    document.getElementById('thesis_submit_btn').addEventListener('click', (event) => {
        toggle_loading("thesis_submit_btn", "loading_thesis_send", 5000);
    });

    document.getElementById('edit_or_edit_article_text_btn').addEventListener('click', compose_article_text_form);
    document.getElementById('close_article_text_form_btn').addEventListener('click', close_article_text_form);

    document.getElementById('article_submit_btn').addEventListener('click', (event) => {
        toggle_loading("article_submit_btn", "loading_article_send", 5000);
    });
});


function compose_article_info_edit() {
    const values = get_inner_html_from_objects_ids_list(['title', 'title_translation',
        'abstract', 'abstract_translation', 'keywords', 'keywords_translation', 'grant',
        'adviser_last_name', 'adviser_first_name', 'adviser_middle_name',
        'adviser_last_name_translation', 'adviser_first_name_translation', 'adviser_degree', 'academic_title', 'job_title', 'adviser_job']);

    const nodes = get_nodes_by_ids_list(['edit_title', 'edit_title_translation',
        'edit_abstract', 'edit_abstract_translation', 'edit_keywords', 'edit_keywords_translation', 'edit_grant',
        'edit_adviser_last_name', 'edit_adviser_first_name', 'edit_adviser_middle_name',
        'edit_adviser_last_name_translation', 'edit_adviser_first_name_translation', 'edit_adviser_degree', 'edit_academic_title', 'edit_job_title', 'edit_adviser_job']);

    for (node of nodes) {
        node.disabled = false
    }

    for (let i = 0; i < values.length; i++) {
        nodes[i].value = values[i];
    }

    const section = document.getElementById('section');
    const edit_section = document.getElementById('edit_section');
    edit_section.disabled = false;
    if (section.innerHTML === '') {
        const section_options = edit_section.getElementsByTagName('option');
        for (option of section_options) {
            option.selected = option.value === 'None';
        }
    } else {
        const section_options = edit_section.getElementsByTagName('option');
        for (option of section_options) {
            option.selected = option.value === section.dataset.section;
        }
    }

    document.getElementById('article_info').hidden = true;
    document.getElementById('edit_article_info_wrapper').hidden = false;
}


function submit_article_info() {
    start_loading('submit_article_info_btn', 'loading_article');
    const values = get_values_dict_from_objects_ids_list(['article_id', 'edit_section' , 'edit_title', 'edit_title_translation',
        'edit_abstract', 'edit_abstract_translation', 'edit_keywords', 'edit_keywords_translation', 'edit_grant',
        'edit_adviser_last_name', 'edit_adviser_first_name', 'edit_adviser_middle_name',
        'edit_adviser_last_name_translation', 'edit_adviser_first_name_translation', 'edit_adviser_degree', 'edit_academic_title', 'edit_job_title', 'edit_adviser_job']);

    fetch('/edit_article_info', {
        method: 'PUT',
        mode: 'same-origin',
        headers: {
            'X-CSRFToken': CSRFTOKEN
        },
        body: JSON.stringify(values)
    })
        .then(response => response.json())
        .then(data => {
            end_loading('submit_article_info_btn', 'loading_article');
            if (data.errors) {
                compose_article_errors(data.errors);
            } else {
                compose_article_info(data.article);
            }
        });
}


function compose_article_info(a) {
    set_values_to_nodes_list(['section', 'title', 'title_translation',
            'abstract', 'abstract_translation', 'keywords', 'keywords_translation', 'grant',
            'adviser_last_name', 'adviser_first_name', 'adviser_middle_name',
            'adviser_last_name_translation', 'adviser_first_name_translation', 'adviser_degree', 'academic_title', 'job_title', 'adviser_job'],
        [a.section, a.title, a.title_translation,
            a.abstract, a.abstract_translation, a.keywords, a.keywords_translation, a.grant,
            a.adviser_last_name, a.adviser_first_name, a.adviser_middle_name,
            a.adviser_last_name_translation, a.adviser_first_name_translation, a.adviser_degree, a.academic_title, a.job_title, a.adviser_job]);

    disable_nodes(['edit_section' , 'edit_title', 'edit_title_translation',
        'edit_abstract', 'edit_abstract_translation', 'edit_keywords', 'edit_keywords_translation', 'edit_grant',
        'edit_adviser_last_name', 'edit_adviser_first_name', 'edit_adviser_middle_name',
        'edit_adviser_last_name_translation', 'edit_adviser_first_name_translation', 'edit_adviser_degree', 'edit_academic_title', 'edit_job_title', 'edit_adviser_job']);

    document.getElementById('section').dataset.section = a.section_id;

    document.getElementById('edit_article_info_wrapper').hidden = true;
    document.getElementById('article_info').hidden = false;
}


function compose_article_errors(errors) {
    let container = document.getElementById('edit_article_error_container');

    for (error of errors) {
        let e = document.createElement('div');
        e.classList.add('error', 'red');
        e.innerHTML = error;
        container.append(e);
    }
}


function close_article_info() {
    document.getElementById('edit_article_info_wrapper').hidden = true;
    document.getElementById('article_info').hidden = false;

    disable_nodes(['edit_section' , 'edit_title', 'edit_title_translation',
        'edit_abstract', 'edit_abstract_translation', 'edit_keywords', 'edit_keywords_translation', 'edit_grant',
        'edit_adviser_last_name', 'edit_adviser_first_name', 'edit_adviser_middle_name',
        'edit_adviser_last_name_translation', 'edit_adviser_first_name_translation', 'edit_adviser_degree', 'edit_academic_title', 'edit_job_title', 'edit_adviser_job']);
}


function compose_source_form() {
    document.getElementById('add_source_form_btn').hidden = true;
    document.getElementById('add_source_form_wrapper').hidden = false;
}


function close_source_form() {
    document.getElementById('add_source_form_wrapper').hidden = true;
    document.getElementById('add_source_form_btn').hidden = false;
}


function toggle_source_remove_modal(source_id) {
    // document.getElementById('delete_source_btn').dataset.source_id = source_id;

    let url = document.getElementById('delete_source_url').href.split('/').slice(0, -1).join('/');
    url = url + `/${source_id}`;
    document.getElementById('delete_source_url').href = url;
}


function compose_thesis_form() {
    document.getElementById('thesis_buttons_container').hidden = true;
    document.getElementById('add_thesis_form_wrapper').hidden = false;
}


function close_thesis_form() {
    document.getElementById('add_thesis_form_wrapper').hidden = true;
    document.getElementById('thesis_buttons_container').hidden = false;
}


function compose_article_text_form() {
    document.getElementById('article_text_buttons_container').hidden = true;
    document.getElementById('add_article_text_form_wrapper').hidden = false;
}


function close_article_text_form() {
    document.getElementById('add_article_text_form_wrapper').hidden = true;
    document.getElementById('article_text_buttons_container').hidden = false;
}