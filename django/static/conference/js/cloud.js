document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('thesis_document_download').addEventListener('click', () => {
        toggle_loading("thesis_document_download", "download_thesis_wrapper", 15000);
    });
    document.getElementById('thesis_document_download').addEventListener('click', () => {
        download_document("thesis_document_download");
    });

    document.getElementById('article_document_download').addEventListener('click', () => {
        toggle_loading("article_document_download", "download_article_wrapper", 15000);
    });
    document.getElementById('article_document_download').addEventListener('click', () => {
        download_document("article_document_download");
    });
});


function download_document(node_id, need_check=false) {
    const node = document.getElementById(node_id);
    const filename = `${node.dataset.filename}.docx`;
    let url = node.dataset.href;
    if (need_check) url = url + '/1'

    fetch(url, {
        method: 'GET',
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    console.log(data.errors);
                    compose_modal_errors(data.errors, "errors_container", "errors_wrapper");
                    document.getElementById("modal_errors_toggle").click();
                });
            }
            if (response.status === 202) return;

            const a = document.createElement('a');
            a.download = filename;
            a.hidden = true;
            a.id = 'generated_file_name';
            document.body.appendChild(a);

            return response.blob();
        })
        .then(blob => {
            if (!(blob instanceof Blob)) {
                return;
            }
            const url = URL.createObjectURL(blob);
            const a = document.getElementById('generated_file_name');
            a.href = url;
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
        })
        .catch(error => {
            console.error('Ошибка:', error);
        });
}


function getFilenameFromResponse(response) {
    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = null;
    if (contentDisposition) {
        const matches = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (matches && matches[1]) {
            filename = matches[1].replace(/['"]/g, '');
            filename = decodeURIComponent(filename);

            const charsetIndex = filename.indexOf("utf-8");
            if (charsetIndex !== -1) {
                filename = filename.substring(charsetIndex + 5); // Длина "utf-8"
            }
        }
    }

    return filename || 'Документ';
}


