$('#InwardCheckAll').on('click',function(){
    switch ($(this).prop('checked')) {
        case true:
            $(this).prop('checked',true)
            $.each($('input[id="InwardCheck"]'),function(){
            $(this).attr('checked',true);
            });
            break;
        default:
            $.each($('input[id="InwardCheck"]'),function(){
            $(this).attr('checked',false);
            });
            break;
    }
});  
$('#InwardSubmit').on('click',function(){
    var inwardSelected = [];
    $.each($('input[id="InwardCheck"]'),function(){
        if($(this).prop('checked')){
        inwardSelected.push($(this).val());
        }
    });
    if(inwardSelected.length === 0){
        toastr.error('Please Select from the below Table.', 'Failed');
    }else{
        $('#preloader').fadeIn();
        $('body').css('overflow', 'hidden');
        $.ajax({
        url: '/QR/Cylinder-Stocking-In',
        type: 'POST',
        // processData: false,
        // contentType: false,
        // mimeType: 'multipart/form-data',
        headers: {
            'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val(),
        },
        data: {'selectedinward' :inwardSelected },
        success: function(response) {
            $('#preloader').fadeOut();
            $('body').removeAttr('style');
            toastr.success('Inward Successfull', 'Success');
            $.each($('input[id="InwardCheck"]'),function(){
            if($.inArray($(this).val(), inwardSelected) !== -1){
                $(this).parent().parent().remove();
            }
            });
            setTimeout(() => {
            window.location.reload();
            }, 2500);
        },
        error: function(xhr, status, error) {
            // Handle any errors
            $('#preloader').fadeOut();
            $('body').removeAttr('style');
            console.error(status, error, 'Failed');
            toastr.error('Inward Action Cannot be Completed', 'Failed');
        }
        });
    }
});