$(document).ready(function (){

    $('[data-toggle="tooltip"]').tooltip();            // i dont no what the problem is.

    // Bootstrap Modal
    // Bootstrap Modals: must be in base.html for the formURL.
    //$(".bs-modal").each(function (){
        //$(this).modalForm({ formURL: $(this).data('form-url'), });
    //});

    // Function to get the CSRF token from the cookie
    function getCSRFToken() {
        var name = 'csrftoken=';
        var value = document.cookie.split(';').find(row => row.trim().startsWith(name));
        return value ? value.split('=')[1] : null;
    }

    // toggle info dashboard
    $('.command_form_btn').click(function(){
        $($(this).data('form')).fadeToggle(1000);
        $(this).toggleClass('selected');

        if ( $(this).hasClass('selected') ) {
            $(this).html('Hide <i class="fa fa-chevron-up"></i>')
            $(this).after('<hr class="cmd_form_hr">');
        } else {
            $(this).html('N. Commande <i class="fa fa-chevron-down"></i>')
            $('.cmd_form_hr').remove();
        }
    });


    // Dashboard: toggle info div
    $('.toggle_info').click(function(){
        $(this).toggleClass('selected').parent().next('.card-body').slideToggle('slow');
        if ( $(this).hasClass('selected') ) {
            $(this).html('<i class="fa fa-caret-left fa-lg"></i>')
        } else {
            $(this).html('<i class="fa fa-caret-down fa-lg"></i>')
        }
    });

    // Enable tooltip
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // ---------------------------------------
    // Add Category Modal
    // ---------------------------------------

    // Open modal and load the form dynamically
    $('#addCategoryBtn').click(function () {
        $.get('/category/form/', function (data) {
            $('#modalContent').html(data);
            $('#mainModal').modal('show');
        });
    });

    $(document).on('submit', '#categoryForm', function (e) {
        e.preventDefault();
        $.ajax({
            url: "create-category/",  // Adjust the URL as needed
            type: 'POST',
            data: $(this).serialize(),
            headers: {'X-CSRFToken': getCSRFToken()},
            success: function(response) {
                if (response.success) {
                    $('#mainModal').modal('hide');
                    alert('Category added: ' + response.name);
                    $('#formErrors').html().hide();
                    // Optionally update the DOM with new category
                } else {
                    console.log(errorHtml)
                    let errorHtml = '';
                    for (let field in response.errors) {
                        errorHtml += field + ': ' + response.errors[field].join(', ') + '<br>';
                    }
                    $('#formErrors').html(errorHtml).show();
                }
            }
        });
    });

    // ---------------------------------------
    // Add Article
    // ---------------------------------------

    // Open modal and load the form dynamically
    $('#addArticleBtn').click(function () {
        $.get('/article/form/', function (data) {
            $('#modalContent').html(data);
            $('#mainModal').modal('show');
        });
    });

    $(document).on('submit', '#articleForm', function (e) {
        e.preventDefault();
        $.ajax({
            url: "create-article/",  // Adjust the URL as needed
            type: 'POST',
            data: $(this).serialize(),
            headers: {'X-CSRFToken': getCSRFToken()},
            success: function(response) {
                if (response.success) {
                    $('#mainModal').modal('hide');
                    alert('Article added: ' + response.code);
                    // Optionally update the DOM with new category
                } else {
                    let errorHtml = '';
                    for (let field in response.errors) {
                        errorHtml += field + ': ' + response.errors[field].join(', ') + '<br>';
                    }
                    $('#formErrors').html(errorHtml);
                }
            }
        });
    });

    // ---------------------------------------
    // Read Article
    // ---------------------------------------
    $('.readArticleBtn').click(function () {
        let slug = $(this).data('slug');
        let art_id = $(this).data('art-id');
        $.get(`/read-article/${art_id}/${slug}`, function (data) {
            $('#modalContent').html(data);
            $('#mainModal').modal('show');
        });
    });

    // ---------------------------------------
    // Update Article AJAX
    // ---------------------------------------
    $('.updateArticleBtn').click(function () {
        let slug = $(this).data('slug');
        let art_id = $(this).data('art-id');
        const url = $(this).data('url') + `/${art_id}/${slug}/`;
        $.get(`/edit-article/form/${art_id}/${slug}`, function (data) {
            $('#modalContent').html(data);
            $('#mainModal').modal('show');
        });
    });

    $(document).on('submit', '#articleEditForm', function (e) {
        e.preventDefault();
        const art_id = $(this).data('art-id');
        const slug = $(this).data('slug');
        $.ajax({
            type: 'POST',
            url: `/update-article/${art_id}/${slug}`,
            data: $(this).serialize(),
            headers: { 'X-CSRFToken': getCSRFToken() },
            success: function (res) {
                if (res.success) {
                    $('#mainModal').modal('hide');
                    alert('Updated: ' + res.designation);
                    $('#formErrors').html().hide();
                    // Optional: refresh the table or row
                } else {
                    let errorHtml = '';
                    for (let field in res.errors) {
                        errorHtml += `<strong>${field}:</strong> ${res.errors[field].join(', ')}<br>`;
                    }
                    $('#formErrors').html(errorHtml).show();
                }
            }
        });
    });
    // ---------------------------------------
    // Delete Article AJAX
    // --------------------------------------
    $('.deleteArticleBtn').click(function () {
        const art_id = $(this).data('art-id');
        const slug = $(this).data('slug');
        console.log('delete', art_id, slug);
        const html = `

            <div class="modal-header">
                <h3 class="modal-title">Suppression Article</h3>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close">
                </button>
            </div>

            <div class="modal-body">
                <p>Suppression aricle avec ID:<strong>${art_id}</strong>?</p>
            </div>

            <div class="modal-footer">
                <button type="button" class="btn btn-default" data-bs-dismiss="modal">Close</button>
                <button class="btn btn-danger confirm-delete-btn" data-art-id="${art_id}" data-slug="${slug}">
                    Confirm Delete it
                </button>
            </div>
            </div>`;
        $('#modalContent').html(html);
        $('#mainModal').modal('show');
    });

    $(document).on('click', '.confirm-delete-btn', function () {
        const art_id = $(this).data('art-id');
        const slug = $(this).data('slug');
        $.ajax({
            url: `/delete-article/${art_id}/${slug}`,
            type: 'POST',
            headers: { 'X-CSRFToken': getCSRFToken() },
            success: function (res) {
                if (res.success) {
                    $('#mainModal').modal('hide');
                    // Fade out the article row
                    $(`#article-row-${art_id}`).fadeOut(500, function () {
                        $(this).remove();
                    });

                    // Show success message
                    $('#successAlert')
                        .removeClass('d-none')
                        .text('Article deleted successfully.')
                        .fadeIn()
                        .delay(3000)
                        .fadeOut();

                } else {
                    $('#modalContent').html('<div class="alert alert-danger">Failed to delete article.</div>');
                }
            }
        });
    });
})
