
// Event listeners for the buttons
document.addEventListener("DOMContentLoaded", function () {
   var uploadedAudio = null; // Store the Audio file object
   var uploadedTextContent = ""; // Store the text content

   // Video Upload
   document.getElementById('loadAudioBtn').addEventListener('click', function () {
      var input = document.createElement('input');
      input.type = 'file';
      input.accept = 'audio/*';
      input.onchange = e => {
         uploadedAudio = e.target.files[0]; // Save the file object
         audioUploaded(uploadedAudio); // Placeholder function call
      }
      input.click();
   });

   function audioUploaded(file) {
      console.log('Audio Uploaded:', file.name);
      alert("Audio uploaded successfully");
      // Here you would typically handle the file further, e.g., read its content if needed
   }

   // Text Upload
   document.getElementById('loadTextBtn').addEventListener('click', function () {
      var input = document.createElement('input');
      input.type = 'file';
      input.accept = 'text/*';
      input.onchange = e => {
         var file = e.target.files[0];
         var reader = new FileReader();
         reader.onload = function (e) {
            uploadedTextContent = e.target.result; // Save the text content
            textUploaded(file); // Placeholder function call
         }
         reader.readAsText(file);
      }
      input.click();
   });

   function textUploaded(file) {
      console.log('Text Uploaded:', file.name);
      alert("Text uploaded successfully");
      // Text content is now stored in uploadedTextContent
   }

   // Transform Button
   document.getElementById('transformBtn').addEventListener('click', function () {
      if (uploadedAudio !== null) {
         convertAudio(uploadedAudio);
      } else if (uploadedTextContent !== "") {
         convertText(uploadedTextContent);
      } else {
         console.log('No file uploaded.');
         alert("Please upload a file first");
      }
   });

   // functions to convert the uploaded content

   function convertAudio(audioFile) {
      console.log('Converting audio from video:', audioFile.name);
      alert("Audio conversion started");
      // Implement the logic to convert or handle the video file here

      // after indexer is done, call the function to convert the text
      convertText("This is a placeholder text");
   }

   async function convertText(textContent) {
      alert("Text conversion started");
      console.log('Text Content:', textContent);
      // Call a backend API (e.g., Flask or FastAPI) that wraps around your Python model
      const response = await fetch('/api/translate', {
         method: 'POST',
         headers: {
            'Content-Type': 'application/json',
         },
         body: JSON.stringify({ text: textContent }),
      });
      const translatedText = await response.json();
      alert("Text conversion completed");
      // Use translatedText as needed
   }

});


