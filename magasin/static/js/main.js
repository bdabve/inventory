$(document).ready(function (){

    $('[data-toggle="tooltip"]').tooltip();            // i dont no what the problem is.

    // Enable tooltip
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    // -------------------------------------------------------
    // Toggle Theme
    // Check if dark mode is already enabled in localStorage
    if (localStorage.getItem("theme") === "dark") {
        $("html").attr("data-bs-theme", "dark");
        $("#toggle-theme").html("<i class='bi bi-sun'></i> Light");
    }
    // Toggle theme
    $('#toggle-theme').click(function() {
        let currentTheme = $("html").attr("data-bs-theme");
        if ( currentTheme === "light" ) {
            $("html").attr("data-bs-theme", "dark");
            localStorage.setItem("theme", "dark");
            $("#toggle-theme").html("<i class='bi bi-sun-fill'></i>&nbsp; Light");
        } else {
            $("html").attr("data-bs-theme", "light");
            localStorage.setItem("theme", "light");
            $("#toggle-theme").html("<i class='bi bi-moon-stars'></i>&nbsp; Dark");
        }
    });
    // -------------------------------------------------------
    // ==> DASHBOARD Functions
    // -----------------------
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
    // ---------------------------------------
    // Total Modal
    // ---------------------------------------
    //
    // Open modal and load the form dynamically
    $('#totalsModal').click(function () {
        const url = $(this).data('form-url');
        $.get(url, function (data) {
            $('#modalContent').html(data);
            $('#mainModal').modal('show');
        });
    });
    // ---------------------------------------
    // Global Functions
    // ------------------
    // Function to get the CSRF token from the cookie
    function getCSRFToken() {
        var name = 'csrftoken=';
        var value = document.cookie.split(';').find(row => row.trim().startsWith(name));
        return value ? value.split('=')[1] : null;
    }
    // -------------------------------------
    // ==> Formating Errors for Users Page
    // This work with users page because of user_form.errors and profile_form.errors
    // ------------------------------------------------------------------------------
    function formatUsersErrors(errors) {
        let errorHtml = '';
        for (let formName in errors) {
            const formErrors = errors[formName];
            for (let field in formErrors) {
                const fieldErrors = formErrors[field];
                if (Array.isArray(fieldErrors)) {
                    const messages = fieldErrors.map(err => err.message).join('<br>');
                    errorHtml += `<strong>${field}:</strong> ${messages}<br>`;
                }
            }
        }
        return errorHtml;
    }
    // ---------------------------------------------------
    // ==> Formating Errors for Articles Page
    // --------------------------------------
    function formatArticleErrors(errors) {
        let errorHtml = '';
        for (let field in errors) {
            errorHtml += field + ': ' + errors[field].join(', ') + '<br>';
        }
        return errorHtml;
    }
    // ---------------------------------------------------
    // display Messages
    // -----------------
    function showMessages(msg, alert_type='alert-info') {
        const $alert = $('#successAlert');
        $alert
            .stop(true, true)
            .hide()
            .removeClass('d-none alert-info alert-success alert-danger alert-warning show')
            .addClass(`show ${alert_type}`)
            .html(`
                <span>${msg}</span>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `)
            .fadeIn(300)
            .delay(4000)
            .fadeOut(300);
    }
    // ---------------------------------------------------
    // ==> Handle Ajax Form Submition
    // ------------------------------
    function handleAjaxFormSubmit(formSelector) {
        $(document).on('submit', formSelector, function (e) {
            e.preventDefault();
            const $form = $(this);
            const url = $form.data('form-url');

            $.ajax({
                type: 'POST',
                url: url,
                data: $form.serialize(),
                headers: { 'X-CSRFToken': getCSRFToken() },
                success: function (response) {
                    if (response.success) {
                        $('#formErrors').html('').hide();
                        $('#mainModal').modal('hide');
                        showMessages(response.message, 'alert-info');
                    } else {
                        if (formSelector == '#userEditForm' || formSelector == '#addUserForm') {
                            errorHtml = formatUsersErrors(response.errors);
                        } else {
                            errorHtml = formatArticleErrors(response.errors);
                        }
                        $('#formErrors').html(errorHtml).show();
                    }
                }
            });
        });
    }
    // ---------------------------------------------------
    // ==> Generate Delete Dialog HTML
    // -------------------------------
    function generateDeleteDialog(item_title, slug, btnClassName, art_id=null) {
        const artIdAttribute = art_id ? `data-art-id="${art_id}"` : '';
        html = `
        <div class="modal-header">
                <h3 class="modal-title">🗑️ Suppression</h3>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close">
                </button>
            </div>

            <div class="modal-body">
                <div class="deleteErrors"></div>
                <p>
                    ⚠️  Êtes-vous sûr de vouloir supprimer ${item_title} <strong>« ${slug} »</strong> ?<br>
                       &nbsp;&nbsp;&nbspCette action est irréversible.
                </p>
            </div>

            <div class="modal-footer">
                <button type="button" class="btn btn-default" data-bs-dismiss="modal">Close</button>
                <button class="btn btn-danger ${btnClassName}"
                        data-slug="${slug}" ${artIdAttribute}">
                    <i class="bi bi-trash"></i> Confirm
                </button>
            </div>
            </div>
        `
        return html
    }

    // ---------------------------------------------------
    // Add Category
    // -------------
    // Open modal and load the form dynamically
    $('#addCategoryBtn').click(function () {
        const url = $(this).data('form-url');
        $.get(url, function (data) {
            $('#modalContent').html(data);
            $('#mainModal').modal('show');
        });
    });
    // Handle category form submission
    handleAjaxFormSubmit('#categoryForm');
    // ---------------------------------------------------
    // Remove Category
    // -----------------
    $('.removeCategoryBtn').click(function (e) {
        e.preventDefault();
        const slug = $(this).data('slug');
        const html = generateDeleteDialog('catégorie', slug, 'confirmDeleteCatBtn');
        $('#modalContent').html(html);
        $('#mainModal').modal('show');
    });
    //
    // Handle delete form submission
    $(document).on('click', '.confirmDeleteCatBtn', function () {
        const slug = $(this).data('slug');
        const url = `/magasin/delete-category/${slug}`;
        $.ajax({
            type: 'POST',
            url: url,
            headers: { 'X-CSRFToken': getCSRFToken() },
            success: function (res) {
                if (res.success) {
                    $('#mainModal').modal('hide');
                    // Show success message
                    showMessages(res.message, 'alert-success');
                } else {
                    $('#deleteErrors').text(res.error);
                }
            }
        });
    });
    // ---------------------------------------------------
    // Add Article
    // ------------
    $('#addArticleBtn').click(function () {
        const url = $(this).data('form-url');
        $.get(url, function (data) {
            $('#modalContent').html(data);
            $('#mainModal').modal('show');
        });
    });
    // Handle New Article form submission
    handleAjaxFormSubmit('#articleForm');

    // ---------------------------------------------------
    // Read Article
    // --------------
    $('.readArticleBtn').click(function () {
        const url = $(this).data('form-url');
        $.get(url, function (data) {
            $('#modalContent').html(data);
            $('#mainModal').modal('show');
        });
    });

    // ---------------------------------------------------
    // Update Article
    // ----------------
    $('.updateArticleBtn').click(function () {
        const url = $(this).data("form-url");
        $.get(url, function (data) {
            $('#modalContent').html(data);
            $('#mainModal').modal('show');
        });
    });
    // Handle update article form submission
    handleAjaxFormSubmit('#articleEditForm');

    // ---------------------------------------------------
    // Delete Article
    // ---------------
    $('.deleteArticleBtn').click(function () {
        const art_id = $(this).data('art-id');
        const slug = $(this).data('slug');
        const html = generateDeleteDialog("l'article ", slug, 'confirmDeleteArtBtn', art_id);
        $('#modalContent').html(html);
        $('#mainModal').modal('show');
    });
    //
    // Handle Delete Article form submission
    $(document).on('click', '.confirmDeleteArtBtn', function () {
        const art_id = $(this).data('art-id');
        const slug = $(this).data('slug');
        const url = `/magasin/delete-article/${art_id}/${slug}`;
        $.ajax({
            type: 'POST',
            url: url,
            headers: { 'X-CSRFToken': getCSRFToken() },
            success: function (res) {
                if (res.success) {
                    $('#mainModal').modal('hide');
                    // Fade out the article row
                    $(`#article-row-${art_id}`).fadeOut(500, function () {
                        $(this).remove();
                    });
                    // Show success message
                    showMessages(res.message, 'alert-info');
                } else {
                    $('#deleteErrors').text(res.error);
                }
            }
        });
    });
    // ---------------------------------------------------
    // Entree Article
    // ---------------
    $('.newEntreeBtn').click(function () {
        const url = $(this).data("form-url");
        $.get(url, function (data) {
            $('#modalContent').html(data);
            $('#mainModal').modal('show');
        });
    });
    // Handle Entree form submission
    handleAjaxFormSubmit('#entreeArticleForm');

    // ---------------------------------------------------
    // Sortie Article
    // ---------------
    $('.newSortieBtn').click(function () {
        const url = $(this).data("form-url");
        $.get(url, function (data) {
            $('#modalContent').html(data);
            $('#mainModal').modal('show');
        });
    });
    // Handle Sortie form submission
    handleAjaxFormSubmit('#sortieArticleForm');

    // ---------------------------------------------------------------
    // ===> USERS PAGE
    // ----------------
    // Read User
    $('.readUserBtn').click(function () {
        const url = $(this).data('form-url');
        $.get(url, function (data) {
            $('#modalContent').html(data);
            $('#mainModal').modal('show');
        });
    });
    // --------------------------------------------------------
    // Create user
    // ------------
    $('#createUserBtn').click(function () {
        const url = $(this).data('form-url');
        $.get(url, function (data) {
            $('#modalContent').html(data);
            $('#mainModal').modal('show');
        });
    });
    // Handle CreateUser form submission
    handleAjaxFormSubmit('#addUserForm');

    // ------------------------------------------------------------
    // Edit user
    // ----------
    $('.editUserBtn').click(function () {
        const url = $(this).data('form-url');
        $.get(url, function (data) {
            $('#modalContent').html(data);
            $('#mainModal').modal('show');
        });
    });
    // Handle UpdateUser form submission
    handleAjaxFormSubmit('#userEditForm');

    // ---------------------------------------
    // Delete User AJAX
    // -----------------
    $('.deleteUserBtn').click(function () {
        const user_id = $(this).data('userid');
        const username = $(this).data('username');
        const html = generateDeleteDialog("l'utilisateur ", username, 'confirmDeleteUserBtn', user_id);
        $('#modalContent').html(html);
        $('#mainModal').modal('show');
    });
    //
    // Handle form submission
    $(document).on('click', '.confirmDeleteUserBtn', function () {
        const user_id = $(this).data('art-id');
        const url = `/accounts/delete-user/${user_id}`;
        $.ajax({
            type: 'POST',
            url: url,
            headers: { 'X-CSRFToken': getCSRFToken() },
            success: function (res) {
                if (res.success) {
                    $('#mainModal').modal('hide');
                    // Fade out the article row
                    $(`#user-row-${user_id}`).fadeOut(500, function () {
                        $(this).remove();
                    });
                    // Show success message
                    showMessages(res.message, 'alert-info');
                } else {
                    $('#deleteErrors').text(res.error);
                }
            }
        });
    });
    // ---------------------------------------------------------------
    // ===> Commandes PAGE
    // --------------------
    // Activate Commande
    $(document).on('click', '.activateCommandeBtn', function (e) {
        e.preventDefault();  // Prevent default action
        const url = $(this).data('form-url');  
        $.ajax({
            url: url,  
            type: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()  // Include CSRF token for security
            },
            success: function(response) {
                if (response.success) {
                    // Display a success message
                    showMessages(response.message, 'alert-success');
                    // Optionally, you can reload the page or update the UI
                    location.reload();  // Uncomment to reload the page after success
                }
            },
            error: function(xhr, status, error) {
                // Handle AJAX error
                showMessages('An error occurred while processing your request.', 'alert-danger');
            }
            });
    });

    // ------------------------------------------------------------
    // Edit Commande
    // --------------
    $('.editCommandeBtn').click(function () {
        const url = $(this).data('form-url');
        $.get(url, function (data) {
            $('#modalContent').html(data);
            $('#mainModal').modal('show');
        });
    });
    // Handle EditCommande form submission
    handleAjaxFormSubmit('#commandeEditForm');
    // ------------------------------------------------------------
    // Read Commande
    $('.readCommandBtn').click(function () {
        const url = $(this).data('form-url');
        $.get(url, function (data) {
            $('#modalContent').html(data);
            $('#mainModal').modal('show');
        });
    });    
    // ---------------------------------------
    // Delete Commande AJAX
    // ----------------------
    $('.deleteCommandeBtn').click(function () {
        const commande_id = $(this).data('commande-id');
        const html = generateDeleteDialog("la commande ", commande_id, 'confirmDeleteCmdBtn');
        $('#modalContent').html(html);
        $('#mainModal').modal('show');
    });
    //
    // Handle form submission
    $(document).on('click', '.confirmDeleteCmdBtn', function () {
        const commande_id = $(this).data('slug');
        const url = `/magasin/delete-commande/${commande_id}`;
        $.ajax({
            type: 'POST',
            url: url,
            headers: { 'X-CSRFToken': getCSRFToken() },
            success: function (res) {
                if (res.success) {
                    $('#mainModal').modal('hide');
                    // Fade out the article row
                    $(`#commande-row-${commande_id}`).fadeOut(500, function () {
                        $(this).remove();
                    });
                    // Show success message
                    showMessages(res.message, 'alert-info');
                } else {
                    $('#deleteErrors').text(res.error);
                }
            }
        });
    });
    // ---------------------------------------
    // Delete Movement AJAX
    // ----------------------
    $('.deleteMovementBtn').click(function () {
        const movement_id = $(this).data('movement-id');
        const html = generateDeleteDialog("le movement ", movement_id, 'confirmDeleteMovBtn');
        $('#modalContent').html(html);
        $('#mainModal').modal('show');
    });
    //
    // Handle form submission
    $(document).on('click', '.confirmDeleteMovBtn', function () {
        const movement_id = $(this).data('slug');
        const url = `/magasin/delete-movement/${movement_id}`;
        $.ajax({
            type: 'POST',
            url: url,
            headers: { 'X-CSRFToken': getCSRFToken() },
            success: function (res) {
                if (res.success) {
                    $('#mainModal').modal('hide');
                    // Fade out the article row
                    $(`#commande-row-${movement_id}`).fadeOut(500, function () {
                        $(this).remove();
                    });
                    // Show success message
                    showMessages(res.message, 'alert-info');
                } else {
                    showMessages(res.error, 'alert-danger');
                }
            }
        });
    });
})
