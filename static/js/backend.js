
// Event listeners for the buttons
document.addEventListener("DOMContentLoaded", function () {
   var uploadedAudio = null; // Store the Audio file object
   var uploadedText = null; // Store the Audio file object
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
         uploadedTextFile = file; // Save globally for later use
         var reader = new FileReader();
         reader.onload = function (e) {
            uploadedTextContent = e.target.result; // Save the text content
            textUploaded(file); // Placeholder function call
         };
         reader.readAsText(file);
      };
      input.click();
   });

   function textUploaded(file) {
      console.log('Text Uploaded:', file.name);
      alert(file.name + "Text uploaded successfully");
      // Text content is now stored in uploadedTextContent
   }

   // Transform Button
   document.getElementById('transformBtn').addEventListener('click', function () {
      if (uploadedAudio !== null) {
         convertAudio(uploadedAudio, uploadedTextFile.name);
      } else if (uploadedTextContent !== "") {
         convertText(uploadedTextContent, uploadedTextFile.name);
      } else {
         console.log('No file uploaded.');
         alert("Please upload a file first");
      }
   });

   // functions to convert the uploaded content

   function convertAudio(audioFile) {
      console.log('Converting audio from video:', audioFile.name);
      alert(audioFile.name + "Audio conversion started");
      // Implement the logic to convert or handle the video file here

      // after indexer is done, call the function to convert the text
      convertText("This is a placeholder text");
   }

   async function convertText(textContent, filename) {
      console.log('Sending POST request with text content:', textContent);
      try {
         const response = await fetch('/api/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: textContent }),
         });
         if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
         }
         const data = await response.json();
         console.log('Received translated text:', data.translated_text);
         saveTextAsFile(data.translated_text, filename);
      } catch (error) {
         console.error('Error during text conversion:', error);
      }
   }

   // async function convertText(textContent, filename) {
   //    alert("Text conversion started");
   //    console.log('Text Content:', textContent);
   //    try {
   //       const response = await fetch('/api/translate', {
   //          method: 'POST',
   //          headers: {
   //             'Content-Type': 'application/json',
   //          },
   //          body: JSON.stringify({ text: textContent }),
   //       });
   //       if (!response.ok) {
   //          throw new Error(`HTTP error! status: ${response.status}`);
   //       }
   //       const data = await response.json();
   //       alert("Text conversion completed");
   //       console.log('Translated Text:', data.translated_text);

   //       // Automatically save the translated text to a file
   //       saveTextAsFile(data.translated_text, filename);

   //    } catch (error) {
   //       console.error('Error during text conversion:', error);
   //       alert("Failed to convert text. Check the console for more details.");
   //    }
   // }

   function saveTextAsFile(textToSave, filename) {
      const blob = new Blob([textToSave], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename + ".txt";  // You can specify the default file name here
      document.body.appendChild(a);
      a.click();  // Simulates a click on the link to trigger the download
      document.body.removeChild(a);
      URL.revokeObjectURL(url);


   }
});


