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
    const errorElement = document.getElementById("error");
    const vggPredictionSpan = document.getElementById("class-vgg");
    const mobileNetPredictionSpan = document.getElementById("class-mobile-net");
    const cnnPredictionSpan = document.getElementById("class-CNN");
    const classTable = document.getElementById("classTable");

    // Now trigger classification
    const formData = new FormData();
    formData.append("file", file);

    fetch("/classify_image", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            errorElement.textContent = data.error;
            errorElement.style.display = "block";
            classTable.style.display = "none";
            return;
        }

        vggPredictionSpan.textContent = data.predictions.vgg;
        mobileNetPredictionSpan.textContent = data.predictions.mobile_net;
        cnnPredictionSpan.textContent = data.predictions.cnn;

        errorElement.style.display = "none";
        classTable.style.display = "table";
    })
    .catch(err => {
        errorElement.textContent = "Classification failed: " + err;
        errorElement.style.display = "block";
        classTable.style.display = "none";
    });
});