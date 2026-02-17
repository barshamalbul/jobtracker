function animateCounts() {
    const counters = document.querySelectorAll(".count");

    counters.forEach(counter => {
        const target = +counter.innerText;
        let current = 0;
        const increment = target / 30;

        const updateCount = () => {
            if (current < target) {
                current += increment;
                counter.innerText = Math.ceil(current);
                requestAnimationFrame(updateCount);
            } else {
                counter.innerText = target;
            }
        };

        updateCount();
    });
}

document.addEventListener("DOMContentLoaded", animateCounts);


document.addEventListener("DOMContentLoaded", function () {

    const ctx = document.getElementById('statusChart');

    if (ctx) {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Applied', 'Interview', 'Offer', 'Rejected'],
                datasets: [{
                    label: 'Applications',
                    data: [
                        document.querySelector('[data-status="Applied"] .count').innerText,
                        document.querySelector('[data-status="Interview"] .count').innerText,
                        document.querySelector('[data-status="Offer"] .count').innerText,
                        document.querySelector('[data-status="Rejected"] .count').innerText
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }
});
