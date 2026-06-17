$(document).ready(function() {
    var storedFormData = null;
    if (window.location.href != localStorage.getItem('formDataURL')){
        localStorage.removeItem('formData');
        localStorage.removeItem('formDataURL');
        localStorage.setItem('formDataURL',window.location.href);
    }else{
        storedFormData = localStorage.getItem('formData');
    }
    if (storedFormData) {
        storedFormData = JSON.parse(storedFormData);
        $.each(storedFormData, function(index, element) {
            $('[name="' + element.name + '"]').val(element.value);
        });
    }
    $('form').on('input', function() {
        var formData = $(this).serializeArray();
        localStorage.setItem('formData', JSON.stringify(formData));
    });
});