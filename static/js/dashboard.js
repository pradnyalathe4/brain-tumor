let tumorChart = null;

async function loadStats() {
    try {
        const res = await apiFetch("/api/scans/stats");
        if (!res.ok) throw new Error("Failed to load stats");
        const stats = await res.json();
        
        animateValue("stat-patients", 0, stats.total_patients, 500);
        animateValue("stat-scans", 0, stats.total_scans, 500);
        animateValue("stat-tumors", 0, stats.tumor_detected_count, 500);
        animateValue("stat-clear", 0, stats.no_tumor_count, 500);
        
        renderChart(stats.tumor_type_breakdown);
        renderRecentScans(stats.recent_scans);
    } catch (err) {
        showAlert("Failed to load dashboard data", "error");
    }
}

function animateValue(id, start, end, duration) {
    const el = document.getElementById(id);
    const range = end - start;
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const value = Math.floor(range * progress + start);
        el.textContent = value;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

function renderChart(breakdown) {
    const ctx = document.getElementById("tumorChart");
    if (!ctx) return;
    
    const data = {
        labels: ["Glioma", "Meningioma", "Pituitary", "No Tumor"],
        datasets: [{
            data: [
                breakdown["Glioma"] || 0,
                breakdown["Meningioma"] || 0,
                breakdown["Pituitary"] || 0,
                breakdown["No Tumor"] || 0
            ],
            backgroundColor: ["#DC2626", "#D97706", "#7C3AED", "#059669"],
            borderWidth: 0
        }]
    };
    
    if (tumorChart) {
        tumorChart.destroy();
    }
    
    tumorChart = new Chart(ctx, {
        type: "doughnut",
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: { color: "#94A3B8", padding: 16 }
                }
            },
            cutout: "65%"
        }
    });
}

function renderRecentScans(scans) {
    const tbody = document.getElementById("recent-scans-body");
    if (!tbody) return;
    
    if (!scans || scans.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No scans yet</td></tr>';
        return;
    }
    
    tbody.innerHTML = scans.map(scan => `
        <tr>
            <td>${scan.patient_name || "Unknown"}</td>
            <td><span class="badge tag-${scan.tumor_type.toLowerCase().replace(" ", "-")}">${scan.tumor_type}</span></td>
            <td>${scan.confidence_score}%</td>
            <td>${formatDate(scan.created_at)}</td>
            <td><a href="/scans/${scan.id}" class="btn btn-outline btn-sm">View</a></td>
        </tr>
    `).join("");
}

document.addEventListener("DOMContentLoaded", loadStats);
