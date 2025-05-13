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

  const file = myDropzone.getAcceptedFiles()[0];
  const formData = new FormData();
  formData.append("file", file);

  errorElement.textContent = "Classifying image...";
  errorElement.style.display = "block";

  // Step 1: Upload the file
  fetch("/upload-handler", {
    method: "POST",
    body: formData,
  })
    .then((uploadRes) => uploadRes.json())
    .then((uploadData) => {
      if (!uploadData.success) {
        throw new Error(uploadData.error || "Upload failed.");
      }

      // Step 2: Send file again for classification
      return fetch("/classify_image", {
        method: "POST",
        body: formData,
      });
    })
    .then((classifyRes) => classifyRes.json())
    .then((result) => {
      if (result.predictions) {
        errorElement.textContent = "Classification successful!";
        console.log("Predictions:", result.predictions);
        document.getElementById("class-vgg").textContent = result.predictions.vgg || "N/A";
        document.getElementById("class-mobile-net").textContent = result.predictions.mobile_net || "N/A";
        document.getElementById("class-CNN").textContent = result.predictions.cnn || "N/A";
        // Optionally display results on the UI
      } else {
        throw new Error(result.error || "Classification failed.");
      }
    })
    .catch((err) => {
      errorElement.textContent = err.message;
      errorElement.style.display = "block";
    });
});
