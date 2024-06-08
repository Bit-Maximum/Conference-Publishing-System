document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('edit_secondary_info_btn').addEventListener('click', compose_secondary_info_edit);
    document.getElementById('submit_secondary_info_btn').addEventListener('click', submit_secondary_info);
    document.getElementById('cansel_secondary_info_btn').addEventListener('click', cansel_secondary_info);

    document.getElementById('add_or_edit_consent_btn').addEventListener('click', compose_consent_form);
    document.getElementById('close_consent_form_btn').addEventListener('click', close_consent_form);
});


function compose_secondary_info_edit() {

    const nodes = get_nodes_by_ids_list(['edit_first_name_translation', 'edit_last_name_translation',
                                             'edit_country', 'edit_city', 'edit_institution', 'edit_department',
                                             'edit_department_group', 'edit_major', 'edit_level', 'edit_course',
                                             'edit_education_group']);

    for (node of nodes) {
        node.disabled = false
    }

    const edit_level = document.getElementById('edit_level');
    edit_level.disabled = false;

    if (!document.getElementById('secondary_info_not_provided')) {
        const values = get_inner_html_from_objects_ids_list(['first_name_translation', 'last_name_translation',
            'country', 'city', 'institution', 'department', 'department_group',
            'major', 'level', 'course', 'education_group']);

        for (let i = 0; i < values.length; i++) {
            nodes[i].value = values[i];
        }

        const level = document.getElementById('level').innerHTML;
        if (level === '') {
            const level_options = edit_level.getElementsByTagName('option');
            for (option of level_options) {
                option.selected = option.value === 'None';
            }
        } else {
            const level_options = edit_level.getElementsByTagName('option');
            for (option of level_options) {
                option.selected = option.value === level;
            }
        }
    }

    document.getElementById('secondary_info').hidden = true;
    document.getElementById('edit_secondary_info_wrapper').hidden = false;
}


function submit_secondary_info() {
    const values = get_values_dict_from_objects_ids_list(['edit_first_name_translation', 'edit_last_name_translation',
                                                              'edit_country', 'edit_city', 'edit_institution', 'edit_department',
                                                              'edit_department_group', 'edit_major', 'edit_level', 'edit_course',
                                                              'edit_education_group']);

    fetch('/edit_secondary_info', {
        method: 'PUT',
        mode: 'same-origin',
        headers: {
            'X-CSRFToken': CSRFTOKEN
        },
        body: JSON.stringify(values)
    })
        .then(response => response.json())
        .then(data => {
            if (data.errors) {
                compose_profile_errors(data.errors);
            } else {
                if (document.getElementById('city') === null)
                    location.reload();
                compose_secondary_info(data.user);
            }
        });
}


function compose_secondary_info(a) {
    set_values_to_nodes_list(['first_name_translation', 'last_name_translation',
                                  'country', 'city', 'institution', 'department', 'department_group',
                                  'major', 'level', 'course', 'education_group'],
                            [a.first_name_translation, a.last_name_translation,
                                   a.country, a.city, a.institution, a.department, a.department_group,
                                   a.major, a.level, a.course, a.education_group]);

    disable_nodes(['edit_first_name_translation', 'edit_last_name_translation',
                       'edit_country', 'edit_city', 'edit_institution', 'edit_department',
                       'edit_department_group', 'edit_major', 'edit_level', 'edit_course',
                       'edit_education_group']);

    document.getElementById('edit_secondary_info_wrapper').hidden = true;
    document.getElementById('secondary_info').hidden = false;
}


function cansel_secondary_info() {
    document.getElementById('edit_secondary_info_wrapper').hidden = true;
    document.getElementById('secondary_info').hidden = false;

    disable_nodes(['edit_first_name_translation', 'edit_last_name_translation',
                       'edit_country', 'edit_city', 'edit_institution', 'edit_department',
                       'edit_department_group', 'edit_major', 'edit_level', 'edit_course',
                       'edit_education_group']);
}


function compose_consent_form() {
    document.getElementById('consent_buttons_container').hidden = true;
    document.getElementById('add_consent_form_wrapper').hidden = false;
}


function close_consent_form() {
    document.getElementById('add_consent_form_wrapper').hidden = true;
    document.getElementById('consent_buttons_container').hidden = false;
}
