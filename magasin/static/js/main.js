$(document).ready(function (){

    $('[data-toggle="tooltip"]').tooltip();            // i dont no what the problem is.

    // Bootstrap Modal
    // Bootstrap Modals: must be in base.html for the formURL.
    $(".bs-modal").each(function (){
        $(this).modalForm({ formURL: $(this).data('form-url'), });
    });

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
    // handle sortie form
    // FIXME
    //$('#sortie_form_modal').submit(function(event){
        //event.preventDefault();
        //$.ajax({
                //data: $(this).serialize(),
                //type: $(this).attr('method'),
                //url: $(this).attr('action'),
                //success: function(response){
                    //console.log(response);
                //},
                //error: function(request, status, error) {
                    //console.log(request.responseText);
                //}
        //});
    //});
})
