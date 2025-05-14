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
            if (this.files.length === 1) {
                uploadImageElement.style.display = "none";
                uploadTextImageElement.style.display = "none";
            }
        });

        this.on("removedfile", function () {
            if (this.files.length === 0) {
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

let currentMode = "disease";

document.getElementById("link-classify-disease").addEventListener("click", function (e) {
    currentMode = "disease";
    document.getElementById("prediction-type-header").textContent = "Predicted Disease";
    document.getElementById("model_1").textContent = "VGG";
    document.getElementById("model_2").textContent = "MobileNet";
    document.getElementById("model_3").textContent = "CNN";
    clearTable();
});

document.getElementById("link-classify-age").addEventListener("click", function (e) {
    currentMode = "age";
    document.getElementById("prediction-type-header").textContent = "Predicted Age";
    clearTable();
});

document.getElementById("link-classify-variety").addEventListener("click", function (e) {
    currentMode = "variety";
    document.getElementById("prediction-type-header").textContent = "Predicted Variety";
    document.getElementById("model_1").textContent = "CNN";
    document.getElementById("model_2").textContent = "ResNet50";
    document.getElementById("model_3").textContent = "EfficientNet";
    clearTable();
});

function clearTable() {
    for (let i = 1; i <= 3; i++) {
        document.getElementById(`label_${i}`).textContent = "-";
        document.getElementById(`confidence_${i}`).textContent = "-";
    }
}

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
    myDropzone.processQueue();
});

myDropzone.on("success", function (file, response) {
    const errorElement = document.getElementById("error");
    const classTable = document.getElementById("classTable");

    // Now trigger classification
    const formData = new FormData();
    formData.append("file", file);
    formData.append("mode", currentMode);

    fetch("/classify_image", {
        method: "POST",
        body: formData,
    })
        .then((res) => res.json())
        .then((data) => {
            if (data.error) {
                errorElement.textContent = data.error;
                errorElement.style.display = "block";
                classTable.style.display = "none";
                return;
            }

            if (currentMode === "disease") {
                document.getElementById("label_1").textContent = data.predictions.vgg.label;
                document.getElementById("confidence_1").textContent = data.predictions.vgg.confidence;

                document.getElementById("label_2").textContent = data.predictions.mobile_net.label;
                document.getElementById("confidence_2").textContent = data.predictions.mobile_net.confidence;

                document.getElementById("label_3").textContent = data.predictions.cnn.label;
                document.getElementById("confidence_3").textContent = data.predictions.cnn.confidence;
            }

            if (currentMode === "variety") {
                document.getElementById("label_1").textContent = data.predictions.cnn.label;
                document.getElementById("confidence_1").textContent = data.predictions.cnn.confidence;

                document.getElementById("label_2").textContent = data.predictions.resnet50.label;
                document.getElementById("confidence_2").textContent = data.predictions.resnet50.confidence;

                document.getElementById("label_3").textContent = data.predictions.efficient_net.label;
                document.getElementById("confidence_3").textContent = data.predictions.efficient_net.confidence;
            }

            errorElement.style.display = "none";
            classTable.style.display = "table";
        })
        .catch((err) => {
            errorElement.textContent = "Classification failed: " + err;
            errorElement.style.display = "block";
            classTable.style.display = "none";
        });
});
