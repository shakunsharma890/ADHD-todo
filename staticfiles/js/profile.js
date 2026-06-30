// profile.js

document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("editForm");
    const button = document.getElementById("updateProfileBtn");

    if (!form || !button) return;

    button.addEventListener("click", function () {

        if (form.style.display === "none") {

            form.style.display = "block";
            button.innerText = "Cancel";

        } else {

            form.style.display = "none";
            button.innerText = "Update Profile";
        }
    });
});