let patients = [];

async function loadPatients() {
    try {
        const res = await apiFetch("/api/patients");
        if (!res.ok) throw new Error("Failed to load patients");
        patients = await res.json();
        renderPatients(patients);
        loadPatientDropdown();
    } catch (err) {
        showAlert("Failed to load patients", "error");
    }
}

function renderPatients(data) {
    const tbody = document.getElementById("patients-body");
    if (!tbody) return;
    
    if (!data || data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No patients yet</td></tr>';
        return;
    }
    
    tbody.innerHTML = data.map(patient => {
        const age = calculateAge(patient.date_of_birth);
        const lastScan = patient.scans_count > 0 ? "Scans: " + patient.scans_count : "No scans";
        return `
            <tr>
                <td><a href="/patients/${patient.id}">${patient.name}</a></td>
                <td>${age}</td>
                <td>${patient.gender}</td>
                <td>${patient.scans_count}</td>
                <td>${lastScan}</td>
                <td>
                    <a href="/patients/${patient.id}" class="btn btn-outline btn-sm">View</a>
                    <button class="btn btn-danger btn-sm" onclick="deletePatient('${patient.id}')">Delete</button>
                </td>
            </tr>
        `;
    }).join("");
}

function calculateAge(dob) {
    const birth = new Date(dob);
    const today = new Date();
    let age = today.getFullYear() - birth.getFullYear();
    const m = today.getMonth() - birth.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) {
        age--;
    }
    return age;
}

async function loadPatientDropdown() {
    try {
        const res = await apiFetch("/api/patients");
        const data = await res.json();
        const select = document.getElementById("patient-select");
        if (!select) return;
        
        select.innerHTML = '<option value="">-- No patient --</option>' +
            data.map(p => `<option value="${p.id}">${p.name}</option>`).join("");
        
        const params = new URLSearchParams(window.location.search);
        const patientId = params.get("patient_id");
        if (patientId) {
            select.value = patientId;
        }
    } catch (err) {}
}

document.getElementById("patient-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    btn.classList.add("loading");
    
    try {
        const res = await apiFetch("/api/patients", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name: document.getElementById("patient-name").value,
                date_of_birth: document.getElementById("patient-dob").value,
                gender: document.getElementById("patient-gender").value,
                contact_email: document.getElementById("patient-email").value || null,
                notes: document.getElementById("patient-notes").value || null
            })
        });
        
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Failed to create patient");
        }
        
        showAlert("Patient created successfully", "success");
        closeModal("patient-modal");
        e.target.reset();
        loadPatients();
    } catch (err) {
        showAlert(err.message, "error");
    } finally {
        btn.classList.remove("loading");
    }
});

document.getElementById("search-patients").addEventListener("input", (e) => {
    const query = e.target.value.toLowerCase();
    const filtered = patients.filter(p => 
        p.name.toLowerCase().includes(query) ||
        (p.contact_email && p.contact_email.toLowerCase().includes(query))
    );
    renderPatients(filtered);
});

async function deletePatient(id) {
    if (!confirm("Are you sure you want to delete this patient?")) return;
    
    try {
        const res = await apiFetch(`/api/patients/${id}`, { method: "DELETE" });
        if (!res.ok) throw new Error("Failed to delete patient");
        
        showAlert("Patient deleted", "success");
        loadPatients();
    } catch (err) {
        showAlert(err.message, "error");
    }
}

document.addEventListener("DOMContentLoaded", loadPatients);
