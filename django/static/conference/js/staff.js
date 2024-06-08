document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('edit_section_info_btn').addEventListener('click', compose_section_info_edit);
    document.getElementById('submit_section_info_btn').addEventListener('click', submit_section_info);
    document.getElementById('cansel_section_info_btn').addEventListener('click', cansel_section_info);
    document.getElementById('filter_btn').addEventListener('click', search_article);

    document.getElementById('filter_all').addEventListener('click', (event) => {
        check_all(event.target);
    });
    document.getElementById('filter_winners').addEventListener('click', (event) => {
        check_winners(event.target);
    });
    document.getElementById('filter_unapproved').addEventListener('click', (event) => {
        check_unapproved(event.target);
    });
    document.getElementById('filter_edited').addEventListener('click', (event) => {
        check_edited(event.target);
    });
    document.getElementById('filter_rejected').addEventListener('click', (event) => {
        check_rejected(event.target);
    });

    add_checked_event_listeners();
    set_up_filter();
    search_article();
});


function compose_section_info_edit() {
    const section = document.getElementById('section').innerHTML;

    const edit_section = document.getElementById('edit_section');
    edit_section.disabled = false;
    const section_options = edit_section.getElementsByTagName('option');
    if (section === '') {
        for (option of section_options) {
            option.selected = option.value === 'None';
        }
    } else {
        for (option of section_options) {
            console.log(option.value)
            option.selected = option.innerHTML === section;
        }
    }

    document.getElementById('section_info').hidden = true;
    document.getElementById('edit_section_info_wrapper').hidden = false;
}


function submit_section_info() {
    const values = get_values_dict_from_objects_ids_list(['edit_section']);

    fetch('/edit_section_info', {
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
                location.reload()
                // complete_edit_section(data.editor);
            }
        });
}


function cansel_section_info() {
    document.getElementById('edit_section_info_wrapper').hidden = true;
    document.getElementById('section_info').hidden = false;

    document.getElementById('edit_section').disabled = true;
}

function complete_edit_section(data) {
    document.getElementById('section').innerHTML = data.section;

    document.getElementById('edit_section_info_wrapper').hidden = true;
    document.getElementById('section_info').hidden = false;

    disable_nodes(['edit_section']);
}


function search_article() {
    const values = get_checked_dict_from_objects_ids_list(['filter_all', 'filter_winners', 'filter_unapproved', 'filter_edited', 'filter_rejected'])

    fetch('/search_articles', {
        method: 'POST',
        mode: 'same-origin',
        headers: {
            'X-CSRFToken': CSRFTOKEN
        },
        body: JSON.stringify(values)
    })
        .then(response => response.json())
        .then(data => {
            remove_node_by_id('items_wrapper');
            const base_node = create_div_with_id(document.getElementById('articles_container'), 'items_wrapper');

            if (data.items.length === 0) {
                compose_filler(base_node, "Подходящие доклады не найдены");
            }
            else {
                compose_count_of_found(base_node, data.items.length);
            }

            for (item of data.items) {
                compose_article_item(base_node, item);
            }
            save_filter();
        });
}


function check_no_one_checked() {
    for (item of ['filter_all', 'filter_winners', 'filter_unapproved', 'filter_edited', 'filter_rejected']) {
        if (document.getElementById(item).checked) {
            return;
        }
    }
    document.getElementById('filter_all').checked = true;
}


function check_edited(target) {
    if (target.checked) {
        for (item of ['filter_all', 'filter_unapproved']) {
            document.getElementById(item).checked = false;
        }
    }

}


function check_unapproved(target) {
    if (target.checked) {
        for (item of ['filter_all', 'filter_edited']) {
            document.getElementById(item).checked = false;
        }
    }
}


function check_winners(target) {
    if (target.checked) {
        document.getElementById('filter_all').checked = false;
    }
}


function check_rejected(target) {
    if (target.checked) {
        document.getElementById('filter_all').checked = false;
    }
}


function check_all(target) {
    if (target.checked) {
        for (item of ['filter_winners', 'filter_unapproved', 'filter_edited', 'filter_rejected']) {
            document.getElementById(item).checked = false;
        }
    }
}


function add_checked_event_listeners() {
    for (item of ['filter_all', 'filter_winners', 'filter_unapproved', 'filter_edited', 'filter_rejected']) {
        document.getElementById(item).addEventListener('click', check_no_one_checked)
    }
}


function save_filter() {
    const values = get_checked_dict_from_objects_ids_list(['filter_all', 'filter_winners', 'filter_unapproved', 'filter_edited', 'filter_rejected'])
    setCookie('staff_filters', JSON.stringify(values), {secure: true, 'max-age': 60 * 60 * 24 * 3});
}


function set_up_filter() {
    const values = getCookieSmart('staff_filters');
    if (values === undefined) return;

    let cookies = values.split("{")[1];
    cookies = cookies.split("}")[0];
    cookies = cookies.split(",");

    for (msg of cookies) {
        let cookie = msg.replace('"', '');
        cookie = cookie.replace('"', '');
        const temp = cookie.split(":");
        document.getElementById(temp[0]).checked = (temp[1] === "true");
    }
}
