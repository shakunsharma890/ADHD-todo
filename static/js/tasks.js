function showForm() {
    const form = document.getElementById("task-form");
    form.style.display = (form.style.display === "none") ? "block" : "none";
}


/* =========================
   CSRF TOKEN
========================= */
function getCookie(name) {
    let cookieValue = null;

    if (document.cookie) {
        document.cookie.split(';').forEach(cookie => {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.split('=')[1]);
            }
        });
    }

    return cookieValue;
}

const csrfToken = getCookie('csrftoken');


/* =========================
   COMPLETE TASK
========================= */
document.addEventListener("change", function (e) {

    if (!e.target.classList.contains("task-complete")) return;

    const checkbox = e.target;

    // ❌ BLOCK UNCHECKING
    if (!checkbox.checked) {
        checkbox.checked = true;
        return;
    }

    const taskId = checkbox.dataset.id;

    fetch(`/base/complete-task/${taskId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken
        }
    })
    .then(r => r.json())
    .then(data => {

        if (!data.success) return;

        const card = checkbox.closest(".task-card");
        const title = card.querySelector("strong");

        // UI update
        card.style.opacity = "0.6";
        if (title) {
            title.style.textDecoration = "line-through";
        }
        const editBtn = card.querySelector(".btn-outline-primary");

            if (editBtn) {
            
                editBtn.remove();
            
            }
        // 🔒 HARD LOCK (IMPORTANT)
        checkbox.disabled = true;
    });
});
/* =========================
   DELETE TASK
========================= */
document.addEventListener("click", function (e) {

    const btn = e.target.closest(".delete-task");
    if (!btn) return;

    const taskId = btn.dataset.id;
    const card = btn.closest(".task-card");

    btn.disabled = true;

    fetch(`/base/delete-task/${taskId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken,
            "Accept": "application/json"
        }
    })
    .then(r => r.json())
    .then(data => {

        if (!data.success) return;
        if (window.location.pathname.includes("dashboard")) {
            const totalEl = document.getElementById("totalTasksCount");
            if (totalEl) {
                totalEl.textContent = parseInt(totalEl.textContent) - 1;
            }
        }

        card.remove();
    })
    .catch(err => console.log("Delete error:", err));
});
window.csrfToken = getCookie('csrftoken');

document.querySelector("#task-form form")?.addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData(this);

    fetch("/base/tasks/", {
        method: "POST",
        body: formData,
        headers: {
            "X-CSRFToken": csrfToken
        }
    })
    .then(res => res.json())
    .then(data => {

        if (!data.success) return;

        // 👉 STEP 3: CHECK PRIORITY
        if (data.is_high) {
            showHighPriorityPopup(data);
        } else {
            addTaskToUI(data); // normal insert
        }

        this.reset();
    });
});
function showHighPriorityPopup(data) {

    const popup = document.createElement("div");

    popup.innerHTML = `
        <div class="popup-overlay">
            <div class="popup-box">
                <h4>⚡ High Priority Task Added</h4>
                <p>${data.title}</p>

                <div class="popup-buttons">
                    <button id="stay-btn">Stay Here</button>
                    <button id="focus-btn">Go to Focus Timer</button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(popup);

    document.getElementById("stay-btn").onclick = () => {
        popup.remove();
        addTaskToUI(data);
    };

    document.getElementById("focus-btn").onclick = () => {
        window.location.href = "/base/focus_timer/";
    };
}
function addTaskToUI(data) {
    const taskList = document.getElementById("task-list");
    const stepsHTML = data.steps.map(step =>
    `<li class="step-item">${step}</li>`
    ).join("");
    taskList.insertAdjacentHTML("afterbegin", `
        <div class="card task-card p-3 mb-3">

            <div class="d-flex justify-content-between align-items-center">

                <div class="d-flex align-items-center">

                    <input type="checkbox"
                           class="task-complete me-3"
                           data-id="${data.task_id}">

                    <div>
                        <strong>${data.title}</strong>


                            <span class="category-tag">

                                ${data.category}

                            </span>

                            <ul class ='mt-2'>

                                ${stepsHTML}

                            </ul>

                            <small class="text-muted">

                                Priority: ${data.priority} |

                                Due: ${data.due_date}

                            </small>
                    </div>

                </div>

                <div class="d-flex">

                    <a href="${data.edit_url}"
                       class="btn btn-sm btn-outline-primary">
                        Edit
                    </a>

                    <button type="button"
                            class="btn btn-sm btn-outline-danger delete-task ms-2"
                            data-id="${data.task_id}">
                        Delete
                    </button>

                </div>

            </div>

        </div>
    `);
}