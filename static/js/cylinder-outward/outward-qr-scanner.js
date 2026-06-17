$('.clear-cam-default').hide();
$('#flash-on').on('click',function(){
  turnOffFlashligh();
  $(this).hide();
  $('#flash-off').show();
});
$('#flash-off').on('click',function(){
  turnOnFlashlight();
  $(this).hide();
  $('#flash-on').show();
});
$('.sub-btn').hide();
$('.qr-found-details').hide();
$('#qr-alert').hide();
// $("select").select2();
// $("select").on('click',function(){
//     $('.select2-container').css('z-index','9999999 !important');
// });
// $('.qr-manual').on('click',function(){
//     setTimeout(() => {
//         $("select").select2();
//     }, 200);
// });
const turnOnFlashlight = async() => {
    if (navigator.getBattery && navigator.getBattery().then) {
        navigator.getBattery().then(function(battery) {
            if (battery.level > 0.2) {
                navigator.vibrate(200); // Vibrate the device (optional)
                navigator.vibrate(0); // Stop vibration (optional)
                battery.vibrate = true;
            }
        });
    }
}

// Function to turn off the flashlight
const turnOffFlashligh = async () => {
    if (navigator.getBattery && navigator.getBattery().then) {
        navigator.getBattery().then(function(battery) {
            battery.vibrate = false;
        });
    }
}
const checkCamDefaults = async (currDeviceID) => {
  try {
    if(localStorage.getItem('currDeviceID')){
      $('.clear-cam-default').fadeIn();
    }
    return 'Success';
  } catch (error) {
    console.error('Error accessing camera devices:', error);
    return [];
  }
};
const hideCamDefault = async (currDeviceID) => {
  try {
    if(localStorage.getItem('currDeviceID')){
      $('.clear-cam-default').fadeOut();
    }
    return 'Success';
  } catch (error) {
    console.error('Error accessing camera devices:', error);
    return [];
  }
};
$('.clear-cam-default').on('click',function(){
  localStorage.removeItem('currDeviceID');
  $('.cam-switch').slideDown();
  $(this).fadeOut();
});

var currDeviceID = localStorage.getItem('currDeviceID') || null ;
// var currDeviceID = null ;
const getCameraDevices = async () => {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    const videoDevices = devices.filter(device => device.kind === 'videoinput');
    return videoDevices;
  } catch (error) {
    console.error('Error accessing camera devices:', error);
    return [];
  }
};

const switchCamera = async (deviceId) => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: { deviceId: { exact: deviceId } } });
    const video = document.getElementById('qr-video');
    video.srcObject = null;
    video.srcObject = stream;
    video.play();
    $('.stop-scan').on('click', function () {
      $('.sub-btn').hide();
      $('.qr-found-details').hide();
      $('#qr-alert').hide();
      stream.getTracks().forEach(track => track.stop());
      video.srcObject = null;
      formReset();
      $('.stop-scan').off('click');
      $('.re-scan').off('click');
    });
    $('.re-scan').on('click', function () {
        $('.sub-btn').hide();
        $('.qr-found-details').hide();
        $('#qr-alert').hide();
        stream.getTracks().forEach(track => track.stop());
        video.srcObject = null;
        formReset();
        $('.stop-scan').off('click');
        $('.re-scan').off('click');
    });
  } catch (error) {
    console.error('Error switching camera:', error);
    // window.alert('Error switching camera:', error);
  }
};

const endCameraStream = (stream) => {
  stream.getTracks().forEach(track => track.stop());
};

const displayCameraOptions = async () => {
  const cameraDevices = await getCameraDevices();
  const cameraOptions = cameraDevices.map(device => ({
    label: device.label || `Camera ${device.deviceId}`,
    value: device.deviceId
  }));

  const selectDropdown = document.getElementById('camera-list');
  selectDropdown.innerHTML = '';
  cameraOptions.forEach(option => {
    const optionElement = document.createElement('option');
    optionElement.value = option.value;
    optionElement.textContent = option.label;
    selectDropdown.appendChild(optionElement);
  });

  selectDropdown.addEventListener('change', (event) => {
    const selectedDeviceId = event.target.value;
    const video = document.getElementById('qr-video');
    const currentStream = video.srcObject;
    currDeviceID = selectedDeviceId
    if (currentStream) {
      endCameraStream(currentStream);
    }
    switchCamera(selectedDeviceId);
  });
};

const formReset = () => {
  $('#qr-video').parent().parent().find('p').remove();
  $('#qr-video').fadeIn();
  $('.qr_sl_number').val('');
  $('#qr_sl_number').val('');
};

const scanQRCode = async () => {
  try {
    $('.re-scan').hide();
    formReset();
    checkCamDefaults();
    var newstream;
    if (currDeviceID){
      $('.cam-switch').hide();
      newstream = await navigator.mediaDevices.getUserMedia({ video: { deviceId: { exact: currDeviceID } } });
    }else{
      newstream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
    }
    const stream = newstream;
    const videoTracks = stream.getVideoTracks();
    if (videoTracks.length > 0) {
      $('#camera-list option').each(function () {
        if ($(this).val() == videoTracks[0].getSettings().deviceId) {
          currDeviceID = videoTracks[0].getSettings().deviceId;
          $(this).prop('selected', true);
        }
      });
    }
    const video = document.getElementById('qr-video');
    video.srcObject = stream;
    video.setAttribute('playsinline', true);
    video.play();
    $('.stop-scan').on('click', function () {
      $('.sub-btn').hide();
      $('.qr-found-details').hide();
      $('#qr-alert').hide();
      stream.getTracks().forEach(track => track.stop());
      clearInterval(scanInterval);
      video.srcObject = null;
      formReset();
      $('.stop-scan').off('click');
      $('.re-scan').off('click');
    });
    $('.re-scan').on('click', function () {
        $('.sub-btn').hide();
        $('.qr-found-details').hide();
        $('#qr-alert').hide();
        stream.getTracks().forEach(track => track.stop());
        clearInterval(scanInterval);
        video.srcObject = null;
        formReset();
        scanQRCode();
        $('.stop-scan').off('click');
        $('.re-scan').off('click');
    });
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');

    const scanInterval = setInterval(() => {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
      const code = jsQR(imageData.data, imageData.width, imageData.height);

      if (code && code.data) {
        if (!(localStorage.getItem('currDeviceID'))){
          localStorage.setItem('currDeviceID', currDeviceID);
        }
        hideCamDefault();
        stream.getTracks().forEach(track => track.stop());
        clearInterval(scanInterval);
        $('#preloader').fadeIn();
        $('body').css('overflow', 'hidden');
        setTimeout(() => {
          const scannedData = (code.data).toUpperCase();
          $('.qr_sl_number').val(scannedData);
          $('#qr_sl_number').val(scannedData);
          CylinderQRMatch(scannedData);
          const successText = $('<p>').addClass('alert alert-success text-center').text('Scan Successful.');
          $('#qr-video').fadeOut();
          $('#qr-video').parent().parent().append(successText);
          $('#preloader').fadeOut();
          $('body').removeAttr('style');
          video.srcObject = null;
          $('.re-scan').show();
          $('.cam-switch').slideUp();
        }, 700);
      }
    }, 300);
  } catch (error) {
    console.error('Error accessing camera:', error);
    // window.alert('Error accessing camera:', error);
    const errorText = $('<p>').addClass('alert alert-danger text-center').text('Allow camera permissions in your browser settings.');
    $('#qr-video').fadeOut();
    $('#qr-video').parent().parent().find('p').remove();
    $('#qr-video').parent().parent().append(errorText);
  }
};

$('.qr-btn').on('click', function () {
  scanQRCode();
});

displayCameraOptions();
checkCamDefaults();

$('#outward-dc-form').on('submit',function(e){
  e.preventDefault();
});

$('#OutwardCheckAll').on('click',function(){
  switch ($(this).prop('checked')) {
    case true:
      $(this).prop('checked',true)
      $.each($('input[id="OutwardCheck"]'),function(){
        $(this).attr('checked',true);
      });
      break;
    default:
      $.each($('input[id="OutwardCheck"]'),function(){
        $(this).attr('checked',false);
      });
      break;
  }
});

const CylinderQRMatch = async (data) => {
    $('#preloader').fadeIn();
    $('body').css('overflow', 'hidden');
    $.ajax({
        url: '/QR/Cylinder-Outward-Check',
        type: 'POST',
        headers: {
            'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val(),
        },
        data: {'qr_sl_number' :data },
        success: function(response) {
            $('#preloader').fadeOut();
            $('body').removeAttr('style');
            toastr.success('Cylinder Serial Number Found', 'Success');
            $('#cylinder_gas_type').val(response['cylinder_type']);
            $('input[id="cylinder_gas_vendor"]').val(response['vendor_id']);
            $('#cylinder_gas_vendor_name').val(response['vendor_name']);
            $('#qr_sl_no_id').val(response['cylinder_id']);
            $('.sub-btn').show();
            $('.qr-found-details').show();
            $('#qr-alert').hide();
        },
        error: function(xhr, status, error) {
            // Handle any errors
            $('#preloader').fadeOut();
            $('body').removeAttr('style');
            console.error(status, error, 'Failed');
            toastr.error('Cylinder Serial Number Not Found', 'Failed');
            $('#cylinder_gas_type').val('');
            $('input[id="cylinder_gas_vendor"]').val('');
            $('#cylinder_gas_vendor_name').val('');
            $('#qr_sl_no_id').val('');
            $('.sub-btn').hide();
            $('.qr-found-details').hide();
            $('#qr-alert').show();
        }
    });
}
// End QR Scanner Cylinder Search

// Manual Select Cylinder Search
$('select[id="cylinder_gas_vendor"]').on('change',function(){
    $('#preloader').fadeIn();
    $('body').css('overflow', 'hidden');
    $.ajax({
        url: '/QR/Cylinder-Vendors',
        type: 'POST',
        headers: {
            'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val(),
        },
        data: {'vendor_id' :$(this).val(),'vendor_name': $(this).find('option:selected').text()},
        success: function(response) {
            $('#cylinder_gas_type_manual').val('');
            $('#cylinder_sl_no').find('option').remove();
            var disabledOption = $('<option>').attr({'value':'', 'disabled':true, 'selected':true}).text('Select Cylinder Serial Number');
            $('#cylinder_sl_no').append(disabledOption);
            $.each(response,function(i,val){
                var selectableOpiton = $('<option>').val(val.cylinder_db_id).text(val.cylinder_sl_r_qr_no);
                $('#cylinder_sl_no').append(selectableOpiton);
            });
            $('#preloader').fadeOut();
            $('body').removeAttr('style');
            toastr.success('Vendor Found', 'Success');
        },
        error: function(xhr, status, error) {
            $('#preloader').fadeOut();
            $('body').removeAttr('style');
            console.error(status, error, 'Failed');
            toastr.error('Invalid Vendor Details', 'Error');
        }
    });
});
$('#cylinder_sl_no').on('change',function(){
    $('#preloader').fadeIn();
    $('body').css('overflow', 'hidden');
    $.ajax({
        url: '/QR/Cylinder-List',
        type: 'POST',
        headers: {
            'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val(),
        },
        data: {'cylinder_id' :$(this).val(),'cylinder_sl_no': $(this).find('option:selected').text()},
        success: function(response) {
            $('#cylinder_gas_type_manual').val(response);
            $('#preloader').fadeOut();
            $('body').removeAttr('style');
            toastr.success('Cylinder Found', 'Success');
        },
        error: function(xhr, status, error) {
            // Handle any errors
            $('#preloader').fadeOut();
            $('body').removeAttr('style');
            console.error(status, error, 'Failed');
            toastr.error('Cylinder Not Found', 'Error');
        }
    });
});
// End Manual Select Cylinder Search

$('#OutwardSubmit').on('click',function(){
  $('#outward-dc-form-submit').click();
  if(document.getElementById('outward-dc-form')){

    if(document.getElementById('outward-dc-form').checkValidity()){
      var outwardSelected = [];
      $.each($('input[id="OutwardCheck"]'),function(){
        if($(this).prop('checked')){
          outwardSelected.push($(this).val());
        }
      });
      if(outwardSelected.length === 0){
        toastr.error('Please Select from the below Table.', 'Failed');
      }else{
        $('#preloader').fadeIn();
        $('body').css('overflow', 'hidden');
        $.ajax({
          url: '/QR/Cylinder-Stocking-Out',
          type: 'POST',
          headers: {
              'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val(),
          },
          data: {'outwardSelected' :outwardSelected,'return_dc_no':$('#return_dc_no').val(),'return_remarks':$('#return_remarks').val() },
          success: function(response) {
              $('#preloader').fadeOut();
              $('body').removeAttr('style');
              toastr.success('Outward Successfull', 'Success');
              $.each($('input[id="OutwardCheck"]'),function(){
                if($.inArray($(this).val(), outwardSelected) !== -1){
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
              toastr.error('Outward Action Cannot be Completed', 'Failed');
          }
        });
      }
    }else{
      toastr.error('Please Fill Out the form.', 'Failed');
    }
  }else{
    toastr.warning('Please Select Items to Outward.', 'Failed');
  }
});