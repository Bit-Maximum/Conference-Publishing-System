document.addEventListener('DOMContentLoaded', function() {
    const sections = document.getElementById("sections_form_wrapper");

    const element = document.createElement('select');
    element.classList.add('form-control', 'form-select', 'form-select-lg', 'mb-3', 'required');
    /*element.multiple = true;*/
    element.id = "sections"
    element.name = "sections"
    const default_option = document.createElement('option');
    default_option.selected = true;
    default_option.disabled = true;
    default_option.innerHTML = 'Выберите секцию, за которую вы отвечаете'
    element.append(default_option);

    fetch(`/sections`)
        .then(response => response.json())
        .then(data => {
            let sections = data.sections;

            sections.forEach((data) => {
                const option = document.createElement('option');
                option.value = data.id;
                option.innerHTML = data.content;
                element.append(option);
                });
            });
    sections.append(element);
});
