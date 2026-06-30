document.addEventListener("DOMContentLoaded", function () {

    console.log("Total:", totalTasks);
    console.log("Completed:", completedTasks);
    console.log("Pending:", pendingTasks);
    console.log("total Focus Sessions:", totalFocusSessions);
    const ctx = document.getElementById('taskChart');

    if (ctx) {

        new Chart(ctx, {

            type: 'bar',

            data: {

                labels: ['Total', 'Completed', 'Pending', 'Total Focus Sessions'],
                datasets: [{

                    label: 'Tasks & Focus',

                    data: [

                        Number(totalTasks || 0),
                        Number(completedTasks || 0),
                        Number(pendingTasks || 0),
                        Number(totalFocusSessions || 0)

                    ],
                    backgroundColor: ["#7FCF9A", "#43A047", "#FFB74D","#4DB6AC"],
                    borderWidth: 1

                }]

            },

            options: {

                responsive: true,

                scales: {

                    y: {

                        beginAtZero: true

                    }

                }

            }

        });

    }

});