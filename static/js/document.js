/**
 * Document Upload System - Frontend JavaScript
 * Handles document upload and UI interactions
 */

document.addEventListener("DOMContentLoaded", function () {
    const uploadForm = document.getElementById("uploadForm");

    // Existing upload form handler (if present)
    if (uploadForm) {
        uploadForm.addEventListener("submit", handleFormSubmit);
    }

    // Setup applicant type toggles for conditional document sections
    const applicantSelect = document.getElementById("applicantType");
    if (applicantSelect) {
        applicantSelect.addEventListener("change", handleApplicantTypeChange);
        // run once to set initial visibility
        handleApplicantTypeChange();
    }
});

/**
 * Show/hide sections based on selected applicant type
 */
function handleApplicantTypeChange() {
    const applicantSelect = document.getElementById("applicantType");
    const value = applicantSelect ? applicantSelect.value : "";

    // All conditional sections
    const salaried = document.getElementById("salariedDocs");
    const business = document.getElementById("businessDocs");
    const farmer = document.getElementById("farmerDocs");
    const commonCredit = document.getElementById("commonCreditScore");
    // Toggle visible class for smooth animations
    if (salaried) salaried.classList.remove("visible");
    if (business) business.classList.remove("visible");
    if (farmer) farmer.classList.remove("visible");
    if (commonCredit) commonCredit.classList.remove("visible");

    if (value === "SALARIED") {
        if (salaried) salaried.classList.add("visible");
    } else if (value === "BUSINESS") {
        if (business) business.classList.add("visible");
    } else if (value === "FARMER") {
        if (farmer) farmer.classList.add("visible");
    }

    // Show common credit score for non-farmer applicants
    if (commonCredit) {
        if (value === "FARMER") {
            commonCredit.classList.remove("visible");
        } else {
            commonCredit.classList.add("visible");
        }
    }
}

/**
 * Collect visible file inputs and upload them in one request.
 */
async function submitDocuments() {
    const uploadStatus = document.getElementById("uploadStatus");
    const statusMessage = document.getElementById("statusMessage");

    // Collect visible file inputs
    const allFileInputs = Array.from(document.querySelectorAll("input[type=\"file\"]"));
    const visibleInputs = allFileInputs.filter((input) => {
        const conditional = input.closest(".conditional");
        if (!conditional) return true; // common docs
        return conditional.classList.contains("visible");
    });

    // Validate required fields (data-required="true")
    const missingRequired = visibleInputs.filter((input) => input.dataset.required === "true" && (!input.files || input.files.length === 0));
    if (missingRequired.length > 0) {
        showError(statusMessage, uploadStatus, "Please provide required documents (PAN Card is mandatory).");
        return;
    }

    // Business rules validation per applicant type
    const applicantType = document.getElementById("applicantType")?.value || "";

    function isPresentCategory(cat) {
        return visibleInputs.some(i => (i.dataset.category || "").toUpperCase() === cat && i.files && i.files.length > 0);
    }

    function getNumber(id) {
        const el = document.getElementById(id);
        if (!el) return null;
        const v = el.value;
        return v === "" ? null : Number(v);
    }

    // Require credit_score for SALARIED and BUSINESS
    if (applicantType === "SALARIED" || applicantType === "BUSINESS") {
        const cs = getNumber("credit_score") || getNumber("credit_score_farmer");
        if (!cs || Number.isNaN(cs) || cs <= 0) {
            showError(statusMessage, uploadStatus, "Credit score is required for Salaried and Business applicants.");
            return;
        }
    }

    if (applicantType === "SALARIED") {
        // require salary slip and net_monthly_salary
        if (!isPresentCategory("SALARY_SLIP")) {
            showError(statusMessage, uploadStatus, "Salary slip is required for salaried applicants.");
            return;
        }
        const netSal = getNumber("net_monthly_salary");
        if (!netSal || netSal <= 0) {
            showError(statusMessage, uploadStatus, "Net monthly salary must be provided and greater than zero.");
            return;
        }
    }

    if (applicantType === "BUSINESS") {
        if (!isPresentCategory("BUSINESS_REGISTRATION") || !isPresentCategory("FINANCIAL_STATEMENT")) {
            showError(statusMessage, uploadStatus, "Business registration and financial statements are required for business applicants.");
            return;
        }
        const avgProfit = getNumber("avg_net_profit_3y");
        const bizAge = getNumber("business_age_years");
        if (!avgProfit || avgProfit <= 0) {
            showError(statusMessage, uploadStatus, "Average net profit (3y) must be provided for business applicants.");
            return;
        }
        if (!bizAge || bizAge <= 0) {
            showError(statusMessage, uploadStatus, "Business age (years) must be provided and greater than zero.");
            return;
        }
    }

    if (applicantType === "FARMER") {
        if (!isPresentCategory("KISAN_CREDIT_CARD_STMT")) {
            showError(statusMessage, uploadStatus, "KCC statement is required for farmer applicants.");
            return;
        }
        const annual = getNumber("annual_agri_income");
        if (!annual || annual <= 0) {
            showError(statusMessage, uploadStatus, "Annual agricultural income must be provided and greater than zero for farmer applicants.");
            return;
        }
    }

    // Ensure at least one file is selected
    const filesToUpload = visibleInputs.filter((i) => i.files && i.files.length > 0);
    if (filesToUpload.length === 0) {
        showError(statusMessage, uploadStatus, "No files selected to upload.");
        return;
    }

    const formData = new FormData();
    filesToUpload.forEach((input) => {
        const file = input.files[0];
        const category = input.dataset.category || "";
        formData.append("files", file, file.name);
        formData.append("categories", category);
    });

    // Append metadata fields
    formData.append("applicant_type", applicantType);
    ["loan_amount", "property_value", "credit_score", "net_monthly_salary", "proposed_emi", "existing_emi", "avg_net_profit_3y", "business_age_years", "annual_agri_income", "proposed_emi_business", "credit_score_farmer", "kcc_overdue"].forEach((id) => {
        const el = document.getElementById(id);
        if (el) formData.append(id, el.value || "");
    });

    try {
        // Show loading
        uploadStatus.style.display = "block";
        statusMessage.className = "message";
        statusMessage.textContent = "Uploading...";

        const resp = await fetch("/api/upload-multiple", {
            method: "POST",
            body: formData,
        });

        const data = await resp.json();
        if (resp.ok && data.success) {
            showSuccess(statusMessage, uploadStatus, "All files uploaded successfully.");
            // Optionally redirect or clear inputs
            setTimeout(() => window.location.href = "/documents", 1500);
        } else {
            // Show details of failures if present
            const msg = data.message || (data.results ? JSON.stringify(data.results) : "Upload failed");
            showError(statusMessage, uploadStatus, msg);
        }
    } catch (err) {
        console.error("Upload-multiple error:", err);
        showError(statusMessage, uploadStatus, "An error occurred during upload");
    }
}

/**
 * Handle form submission for document upload
 * @param {Event} event - Form submission event
 */
async function handleFormSubmit(event) {
    event.preventDefault();

    const uploadForm = document.getElementById("uploadForm");
    const uploadStatus = document.getElementById("uploadStatus");
    const statusMessage = document.getElementById("statusMessage");
    const fileInput = document.getElementById("file");
    const categoryInput = document.getElementById("category");

    // Validate inputs
    if (!fileInput.files.length) {
        showError(statusMessage, uploadStatus, "Please select a file");
        return;
    }

    if (!categoryInput.value) {
        showError(statusMessage, uploadStatus, "Please select a category");
        return;
    }

    // Prepare form data
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    formData.append("category", categoryInput.value);

    try {
        // Show loading state
        uploadStatus.style.display = "block";
        statusMessage.className = "message";
        statusMessage.textContent = "Uploading...";
        statusMessage.style.backgroundColor = "#d1ecf1";
        statusMessage.style.color = "#0c5460";

        // Send upload request
        const response = await fetch("/api/upload", {
            method: "POST",
            body: formData,
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showSuccess(
                statusMessage,
                uploadStatus,
                data.message || "File uploaded successfully!"
            );
            // Reset form
            uploadForm.reset();
            // Reload documents after 2 seconds
            setTimeout(() => {
                location.href = "/documents";
            }, 2000);
        } else {
            showError(
                statusMessage,
                uploadStatus,
                data.message || "Upload failed"
            );
        }
    } catch (error) {
        console.error("Upload error:", error);
        showError(statusMessage, uploadStatus, "An error occurred during upload");
    }
}

/**
 * Display success message
 * @param {HTMLElement} messageEl - Message element
 * @param {HTMLElement} statusEl - Status container element
 * @param {string} message - Success message text
 */
function showSuccess(messageEl, statusEl, message) {
    statusEl.style.display = "block";
    messageEl.className = "message success";
    messageEl.textContent = "✓ " + message;
}

/**
 * Display error message
 * @param {HTMLElement} messageEl - Message element
 * @param {HTMLElement} statusEl - Status container element
 * @param {string} message - Error message text
 */
function showError(messageEl, statusEl, message) {
    statusEl.style.display = "block";
    messageEl.className = "message error";
    messageEl.textContent = "✗ " + message;
}

/**
 * Load and display documents
 */
async function loadDocuments() {
    try {
        const response = await fetch("/api/documents");
        const data = await response.json();

        if (data.success) {
            displayDocuments(data.documents);
        }
    } catch (error) {
        console.error("Error loading documents:", error);
    }
}

/**
 * Display documents in UI
 * @param {Object} documents - Documents object organized by category
 */
function displayDocuments(documents) {
    const container = document.querySelector(".recent-uploads");

    if (!container) {
        return;
    }

    let html = "<h3>Your Uploaded Documents</h3>";
    let hasDocuments = false;

    for (const [category, files] of Object.entries(documents)) {
        if (files.length > 0) {
            hasDocuments = true;
            html += `
                <div class="category-group">
                    <h4>${category}</h4>
                    <ul>
                        ${files.map((file) => `<li>${file}</li>`).join("")}
                    </ul>
                </div>
            `;
        }
    }

    if (!hasDocuments) {
        html += "<p>No documents uploaded yet.</p>";
    }

    container.innerHTML = html;
}
