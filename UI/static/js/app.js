// Configure Dropzone
Dropzone.autoDiscover = false;

const myDropzone = new Dropzone("#dropzone", {
  url: "/upload-handler",
  paramName: "file",
  maxFilesize: 10, // MB
  acceptedFiles: "image/png, image/jpeg",
  maxFiles: 1,
  clickable: true,
  addRemoveLinks: true,
  dictRemoveFile: "Remove",
  dictInvalidFileType: "Only PNG and JPG images are allowed",
  autoProcessQueue: false,
  init: function () {
    const uploadImageElement = document.getElementById("upload-image");
    const uploadTextImageElement = document.getElementById("upload-image-text");
    const errorElement = document.getElementById("error"); // Get the error element

    this.on("addedfile", function (file) {
      // Hide the upload image when a file is added
      uploadImageElement.style.display = "none";
      uploadTextImageElement.style.display = "none";
    });

    this.on("removedfile", function (file) {
      if (this.files.length === 0) {
        // Show the upload image when all files are removed
        uploadImageElement.style.display = "block";
        uploadTextImageElement.style.display = "block";
        errorElement.style.display = "none";
      }
    });

    this.on("success", function (file, response) {
      console.log("File uploaded successfully");
    });

    this.on("error", function (file, errorMessage) {
      console.error(errorMessage);
    });
  },
});

// Add event listener to the Classify button
document.getElementById("submitBtn").addEventListener("click", function () {
        const errorElement = document.getElementById("error");
        errorElement.style.display = "none";

        if (myDropzone.getAcceptedFiles().length === 0) {
            errorElement.textContent = "Please upload an image before classifying.";
            errorElement.style.display = "block";
            return;
        }
        errorElement.textContent = "Classifying image...";
        errorElement.style.display = "block";
        myDropzone.processQueue(); // Start the upload and classification
    });

    myDropzone.on("success", function (file, response) {
        const resultsDiv = document.getElementById("results");
        const vggPredictionSpan = document.getElementById("vgg-prediction");
        const mobileNetPredictionSpan = document.getElementById("mobile-net-prediction");
        const cnnPredictionSpan = document.getElementById("cnn-prediction");
        const errorElement = document.getElementById("error");

        if (response.error) {
            errorElement.textContent = response.error;
            errorElement.style.display = "block";
            resultsDiv.style.display = "none";
            return;
        }

        vggPredictionSpan.textContent = response.predictions.vgg;
        mobileNetPredictionSpan.textContent = response.predictions.mobile_net;
        cnnPredictionSpan.textContent = response.predictions.cnn;
        resultsDiv.style.display = "block";
        errorElement.style.display = "none";
    });

    myDropzone.on("error", function (file, errorMessage) {
        const errorElement = document.getElementById("error");
        errorElement.textContent = "Error during classification: " + errorMessage;
        errorElement.style.display = "block";
        document.getElementById("results").style.display = "none";
    });

    myDropzone.on("complete", function() {
        myDropzone.removeAllFiles();
    });