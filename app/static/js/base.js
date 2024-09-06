function domReady(fn) {
  if (
    document.readyState === "complete" ||
    document.readyState === "interactive"
  ) {
    setTimeout(fn, 1000);
  } else {
    document.addEventListener("DOMContentLoaded", fn);
  }
}

domReady(function () {
  let htmlscanner;

  // Mostrar mensaje
  function showMessage() {
    document.getElementById('message').style.display = 'block';
  }

  // Ocultar mensaje
  function hideMessage() {
    document.getElementById('message').style.display = 'none';
  }

  // If found you qr code
  function onScanSuccess(decodeText, decodeResult) {
    console.log("QR Code Readed: " + decodeText, decodeResult);
    var data = {
      decodeResult: decodeResult,
      decodeText: decodeText
    } 

    // Stop scanning
    htmlscanner.clear().then(() => {
      console.log("Scanning temporarily stopped");
      showMessage();

      // Reanudar el escaneo después de 3 segundos
      setTimeout(() => {
        hideMessage();
        htmlscanner.render(onScanSuccess);
        console.log("Scanning resumed");
      }, 3000);
    }).catch(error => {
      console.error("Error, stopping scanning", error);
    });

    fetch(
      '/read_qr_result',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      }
    ).then(response => {
      if (!response.ok) {
        throw new Error('Error sending the QR')
      }
      return response.json();
    }).then(data => {
      console.log("Data sent to server")
      console.log(data)
      if(data['success']){
        alert(`Stock updated
          Product (SKU): ${data['info']['sku']}
          Lot #: ${data['info']['lot_number']}
          Qty Updated: ${data['info']['qty']}`)
      } else {
        alert(`${data['result']['error']}`)
      }

    }).catch(error => {
      console.log(`There was a problem reading the QR code ${error}`)
    })
  }

  htmlscanner = new Html5QrcodeScanner(
    "qr-reader",
    { 
      fps: 10, 
      qrbox: { width: 250, height: 250 },
      rememberLastUsedCamera: true
    },
  );
  htmlscanner.render(onScanSuccess);
});