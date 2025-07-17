document.addEventListener('DOMContentLoaded', () => {
    check_technical_works();

    document.getElementById('toast_close').addEventListener('click', () => {
        setCookie('technical_work_check', true, {secure: true, 'max-age': 60 * 60 * 24});
    });
});


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function compose_inputs(base_node, names, labels=[], type='text') {
    if (type === 'select') {

    } else {
        for (let i = 0; i < names.length; i++) {
            const group = document.createElement('div');
            const label = document.createElement('label');
            const input = document.createElement('input');

            group.classList.add('form-group');
            label.classList.add('form-label');
            input.classList.add('form-control');

            input.name = input.id = names[i];
            input.type = type;

            label.for = names[i];
            label.innerHTML = labels.length? labels[i] : '';

            group.append(label, input);
            base_node.append(group);
        }
    }
}


function create_compose_inputs(base_node, data) {
    for (const [key, dict] of Object.entries(data)) {
        for (const [field, values] of Object.entries(dict)) {
            const node = document.createElement('div');
            node.classList.add(`${key}_${field}_wrapper`);
            compose_inputs(node, values.names, values.labels, values.type);
            base_node.append(node);
        }
    }
}


function compose_custom_input(element, type='text', nullable=false, tag='input', label_top='', label_bottom='') {
    const x = document.createElement('div');
    x.classList.add('form-group mb-3');

    const el = document.createElement(tag);
    el.classList.add('form-control');
    el.type = type;
    el.name = element;
    el.value = document.getElementById(element).innerHTML;

    if (label_top !== '')
    {
        const top = document.createElement('label');
        top.for = el;
        top.innerHTML = label_top;
        x.append(top);
    }
    x.append(el);

    if (label_bottom !== '')
    {
        const bottom = document.createElement('label');
        bottom.for = el;
        bottom.innerHTML = label_top;
        x.append(bottom);
    }

    if (nullable) {
        const label = document.createElement('label');
        label.classList.add('form-label');
        label.for = el.name;
        label.innerHTML = '*если есть';
        el.append(label);
    }
    return x;
}


function compose_input_with_value(element, data, type='text', tag='input', hidden=false, label_top='', label_bottom='') {
    const x = document.createElement('div');
    x.classList.add('form-group mb-3');

    const el = document.createElement(tag);
    el.classList.add('form-control');
    if (hidden) el.classList.add('hidden');
    el.type = type;
    el.name = element;
    el.value = data;

    if (label_top !== '')
    {
        const top = document.createElement('label');
        top.for = el;
        top.innerHTML = label_top;
        x.append(top);
    }
    x.append(el);

    if (label_bottom !== '')
    {
        const bottom = document.createElement('label');
        bottom.for = el;
        bottom.innerHTML = label_top;
        x.append(bottom);
    }
    return x;
}


function get_inner_html_from_objects_ids_list(ids) {
    let inner_html_list = [];
    for (id of ids) {
        inner_html_list.push(document.getElementById(id).innerHTML);
    }
    return inner_html_list;
}


function get_nodes_by_ids_list(ids) {
    let nodes = [];
    for (id of ids) {
        nodes.push(document.getElementById(id));
    }
    return nodes;
}


function get_values_dict_from_objects_ids_list(ids) {
    const values = {};
    for (id of ids) {
        values[id] = document.getElementById(id).value;
    }
    return values;
}


function get_checked_dict_from_objects_ids_list(ids) {
    const values = {};
    for (id of ids) {
        values[id] = document.getElementById(id).checked;
    }
    return values;
}


function get_values_dict_from_objects_names_list(names) {
    const values = {};
    for (n of names) {
        values[n] = document.getElementsByName(n)[0].value;
    }
    return values;
}


function set_values_to_nodes_list(ids, values) {
    for (let i = 0; i < ids.length; i++) {
        if (values[i] === null) {
            document.getElementById(ids[i]).innerHTML = '';
        } else {
            document.getElementById(ids[i]).innerHTML = values[i];
        }
    }
}


function disable_nodes(ids) {
    for (id of ids) {
        document.getElementById(id).disabled = true;
    }
}


function enable_nodes(ids) {
    for (id of ids) {
        document.getElementById(id).disabled = false;
    }
}


function wrap_div(classes, inner_html) {
    const x = document.createElement('div');
    x.classList.add('form-group');

    const el = document.createElement('div');
    for (_class of classes) {
        el.classList.add(_class);
        el.innerHTML = inner_html;
    }
    x.append(el);
    return x;
}


function start_loading(btn_id, loading_id='loading') {
    document.getElementById(btn_id).hidden = true;
    document.getElementById(loading_id).hidden = false;
}


function end_loading(btn_id, loading_id='loading') {
    document.getElementById(loading_id).hidden = true;
    document.getElementById(btn_id).hidden = false;
}


function delay(time) {
    return new Promise(resolve => setTimeout(resolve, time));
}


function getCookieSmart(name) {
    let matches = document.cookie.match(new RegExp(
        "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
}


function setCookie(name, value, options = {}) {

    options = {
        path: '/',
        ...options
    };

    if (options.expires instanceof Date) {
        options.expires = options.expires.toUTCString();
    }

    let updatedCookie = encodeURIComponent(name) + "=" + encodeURIComponent(value);

    for (let optionKey in options) {
        updatedCookie += "; " + optionKey;
        let optionValue = options[optionKey];
        if (optionValue !== true) {
            updatedCookie += "=" + optionValue;
        }
    }

    document.cookie = updatedCookie;
}


function deleteCookie(name) {
    setCookie(name, "", {
        'max-age': -1
    })
}


function check_technical_works() {
    if (getCookieSmart('technical_work_check') !== undefined) return;

    fetch('/check_technical_work', {
        method: 'GET',
        mode: 'same-origin'
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                show_toast(data.work);
            } else {
                setCookie('technical_work_check', true, {secure: true, 'max-age': 60 * 60 * 24});
            }
        });
}


function show_toast(work, node_id='toast') {
    const toast = document.getElementById(node_id);
    const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toast);

    const startDate = new Date(work.start);
    const endDate = new Date(work.end);

    toast.getElementsByClassName('work_start')[0].innerHTML = formatDateTime(startDate);
    toast.getElementsByClassName('work_end')[0].innerHTML = formatDateTime(endDate);

    toastBootstrap.show()
}


function formatDateTime(date) {
    const hours = ("0" + date.getHours()).slice(-2);      // Получаем часы с ведущим нулем
    const minutes = ("0" + date.getMinutes()).slice(-2);  // Получаем минуты с ведущим нулем
    const day = ("0" + date.getDate()).slice(-2);         // Получаем день месяца с ведущим нулем
    const month = ("0" + (date.getMonth() + 1)).slice(-2);// Получаем месяц с ведущим нулем (месяцы в JavaScript начинаются с 0)
    const year = date.getFullYear();                      // Получаем год

    return `${hours}:${minutes} ${day}-${month}-${year}`;
}

function toggle_loading(trigger_id, loading_node_id, time=20000) {
    start_loading(trigger_id, loading_node_id);
    delay(time).then(() => {
        end_loading(trigger_id, loading_node_id);
    });
}


function compose_article_item(base_node, data) {
    const wrapper = document.createElement('div');
    const title = document.createElement('div');
    const section = document.createElement('div');
    const keywords = document.createElement('div');
    const tags = document.createElement('div');
    const tag_rejected = document.createElement('div');
    const tag_winner = document.createElement('div');
    const tag_editor = document.createElement('div');
    const tag_reviewer = document.createElement('div');
    const tag_thesis_loaded = document.createElement('div');
    const tag_text_loaded = document.createElement('div');

    wrapper.classList.add('wrapper', 'article_wrapper');
    title.classList.add('article_title');
    section.classList.add('article_section');
    keywords.classList.add('article_keywords', 'mb-0');
    tags.classList.add('flex', 'flex-wrap');
    tag_rejected.classList.add('alert', 'alert-danger', 'd-inline-block', 'padding_light', 'small', 'mt-2', 'me-2', 'mb-0')
    tag_winner.classList.add('alert', 'alert-warning', 'd-inline-block', 'padding_light', 'small', 'mt-2', 'me-2', 'mb-0')
    tag_editor.classList.add('alert', 'alert-success', 'd-inline-block', 'padding_light', 'small', 'mt-2', 'me-2', 'mb-0')
    tag_reviewer.classList.add('alert', 'alert-success', 'd-inline-block', 'padding_light', 'small', 'mt-2', 'me-2', 'mb-0')
    tag_thesis_loaded.classList.add('alert', 'alert-primary', 'd-inline-block', 'padding_light', 'small', 'mt-2', 'me-2', 'mb-0')
    tag_text_loaded.classList.add('alert', 'alert-primary', 'd-inline-block', 'padding_light', 'small', 'mt-2', 'me-2', 'mb-0')

    tag_rejected.role="alert"
    tag_winner.role="alert"
    tag_editor.role="alert"
    tag_reviewer.role="alert"
    tag_thesis_loaded.role="alert"
    tag_text_loaded.role="alert"

    title.innerHTML = `Тема: <a href="${data.url}">${data.title}</a>`;
    section.innerHTML = `Секция: ${data.section}`;
    keywords.innerHTML = `Ключевые слова: ${data.keywords}`;
    tag_rejected.innerHTML = `Доклад отклонён`;
    tag_winner.innerHTML = `Победитель`;
    tag_editor.innerHTML = `Проверен редактором`;
    tag_reviewer.innerHTML = `Проверен рецензентом`;
    tag_thesis_loaded.innerHTML = `Тезисы загружены`;
    tag_text_loaded.innerHTML = `Статья загружена`;

    if (data.rejected !== null) tags.append(tag_rejected);
    if (data.is_winner === true) tags.append(tag_winner);
    if (data.editor_approved !== null) tags.append(tag_editor);
    if (data.reviewer_approved !== null) tags.append(tag_reviewer);
    if (data.thesis_loaded === true) tags.append(tag_thesis_loaded);
    if (data.text_loaded === true) tags.append(tag_text_loaded);

    wrapper.append(title, section, keywords);
    if (tags.hasChildNodes()) {
        wrapper.append(tags);
    }
    base_node.append(wrapper);
}


function compose_count_of_found(base_node, data) {
    const wrapper = document.createElement('div');
    const title = document.createElement('div');
    const hr = document.createElement('hr');

    title.classList.add('article_title');
    title.innerHTML = `Найдено докладов: ${data}`;

    wrapper.append(title, hr);
    base_node.append(wrapper);
}


function compose_filler(base_node, massage) {
    const msg = document.createElement('h5');
    msg.innerHTML = massage;
    base_node.append(msg);
}


function remove_node_by_id(node_id) {
    const node = document.getElementById(node_id);
    if (node !== undefined) {
        node.remove();
    }
}


function create_div_with_id(base_node, id) {
    const node = document.createElement('div');
    node.id = id;
    base_node.append(node);
    return node;
}


function compose_modal_errors(errors, errors_container_id, wrapper_id, color="inherit") {
    const base_node = document.getElementById(errors_container_id);
    const old = document.getElementById(wrapper_id);
    old.remove();

    const wrapper = document.createElement('ul');
    wrapper.classList.add('list-group', 'list-group-flush');
    wrapper.id = 'errors_wrapper';

    for (error of errors) {
        const li = document.createElement('li');
        li.classList.add('list-group-item');
        if (color !== "inherit") {
            li.style.color = color;
        }
        li.innerHTML = error;
        wrapper.append(li);
    }
    base_node.append(wrapper);
}
