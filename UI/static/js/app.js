// Configure Dropzone
Dropzone.autoDiscover = false;

const myDropzone = new Dropzone("#dropzone", {
    url: "#", // Disable Dropzone’s built-in AJAX upload
    autoProcessQueue: false,
    maxFilesize: 10, // MB
    acceptedFiles: "image/png, image/jpeg",
    maxFiles: 1,
    clickable: true,
    addRemoveLinks: true,
    dictRemoveFile: "Remove",
    dictInvalidFileType: "Only PNG and JPG images are allowed",
    init: function () {
        const uploadImageElement = document.getElementById("upload-image");
        const uploadTextImageElement = document.getElementById("upload-image-text");
        const errorElement = document.getElementById("error");

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
    document.getElementById("model_1").textContent = "CNN";
    document.getElementById("model_2").textContent = "Nasnet";
    document.getElementById("model_3").textContent = "-";
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
    const classTable = document.getElementById("classTable");
    errorElement.style.display = "none";

    const files = myDropzone.getAcceptedFiles();
    if (files.length === 0) {
        errorElement.textContent = "Please upload an image before classifying.";
        errorElement.style.display = "block";
        return;
    }

    const file = files[0];

    // Step 1: Upload the image to the server
    const uploadData = new FormData();
    uploadData.append("file", file);

    errorElement.textContent = "Uploading image...";
    errorElement.style.display = "block";

    fetch("/upload-handler", {
        method: "POST",
        body: uploadData,
    })
        .then((res) => res.json())
        .then((uploadResponse) => {
            if (!uploadResponse.success) {
                throw new Error(uploadResponse.error || "Upload failed");
            }

            // Step 2: Classify the image
            const classifyData = new FormData();
            classifyData.append("file", file);
            classifyData.append("mode", currentMode);

            errorElement.textContent = "Classifying image...";

            return fetch("/classify_image", {
                method: "POST",
                body: classifyData,
            });
        })
        .then((res) => res.json())
        .then((data) => {
            if (data.error) {
                throw new Error(data.error);
            }

            // Update UI
            if (currentMode === "disease") {
                document.getElementById("label_1").textContent = data.predictions.vgg.label;
                document.getElementById("confidence_1").textContent = data.predictions.vgg.confidence;
                document.getElementById("label_2").textContent = data.predictions.mobile_net.label;
                document.getElementById("confidence_2").textContent = data.predictions.mobile_net.confidence;
                document.getElementById("label_3").textContent = data.predictions.cnn.label;
                document.getElementById("confidence_3").textContent = data.predictions.cnn.confidence;
            } else if (currentMode === "variety") {
                document.getElementById("label_1").textContent = data.predictions.cnn.label;
                document.getElementById("confidence_1").textContent = data.predictions.cnn.confidence;
                document.getElementById("label_2").textContent = data.predictions.resnet50.label;
                document.getElementById("confidence_2").textContent = data.predictions.resnet50.confidence;
                document.getElementById("label_3").textContent = data.predictions.efficient_net.label;
                document.getElementById("confidence_3").textContent = data.predictions.efficient_net.confidence;
            }

            if (currentMode === "age") {
                document.getElementById("label_1").textContent = data.predictions.cnn.label;

                document.getElementById("label_2").textContent = data.predictions.nasnet.label;
            }

            errorElement.style.display = "none";
            classTable.style.display = "table";
        })
        .catch((err) => {
            errorElement.textContent = "Error: " + err.message;
            errorElement.style.display = "block";
            classTable.style.display = "none";
        });
});
