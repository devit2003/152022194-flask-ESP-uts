async function fetchData() {
    const response = await fetch('/api/sensorData');
    const data = await response.json();
    return data;
}

async function updateCharts() {
    const data = await fetchData();

    const labels = data.map(item => new Date(item.timestamp).toLocaleTimeString());
    const suhuData = data.filter(item => item.sensorType === 'temperature').map(item => item.value);
    const kelembapanData = data.filter(item => item.sensorType === 'humidity').map(item => item.value);

    const suhuCtx = document.getElementById('suhuChart').getContext('2d');
    new Chart(suhuCtx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Suhu',
                data: suhuData,
                borderColor: 'rgba(255, 159, 243, 0.8)',
                backgroundColor: 'rgba(255, 159, 243, 0.2)',
                pointBackgroundColor: 'rgba(255, 159, 243, 0.8)',
                pointRadius: 3,
                borderWidth: 1.5,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                x: {
                    ticks: { color: '#4a5568', maxRotation: 0 },
                    grid: { display: false }
                },
                y: {
                    ticks: { color: '#4a5568' },
                    grid: { color: 'rgba(200, 200, 200, 0.2)' }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: false
                }
            }
        }
    });

    const kelembapanCtx = document.getElementById('kelembapanChart').getContext('2d');
    new Chart(kelembapanCtx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Kelembapan',
                data: kelembapanData,
                borderColor: 'rgba(129, 236, 236, 0.8)',
                backgroundColor: 'rgba(129, 236, 236, 0.2)',
                pointBackgroundColor: 'rgba(129, 236, 236, 0.8)',
                pointRadius: 3,
                borderWidth: 1.5,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                x: {
                    ticks: { color: '#4a5568', maxRotation: 0 },
                    grid: { display: false }
                },
                y: {
                    ticks: { color: '#4a5568' },
                    grid: { color: 'rgba(200, 200, 200, 0.2)' }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: false
                }
            }
        }
    });
}

updateCharts();
setInterval(updateCharts, 5000);
