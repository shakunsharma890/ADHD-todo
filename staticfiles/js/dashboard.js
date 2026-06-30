/* =========================
   GLOBAL STATE
========================= */
let taskChart = null;

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
   BRAIN DUMP/TASK 
========================= */
function updateDashboardStats(data) {

    const streak = document.getElementById("streakCount");
    if (streak) {
        streak.innerHTML = `${data.streak} Days 🔥`;
    }

    const brainDumpCount = document.getElementById("brainDumpCount");
    if (brainDumpCount) {
        brainDumpCount.textContent =
            `${data.brain_dump_completed}/${data.brain_dump_total}`;
    }

    const taskCount = document.getElementById("taskCount");
    if (taskCount) {
        taskCount.textContent =
            `${data.main_task_completed}/${data.main_task_total}`;
    }

    const brainDumpBar = document.getElementById("brainDumpBar");
    if (brainDumpBar) {
        brainDumpBar.style.width =
            `${data.brain_dump_progress}%`;
    }

    const taskBar = document.getElementById("taskBar");
    if (taskBar) {
        taskBar.style.width =
            `${data.main_task_progress}%`;
    }

    const totalTasksCount = document.getElementById("totalTasksCount");
    if (totalTasksCount) {
        totalTasksCount.textContent = data.total_tasks;
    }
}
/* =========================
   INIT CHART (ONLY DASHBOARD)
========================= */
document.addEventListener("DOMContentLoaded", function () {

    const totalEl = document.getElementById("totalTasksData");
    const completedEl = document.getElementById("completedTasksData");
    const pendingEl = document.getElementById("pendingTasksData");
    const chartEl = document.getElementById("taskChart");

    if (!totalEl || !completedEl || !pendingEl || !chartEl) return;

    taskChart = new Chart(chartEl, {
        type: "bar",
        data: {
            labels: ["Total", "Completed", "Pending"],
            datasets: [{
                label: "Tasks Overview",
                data: [
                    JSON.parse(totalEl.textContent),
                    JSON.parse(completedEl.textContent),
                    JSON.parse(pendingEl.textContent)
                ],
                backgroundColor: ["#7FCF9A", "#43A047", "#FFB74D"]
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } }
        }
    });
});


/* =========================
   COMPLETE / UNCOMPLETE TASK
========================= */
document.addEventListener("change", function (e) {

    if (!e.target.classList.contains("task-complete")) return;

    // ❌ prevent unchecking completely
    if (!e.target.checked) {
        e.target.checked = true;
        return;
    }

    const taskId = e.target.dataset.id;

    fetch(`/base/complete-task/${taskId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken
        }
    })
    .then(r => r.json())
    .then(data => {

        if (!data.success || !taskChart) return;

        const card = e.target.closest(".task-card");
        const title = card?.querySelector("strong");

        // UI update
        card.style.opacity = "0.6";
        if (title) {
            title.style.textDecoration = "line-through";
        }
        
        const editBtn = card.querySelector(".btn-outline-primary");
            
        if (editBtn) {
        
            editBtn.remove();
        
        }
        // hide check box
        e.target.style.display = "none";
        // Popup goes HERE

        if (data.show_popup) {
        
        Swal.fire({
            icon: "success",
            title: "🔥 Streak Protected!",
            html: `
                <strong>You completed a task today.</strong><br><br>
                Keep going—your future self will thank you.
            `,
            confirmButtonText: "Continue Working",
            confirmButtonColor: "#43A047",
            timer: 4500,
            timerProgressBar: true
        });
        
        }
        // chart update (ONLY forward change)
        taskChart.data.datasets[0].data[1] += 1;
        taskChart.data.datasets[0].data[2] -= 1;

        taskChart.update();
        updateDashboardStats(data);
    });
});
/* =========================
   DELETE TASK
========================= */
document.addEventListener("click", function (e) {

    if (!e.target.classList.contains("delete-task")) return;

    const btn = e.target;               // ✅ lock button
    const taskId = btn.dataset.id;
    const card = btn.closest(".task-card");

    // 🚨 PREVENT DOUBLE CLICK
    btn.disabled = true;

    fetch(`/base/delete-task/${taskId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken,
            "Accept": "application/json"
        }
    })
    .then(res => {

        if (!res.ok) {
            console.log("Already deleted or error");
            return;
        }

        return res.json();
    })
    .then(data => {

        if (!data?.success) return;

        if (taskChart) {

            taskChart.data.datasets[0].data[0] -= 1;

            const isCompleted =
                card.querySelector("strong")?.style.textDecoration === "line-through";

            if (isCompleted) {
                taskChart.data.datasets[0].data[1] -= 1;
            } else {
                taskChart.data.datasets[0].data[2] -= 1;
            }

            taskChart.update();
        }
        if (window.location.pathname.includes("dashboard")) {
            const totalEl = document.getElementById("totalTasksCount");
            if (totalEl) {
                totalEl.textContent = parseInt(totalEl.textContent) - 1;
            }
        }
        card.remove();
        updateDashboardStats(data);
    })
    .catch(err => console.log("Delete error:", err));
});


/* =========================
   ADD TASK
========================= */
const addTaskForm = document.getElementById("add-task-form");

addTaskForm?.addEventListener("submit", function (e) {

    e.preventDefault();

    const formData = new FormData(this);

    fetch("/base/dashboard/", {
        method: "POST",
        headers: { "X-CSRFToken": csrfToken },
        body: formData
    })
    .then(r => r.json())
    .then(data => {
        console.log("Response:", data);


    // SHOW WARNING MESSAGE

    if (!data.success) {

        document.getElementById("brainDumpMessage").innerHTML = `

            <div class="alert alert-warning mb-3">

                ${data.message}

            </div>

        `;

        return;

    }
        if (!data.success || !taskChart) return;
        console.log("Passed success check");
        console.log("Before insert");
        const taskList = document.getElementById("task-list");
        console.log("Task List:", taskList);
        taskList.insertAdjacentHTML("afterbegin", `
            <div class="card task-card mb-3 p-3">
                <div class="d-flex justify-content-between align-items-center">

                    <div class="d-flex align-items-center">

                        <input type="checkbox"
                            class="task-complete me-3"
                            data-id="${data.task_id}">

                        <div>
                            <strong>${data.title}</strong>

                            ${data.is_quick_task ?
                            
                            `<span class="badge bg-secondary ms-2">
                            
                                Quick Task
                            
                            </span>` : ''}
                            <br>
                        </div>

                    </div>

                    <div class="d-flex">

                        <a href="${data.edit_url}"
                           class="btn btn-sm btn-outline-primary">
                            Edit
                        </a>

                        <button
                            type="button"
                            class="btn btn-sm btn-outline-danger delete-task ms-2"
                            data-id="${data.task_id}">
                            Delete
                        </button>

                    </div>

                </div>
            </div>
        `);
        taskChart.data.datasets[0].data[0] += 1;
        taskChart.data.datasets[0].data[2] += 1;
        taskChart.update();
        updateDashboardStats(data);
        this.reset();
    });
});

document.addEventListener("click", function (e) {

    if (!e.target.classList.contains("filter-btn")) return;

    const filter = e.target.dataset.filter;

    fetch(`/base/dashboard-filter/?filter=${filter}`)
    .then(response => response.json())
    .then(data => {

        document.getElementById("task-list").innerHTML = data.html;

    })
    .catch(error => console.log(error));

});

document.querySelectorAll(".progress-bar").forEach(bar => {
    bar.style.width = bar.dataset.width + "%";
});