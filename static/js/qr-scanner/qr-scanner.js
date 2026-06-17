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
      stream.getTracks().forEach(track => track.stop());
      video.srcObject = null;
      formReset();
      $('.stop-scan').off('click');
      $('.re-scan').off('click');
    });
    $('.re-scan').on('click', function () {
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
      stream.getTracks().forEach(track => track.stop());
      clearInterval(scanInterval);
      video.srcObject = null;
      formReset();
      $('.stop-scan').off('click');
      $('.re-scan').off('click');
    });
    $('.re-scan').on('click', function () {
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
          $('.qr_sl_number').val(code.data);
          $('#qr_sl_number').val(code.data);
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