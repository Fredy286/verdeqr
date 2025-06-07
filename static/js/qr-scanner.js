// QR Scanner Script for VerdeQR
document.addEventListener('DOMContentLoaded', function() {
    const scanButton = document.getElementById('scanButton');

    if (scanButton) {
        scanButton.addEventListener('click', startQRScanner);
    }

    function startQRScanner() {
        // Create modal overlay
        const overlay = document.createElement('div');
        overlay.className = 'qr-scanner-overlay';

        // Create scanner container
        const scannerContainer = document.createElement('div');
        scannerContainer.className = 'qr-scanner-container';

        // Create video element
        const video = document.createElement('video');
        video.id = 'qr-video';

        // Create canvas element (hidden)
        const canvas = document.createElement('canvas');
        canvas.style.display = 'none';

        // Create close button
        const closeButton = document.createElement('button');
        closeButton.className = 'qr-scanner-close';
        closeButton.innerHTML = '<i class="fas fa-times"></i>';
        closeButton.addEventListener('click', stopScanner);

        // Create scanner message
        const message = document.createElement('div');
        message.className = 'qr-scanner-message';
        message.textContent = 'Apunta la cámara al código QR';

        // Append elements
        scannerContainer.appendChild(video);
        scannerContainer.appendChild(canvas);
        scannerContainer.appendChild(closeButton);
        scannerContainer.appendChild(message);
        overlay.appendChild(scannerContainer);
        document.body.appendChild(overlay);

        // Start camera
        startCamera();

        function startCamera() {
            // Check if browser supports getUserMedia
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                navigator.mediaDevices.getUserMedia({
                    video: {
                        facingMode: 'environment',
                        width: { ideal: 1280 },
                        height: { ideal: 720 }
                    }
                })
                .then(function(stream) {
                    video.srcObject = stream;
                    video.setAttribute('playsinline', true); // required for iOS
                    video.play();

                    // Start scanning
                    scanQRCode(video, canvas);
                })
                .catch(function(error) {
                    console.error("Error accessing camera:", error);
                    message.textContent = 'Error al acceder a la cámara. Por favor, permite el acceso a la cámara e intenta de nuevo.';
                    message.style.color = '#dc3545';
                });
            } else {
                console.error("getUserMedia not supported");
                message.textContent = 'Tu navegador no soporta el acceso a la cámara.';
                message.style.color = '#dc3545';
            }
        }

        function scanQRCode(videoElement, canvasElement) {
            const context = canvasElement.getContext('2d');
            let scanInterval;

            // Check if jsQR is available
            if (typeof jsQR === 'undefined') {
                console.error("jsQR library not found");
                message.textContent = 'Error: Biblioteca de escaneo QR no encontrada.';
                message.style.color = '#dc3545';
                return;
            }

            // Create scanning indicator
            const scanningIndicator = document.createElement('div');
            scanningIndicator.className = 'scanning-indicator';
            scannerContainer.appendChild(scanningIndicator);

            // Counter for scanning attempts
            let scanAttempts = 0;
            const maxScanAttempts = 300; // 30 seconds at 100ms intervals

            // Start scanning
            scanInterval = setInterval(() => {
                if (videoElement.readyState === videoElement.HAVE_ENOUGH_DATA) {
                    // Set canvas dimensions to match video
                    canvasElement.height = videoElement.videoHeight;
                    canvasElement.width = videoElement.videoWidth;

                    // Draw current video frame to canvas
                    context.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);

                    // Get image data from canvas
                    const imageData = context.getImageData(0, 0, canvasElement.width, canvasElement.height);

                    try {
                        // Use jsQR to scan the image data
                        const code = jsQR(imageData.data, imageData.width, imageData.height);

                        if (code) {
                            console.log("QR Code detected:", code);
                            clearInterval(scanInterval);
                            onQRCodeDetected(code.data);
                        } else {
                            // Update scanning animation
                            scanningIndicator.style.transform = `rotate(${scanAttempts * 12}deg)`;

                            // Increment scan attempts
                            scanAttempts++;

                            // If we've been scanning for too long without success
                            if (scanAttempts >= maxScanAttempts) {
                                clearInterval(scanInterval);
                                message.textContent = 'No se detectó ningún código QR. Inténtalo de nuevo.';
                                message.style.color = '#dc3545';
                                scanningIndicator.style.display = 'none';

                                // Add a retry button
                                const retryButton = document.createElement('button');
                                retryButton.className = 'retry-button';
                                retryButton.textContent = 'Intentar de nuevo';
                                retryButton.addEventListener('click', () => {
                                    // Remove retry button
                                    scannerContainer.removeChild(retryButton);
                                    // Reset message
                                    message.textContent = 'Apunta la cámara al código QR';
                                    message.style.color = 'white';
                                    // Show scanning indicator again
                                    scanningIndicator.style.display = 'block';
                                    // Reset scan attempts
                                    scanAttempts = 0;
                                    // Start scanning again
                                    scanInterval = setInterval(() => {
                                        if (videoElement.readyState === videoElement.HAVE_ENOUGH_DATA) {
                                            // Set canvas dimensions to match video
                                            canvasElement.height = videoElement.videoHeight;
                                            canvasElement.width = videoElement.videoWidth;

                                            // Draw current video frame to canvas
                                            context.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);

                                            // Get image data from canvas
                                            const imageData = context.getImageData(0, 0, canvasElement.width, canvasElement.height);

                                            try {
                                                // Use jsQR to scan the image data
                                                const code = jsQR(imageData.data, imageData.width, imageData.height);

                                                if (code) {
                                                    console.log("QR Code detected:", code);
                                                    clearInterval(scanInterval);
                                                    onQRCodeDetected(code.data);
                                                } else {
                                                    // Update scanning animation
                                                    scanningIndicator.style.transform = `rotate(${scanAttempts * 12}deg)`;

                                                    // Increment scan attempts
                                                    scanAttempts++;
                                                }
                                            } catch (error) {
                                                console.error("Error scanning QR code:", error);
                                            }
                                        }
                                    }, 100);
                                    scannerContainer.dataset.scanInterval = scanInterval;
                                });
                                scannerContainer.appendChild(retryButton);
                            }
                        }
                    } catch (error) {
                        console.error("Error scanning QR code:", error);
                    }
                }
            }, 100); // Check every 100ms

            // Store the interval ID so we can clear it later
            scannerContainer.dataset.scanInterval = scanInterval;
        }

        function onQRCodeDetected(data) {
            // Show success message
            message.textContent = '¡Código QR detectado!';
            message.style.color = '#28a745';

            // Create success animation
            const successIcon = document.createElement('div');
            successIcon.className = 'qr-success-icon';
            successIcon.innerHTML = '<i class="fas fa-check-circle"></i>';
            scannerContainer.appendChild(successIcon);

            // Stop the scanner after a short delay
            setTimeout(() => {
                stopScanner();

                // Show the QR code data
                console.log("QR Code data:", data);

                // Handle different types of QR codes
                if (data.startsWith('http')) {
                    // If it's a URL, navigate to it
                    window.location.href = data;
                } else if (data.startsWith('SMSTO:') || data.startsWith('SMS:')) {
                    // If it's an SMS
                    window.location.href = data;
                } else if (data.startsWith('MATMSG:') || data.startsWith('MAILTO:') || data.startsWith('mailto:')) {
                    // If it's an email
                    window.location.href = data.toLowerCase();
                } else if (data.startsWith('tel:')) {
                    // If it's a phone number
                    window.location.href = data;
                } else if (data.startsWith('WIFI:')) {
                    // If it's WiFi credentials, just show the data
                    alert("Datos WiFi escaneados: " + data);
                } else if (data.startsWith('BEGIN:VCARD') || data.startsWith('BEGIN:VEVENT')) {
                    // If it's a contact or calendar event, just show the data
                    alert("Datos escaneados: " + data);
                } else {
                    // For any other type of data, try to search for it
                    window.location.href = '/buscar_arbol?q=' + encodeURIComponent(data);
                }
            }, 1500);
        }

        function stopScanner() {
            // Clear the scanning interval if it exists
            if (scannerContainer.dataset.scanInterval) {
                clearInterval(parseInt(scannerContainer.dataset.scanInterval));
            }

            // Stop the video stream
            if (video.srcObject) {
                const tracks = video.srcObject.getTracks();
                tracks.forEach(track => track.stop());
                video.srcObject = null;
            }

            // Remove the overlay
            document.body.removeChild(overlay);
        }
    }
});
