// Configure Dropzone
Dropzone.autoDiscover = false;

const myDropzone = new Dropzone("#dropzone", {
  url: "/file-upload",
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
  // Check if any files are in the queue
  if (myDropzone.getQueuedFiles().length > 0) {
    // Process the queue (upload the file)
    myDropzone.processQueue();
  } else {
    alert("Please drop an image to classify.");
  }
});
