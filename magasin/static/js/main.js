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
    function showMessages(msg, alert_type='alert-info', alertDiv='#successAlert') {
        const $alert = $(alertDiv);
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
    // --------------------------------------------------
    // ==> Load the html into the Modal
    // --------------------------------
    function openModalOnClick(buttonSelector) {
        $(document).on('click', buttonSelector, function (e) {
            e.preventDefault();
            const url = $(this).data('form-url');
            if (url) {
                $.get(url, function (data) {
                    $('#modalContent').html(data);
                    $('#mainModal').modal('show');
                });
            } else {
                console.warn('Missing data-form-url');
            }
        });
    };
    // ---------------------------------------------------
    // ==> Handle Ajax Form Submition
    // ------------------------------
    function handleAjaxFormSubmit(formSelector, alertDiv="#successAlert", swalMsgTitle='Success') {
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
                        Swal.fire({
                            icon: 'success',
                            title: swalMsgTitle,
                            text: response.message
                        });

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
    function generateDeleteDialog(item_title, item_id, btnClassName) {
        html = `
        <div class="modal-header">
                <h3 class="modal-title">🗑️ Suppression</h3>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close">
                </button>
            </div>

            <div class="modal-body">
                <div class="deleteErrors"></div>
                <p>
                    ⚠️  Êtes-vous sûr de vouloir supprimer ${item_title} avec ID:
                        <strong>« ${item_id} »</strong> ?<br>
                        &nbsp;&nbsp;&nbspCette action est irréversible.
                </p>
            </div>

            <div class="modal-footer">
                <button type="button" class="btn btn-default" data-bs-dismiss="modal">
                    <i class="bi bi-x-lg me-1"></i> Close
                </button>
                <button class="btn btn-danger ${btnClassName}" data-item-id="${item_id}">
                    <i class="bi bi-trash"></i> Confirm
                </button>
            </div>
            </div>
        `
        return html
    }
    /** ----------------------------------------------------------------
     * Opens a Bootstrap modal with a delete confirmation dialog.
     *
     * @param {string} buttonSelector - jQuery selector for the delete button (e.g., '.removeCategoryBtn').
     * @param {string} itemName - The name of the item to display in the confirmation message
                                  (e.g., 'catégorie').
     * @param {string} dialogBtnClass - The class name for the confirm delete button inside the modal
                                        (e.g., 'confirmDeleteCatBtn').
     *
     * Example:
     * openDeleteDialog('.removeCategoryBtn', 'catégorie', 'confirmDeleteCatBtn');
     */
    function openDeleteDialog(buttonSelector, itemName, dialogBtnClass) {
        $(document).on('click', buttonSelector, function (e) {
            e.preventDefault();
            const item_id = $(this).data('item-id');
            const html = generateDeleteDialog(itemName, item_id, dialogBtnClass);
            $('#modalContent').html(html);
            $('#mainModal').modal('show');
        });
    }

    /**
     * Handles the AJAX request for deleting an item after confirmation.
     *
     * @param {string} confirmBtnClass - Class of the confirm delete button (e.g., 'confirmDeleteCatBtn').
     * @param {string} deleteUrlBase - Base URL for the delete endpoint (e.g., '/magasin/delete-category/').
     * @param {string} messageContainer - Optional. The selector for where to show the success message
                                                    (default: '#articleAlert').
     * @param {string} rowPrefix - Optional. The prefix of the row ID to fade out (e.g., 'article-row-').
     *
     * Example:
     * handleDeleteConfirmClick('confirmDeleteCatBtn', '/magasin/delete-category/');
     */
    function handleDeleteConfirmClick(
        confirmBtnClass,
        deleteUrlBase,
        messageContainer='#articleAlert',
        rowPrefix=''
    ) {
        $(document).on('click', `.${confirmBtnClass}`, function () {
            const item_id = $(this).data('item-id');
            const url = `${deleteUrlBase}${item_id}`;
            $.ajax({
                type: 'POST',
                url: url,
                headers: { 'X-CSRFToken': getCSRFToken() },
                success: function (res) {
                    if (res.success) {
                        $('#mainModal').modal('hide');
                        // Remove the corresponding row from the table with fade out
                        if (rowPrefix) {
                            $(`#${rowPrefix}${item_id}`).fadeOut(500, function () {
                                $(this).remove();
                            });
                        }
                        Swal.fire({
                            icon: 'success',
                            title: 'Suppression réussie',
                            text: res.message
                        });
                        //showMessages(res.message, 'alert-success', messageContainer);
                    } else {
                        Swal.fire({
                            icon: 'error',
                            text: res.error,
                        });
                        $('#deleteErrors').text(res.error);
                    }
                }
            });
        });
    }
    // -------------------------------------------------------
    // ==> DASHBOARD Functions
    // -----------------------
    //
    // Total Modal
    openModalOnClick('#totalsModal');       // Open modal and load Statistics
    //
    // Dashboard: toggle info div
    $('.toggle-info').click(function(){
        $(this).toggleClass('selected').parent().next('.card-body').slideToggle('slow');
        if ( $(this).hasClass('selected') ) {
            $(this).html('<i class="bi bi-caret-up-fill"></i>')
        } else {
            $(this).html('<i class="bi bi-caret-down-fill"></i>')
        }
    });
    // ---------------------------------------------------
    // Articles Page
    // ----------------
    //
    // Create Category
    openModalOnClick('#addCategoryBtn')                         // load the form dynamically
    handleAjaxFormSubmit('#categoryForm', '#articleAlert', 'Création');     // Handle form submission
    //
    // Edit Category
    openModalOnClick('.updateCategoryBtn');                         // load the form dynamically
    handleAjaxFormSubmit('#categoryEditForm', '#articleAlert', 'Modification');     // Handle form submission
    // Remove Category
    openDeleteDialog('.removeCategoryBtn', 'catégorie', 'confirmDeleteCatBtn');
    handleDeleteConfirmClick('confirmDeleteCatBtn', '/magasin/delete-category/');
    //
    // Read Article
    openModalOnClick('.readArticleBtn');                        // load the template in modal.
    //
    // Create Article
    openModalOnClick('#addArticleBtn');                         // load the form dynamically
    handleAjaxFormSubmit('#articleForm', '#articleAlert', 'Création Article');      // Handle form submission
    //
    // Create Multiple Articles from Excel file
    openModalOnClick('#createMultipleArticles');    // load the form dynamically
    $(document).on('submit', '#uploadArticleForm', function (e) {
        // Submit Excel form with AJAX
        e.preventDefault();
        const form = this;
        const url = $(form).data('form-url');
        const formData = new FormData(form);

        $.ajax({
            url: url,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: { 'X-CSRFToken': getCSRFToken() },
            success: function (response) {
                if (response.success) {
                    $('#formErrors').addClass('d-none').html('');
                    $('#mainModal').modal('hide');
                    Swal.fire({
                        icon: 'success',
                        title: 'Creation articles réussie',
                        text: res.message
                    });
                } else {
                    if (response.errors && Array.isArray(response.errors)) {
                        // If there are multiple errors
                        errorHtml = `<p>${response.message}</p>`
                        errorHtml += '<ul>';
                        response.errors.forEach(function(err) {
                            errorHtml += `<li>${err}</li>`;
                        });
                        errorHtml += '</ul>';
                    } else if (response.message) {
                        // Only one error message
                        errorHtml = `<p>${response.message}</p>`;
                    }

                    Swal.fire({
                        icon: 'error',
                        title: 'Erreur!',
                        html: response.message,   // use `html` not `text` here to format nicely
                    });
                    $('#formErrors').removeClass('d-none').html(errorHtml || 'Erreur inconnue');
                }
            },
            error: function () {
                $('#formErrors').removeClass('d-none').html('❌ Une erreur s’est produite.');
            }
        });
    });
    //
    // Update Article
    openModalOnClick('.updateArticleBtn');                          // load the form dynamically
    handleAjaxFormSubmit('#articleEditForm', '#articleAlert', 'Modification Article');      // Handle form submission
    //
    // Delete Article
    openDeleteDialog('.deleteArticleBtn', "l'article", 'confirmDeleteArtBtn');    // open dialog
    // confirm delete ajax
    handleDeleteConfirmClick(
        confirmBtnClass='confirmDeleteArtBtn',
        deleteUrlBase='/magasin/delete-article/',
        messageContainer='#articleAlert',
        rowPrefix='article-row-'
    );
    //
    // Entree Article
    openModalOnClick('.newEntreeBtn');                              // load the form dynamically
    handleAjaxFormSubmit('#entreeArticleForm', '#articleAlert', 'Nouvel Entrée');    // Handle form submission
    //
    // Sortie Article
    openModalOnClick('.newSortieBtn');                              // load the form dynamically
    handleAjaxFormSubmit('#sortieArticleForm', '#articleAlert', 'Nouvel Sortie');    // Handle Sortie form submission
    //
    // Find Empty Code
    $(document).on('click', '.missingCodeBtn', function (e) {
        e.preventDefault();
        const cat_id = $(this).data('item-id');
        console.log('Get empty code for', cat_id);
        $.ajax({
            type: 'GET',
            url: '/magasin/missing-code-finder',  // Adjust the URL if needed
            data: { cat_id: cat_id },
            success: function (res) {
                if (res.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Code disponible',
                        text: res.message,
                    });
                    // You can also insert the code somewhere:
                    // $('#codeInput').val(res.empty_code);
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Erreur',
                        text: res.message,
                    });
                }
            },
            error: function () {
                Swal.fire({
                    icon: 'error',
                    title: 'Erreur',
                    text: 'Une erreur est survenue lors de la récupération du code.',
                });
            }
        });
    });

    //
    // ---------------------------------------------------------------
    // ===> USERS PAGE
    // ----------------
    //
    $('#searchUsersWord').on('keyup', function() {
        const searchWord = $(this).val();
        $.ajax({
            url: "/accounts/search-users/",
            data: { search_word: searchWord },
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    $('#userTableBody').html(response.html);
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Groupe non modifié',
                        text: response.message
                    });
                }
            },
            error: function() {
                Swal.fire({
                    icon: 'error',
                    title: 'Groupe non modifié',
                    text: "Une erreur s'est produite lors de la recherche."
                });
            }
        });
    });
    //
    // Read User
    openModalOnClick('.readUserBtn');                           // load the form dynamically
    //
    // Create user
    openModalOnClick('#createUserBtn');                         // load the form dynamically
    handleAjaxFormSubmit('#addUserForm', '#usersAlert', 'Création Utilisateur');        // Handle CreateUser form submission
    //
    // Edit user
    openModalOnClick('.editUserBtn');                           // load the form dynamically
    handleAjaxFormSubmit('#userEditForm', '#usersAlert', 'Modification Utilisateur');       // Handle UpdateUser form submission
    //
    // Change user Groupe
    $(document).on('click', '.changeUserGroupBtn', function (e) {
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
                    //showMessages(response.message, 'alert-success', alertDiv='#usersAlert');
                    Swal.fire({
                        icon: 'success',
                        title: 'Groupe modifié',
                        text: res.message
                    });
                    $(this).remove();
                    // location.reload();
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Groupe non modifié',
                        text: response.message
                    });
                }
            },
            error: function(xhr, status, error) {
                // Handle AJAX error
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'An error occurred while processing your request.'
                });
            }
        });
    });
    //
    // Delete User AJAX
    openDeleteDialog('.deleteUserBtn', "l'utilisateur", 'confirmDeleteUserBtn');    // open dialog
    handleDeleteConfirmClick(                                                       // confirm delete ajax
        confirmBtnClass='confirmDeleteUserBtn',
        deleteUrlBase='/accounts/delete-user/',
        messageContainer='#usersAlert',
        rowPrefix='user-row-'
    );
    //
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
                    //showMessages(response.message, 'alert-success', '#commandeAlert');
                    Swal.fire({
                        icon: 'success',
                        title: 'Commande activée',
                        text: res.message
                    });
                    $(this).fadeOut(500);
                    // location.reload();
                }
            },
            error: function(xhr, status, error) {
                // Handle AJAX error
                //showMessages('An error occurred while processing your request.', 'alert-danger');
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'une erreur est survenue lors de l\'activation de la commande.'
                });
            }
        });
    });
    //
    // Read Commande
    openModalOnClick('.readCommandBtn');                            // load the form dynamically
    //
    // Create Commande
    openModalOnClick('.newCommandeBtn');                            // load the form dynamically
    handleAjaxFormSubmit('#createCommandeForm', '#articleAlert', 'Création commande');   // Handle EditCommande form submission

    // Edit Commande
    openModalOnClick('.editCommandeBtn');                           // load the form dynamically
    handleAjaxFormSubmit('#commandeEditForm', '#commandeAlert', 'Modification commande');  // Handle EditCommande form submission
    //
    // Delete Commande AJAX
    openDeleteDialog('.deleteCommandeBtn', "la commande ", 'confirmDeleteCmdBtn');    // open dialog
    handleDeleteConfirmClick(           // confirm delete ajax
        confirmBtnClass='confirmDeleteCmdBtn',
        deleteUrlBase='/magasin/delete-commande/',
        messageContainer='#commandeAlert',
        rowPrefix='commande-row-'
    );
    //
    // ---------------------------------------------------------------
    // ===> Movement PAGE
    // --------------------
    //
    // Delete Movement AJAX
    openDeleteDialog('.deleteMovementBtn', "le movement ", 'confirmDeleteMovBtn');  // open dialog
    handleDeleteConfirmClick(                                                       // confirm delete ajax
        confirmBtnClass='confirmDeleteMovBtn',
        deleteUrlBase='/magasin/delete-movement/',
        messageContainer='#movementAlert',
        rowPrefix='movement-row-'
    );
    //
    //------------------------------------------
    // ==> Fournisseur Page
    //----------------------
    openModalOnClick('.readFournisBtn');
    //
    // Create Fournisseur
    openModalOnClick('#createFournissBtn');                         // load the form dynamically
    handleAjaxFormSubmit('#createFournissForm', '#fournisAlert', 'Création Fournisseur');   // Handle create form submission
    //
    // Edit Fournisseur
    openModalOnClick('.editFournissBtn');                           // load the form dynamically
    handleAjaxFormSubmit('#fournissEditForm', '#fournisAlert');     // Handle update form submission
    //
    // Delete Commande AJAX
    openDeleteDialog('.deleteFournissBtn', "Fournisseur ", 'confirmDeleteFournissBtn'); // open dialog
    handleDeleteConfirmClick(
        // confirm delete ajax
        confirmBtnClass='confirmDeleteFournissBtn',
        deleteUrlBase='fournisseur/delete-fourniss/',
        messageContainer='#fournisAlert',
        rowPrefix='fourniss-row-'
    );

    // Group Chart
    //
    const groupData = JSON.parse(document.getElementById('group-data').textContent);
    const jobTitleData = JSON.parse(document.getElementById('job-title-data').textContent);

    // Process for Chart.js
    const groupLabels = groupData.map(obj => obj.groupe);
    const groupCounts = groupData.map(obj => obj.count);

    const jobTitleLabels = jobTitleData.map(obj => obj.poste_travaille);
    const jobTitleCounts = jobTitleData.map(obj => obj.count);

    const groupCtx = document.getElementById('groupChart').getContext('2d');
    const groupChart = new Chart(groupCtx, {
        type: 'pie',
        data: {
            labels: groupLabels,
            datasets: [{
                label: 'User Groups',
                data: groupCounts,
                backgroundColor: ['#36A2EB', '#FF6384'],
            }],
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Users by Group'
                }
            }
        }
    });

    // Job Title Chart
    const jobTitleCtx = document.getElementById('jobTitleChart').getContext('2d');
    const jobTitleChart = new Chart(jobTitleCtx, {
        type: 'bar',
        data: {
            labels: jobTitleLabels,
            datasets: [{
                label: 'Job Titles',
                data: jobTitleCounts,
                backgroundColor: '#4BC0C0',
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Users by Job Title'
                }
            }
        }
    });
})
