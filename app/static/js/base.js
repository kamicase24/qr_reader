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
    console.log("QR Leido : " + decodeText, decodeResult);
    var data = {
      decodeResult: decodeResult,
      decodeText: decodeText
    } 

    // Stop scanning
    htmlscanner.clear().then(() => {
      console.log("Escaneo detenido temporalmente");
      showMessage();

      // Reanudar el escaneo después de 3 segundos
      setTimeout(() => {
        hideMessage();
        htmlscanner.render(onScanSuccess);
        console.log("Escaneo reanudado");
      }, 3000);
    }).catch(error => {
      console.error("Error deteniendo el escaneo", error);
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
        throw new Error('Error al enviar el QR')
      }
      return response.json();
    }).then(data => {
      console.log("Datos enviados al servidor")
      console.log(data)
      alert(`Stock actualizado ${data['sku']}: ${data['qty']}`)
    }).catch(error => {
      console.log('Hubo un problema en la lectura del QR')
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


