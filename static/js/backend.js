/**
 * This script handles the uploading and processing of audio/video and text files.
 * Workflow:
 * 1. Users can upload audio/video files which are then sent to Azure Video Indexer for processing.
 * 2. Users can upload text files directly.
 * 3. Users can trigger a transformation on the uploaded content which involves translating the text.
 * 4. The processed results (translated text) can be downloaded.
 */

document.addEventListener("DOMContentLoaded", function () {
   var uploadedAudio = null; // Store the Audio/Video file object for reference.
   var uploadedTextContent = ""; // Store the text content, either directly uploaded or obtained from Azure Video Indexer.

   // Handles audio/video file uploads
   document.getElementById('loadAudioBtn').addEventListener('click', function () {
      var input = document.createElement('input');
      input.type = 'file';
      input.accept = 'video/*, audio/*';  // Set the accepted file types to video and audio.
      input.onchange = async e => {
         uploadedAudio = e.target.files[0]; // Save the selected file.
         var formData = new FormData();
         formData.append('file', uploadedAudio); // Append the file to form data for HTTP POST.

         try {
            // Send the file to the server for upload to Azure Video Indexer.
            const uploadResponse = await fetch('/upload', {
               method: 'POST',
               body: formData,
            });
            if (!uploadResponse.ok) {
               throw new Error(`HTTP error during upload! Status: ${uploadResponse.status}`);
            }
            const data = await uploadResponse.json();
            console.log('Audio/Video uploaded. Processing started. Video ID:', data.videoId);
            alert("Upload successful! Processing started.");

            // Initiate polling to check when the processing is complete.
            getProcessingResults(data.videoId);
         } catch (error) {
            console.error('Error during upload:', error);
            alert("Failed to upload and process audio/video.");
         }
      };
      input.click();  // Trigger the file selection dialog.
   });

   // Polling function to check processing status and retrieve results
   async function getProcessingResults(videoId) {
      try {
         let results = await fetch(`/results/${videoId}`);
         if (!results.ok) {
            throw new Error(`HTTP error while fetching results! Status: ${results.status}`);
         }
         const data = await results.json();
         if (data.processingStatus === "Processed") {
            uploadedTextContent = data.transcript; // needs to be set to the text content
            alert("Processing complete! Text ready for transformation.");
         } else {
            setTimeout(() => getProcessingResults(videoId), 5000); // Retry after 5 seconds if not processed.
         }
      } catch (error) {
         console.error('Error during processing results:', error);
         alert("Failed to process audio/video.");
      }
   }

   // Handles text file uploads
   document.getElementById('loadTextBtn').addEventListener('click', function () {
      var input = document.createElement('input');
      input.type = 'file';
      input.accept = 'text/*';  // Set the accepted file types to text.
      input.onchange = e => {
         var file = e.target.files[0];
         var reader = new FileReader();
         reader.onload = function (e) {
            uploadedTextContent = e.target.result; // Save the loaded text content.
            alert(file.name + " text uploaded successfully");
         };
         reader.readAsText(file);  // Read the file as text.
      };
      input.click();  // Trigger the file selection dialog.
   });

   // Handle transformation request
   document.getElementById('transformBtn').addEventListener('click', function () {
      if (!uploadedTextContent) {
         console.log('No file uploaded.');
         alert("Please upload a file first");
      } else {
         alert("Transformation started. Please wait for the download to begin.")
         transformText(uploadedTextContent);
      }
   });

   // Send the text to the server for translation
   async function transformText(textContent) {
      console.log('Sending POST request with text content:', textContent);
      try {
         const response = await fetch('/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: textContent }),
         });
         if (!response.ok) {
            throw new Error(`HTTP error during translation! Status: ${response.status}`);
         }
         const data = await response.json();
         console.log('Received translated text:', data.translated_text);
         saveTextAsFile(data.translated_text, "translated_output");
      } catch (error) {
         console.error('Error during text translation:', error);
      }
   }

   // Save the translated text as a downloadable file
   function saveTextAsFile(textToSave, filename) {
      const blob = new Blob([textToSave], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename + ".txt";  // Set the default file name for download.
      document.body.appendChild(a);
      a.click();  // Simulate a click on the link to trigger the download.
      document.body.removeChild(a);
      URL.revokeObjectURL(url);  // Clean up the URL object.
   }
});
