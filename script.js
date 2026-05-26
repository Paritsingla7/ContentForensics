// Wait for the DOM to be fully loaded before running the script
document.addEventListener("DOMContentLoaded", () => {
    // Get references to all the HTML elements we'll need to update
    const loadingContainer = document.getElementById("loading-container");
    const errorContainer = document.getElementById("error-container");
    const errorMessage = document.getElementById("error-message");
    const resultsContainer = document.getElementById("results-container");

    const reportUrlTitle = document.getElementById("report-url-title");
    const reportUrlLink = document.getElementById("report-url-link");

    const contentCard = document.getElementById("content-card");
    const entitiesCard = document.getElementById("entities-card");
    const linksCard = document.getElementById("links-card");
    const spamCard = document.getElementById("spam-card");

    // --- Main function to fetch and display the report ---
    async function loadReport() {
        try {
            // Try to fetch the report.json file
            // We add a cache-busting query to ensure we always get the latest file
            const response = await fetch(`report.json?v=${new Date().getTime()}`);

            if (!response.ok) {
                throw new Error(`Failed to load report.json. Server responded with status: ${response.status}`);
            }

            const report = await response.json();

            // Hide loading message
            loadingContainer.classList.add("hidden");

            // Check if the Python script reported an error
            if (report.error) {
                throw new Error(report.error);
            }

            // If no errors, display the results
            displayReport(report);

        } catch (error) {
            // If anything goes wrong, show the error message
            console.error("Error loading report:", error);
            loadingContainer.classList.add("hidden");
            errorMessage.textContent = error.message;
            errorContainer.classList.remove("hidden");
        }
    }

    // --- Function to populate all the cards with data ---
    function displayReport(report) {
        // Set the main title and URL link
        reportUrlTitle.textContent = "Website Analysis Report";
        reportUrlLink.href = report.url;
        reportUrlLink.textContent = report.url;

        // Render each card
        renderContentCard(report.sentiment);
        renderEntitiesCard(report.entities);
        renderLinksCard(report.links);
        renderSpamCard(report.spam, report.genericAnchors); // Pass both spam object and anchor count

        // Show the main results container
        resultsContainer.classList.remove("hidden");
    }

    // --- Helper functions to get icons and colors ---

    // Returns SVG icon paths for card titles
    function getIcon(name) {
        const icons = {
            content: `<svg class="card-title-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>`,
            entities: `<svg class="card-title-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>`,
            links: `<svg class="card-title-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.101 1.101"></path></svg>`,
            spam: `<svg class="card-title-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`,
            success: `<svg class="status-badge-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`,
            warning: `<svg class="status-badge-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>`,
            warningItem: `<svg class="warning-item-icon" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 3.01-1.742 3.01H4.42c-1.53 0-2.493-1.676-1.743-3.01l5.58-9.92zM10 13a1 1 0 100-2 1 1 0 000 2zm-1-4a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z" clip-rule="evenodd"></path></svg>`
        };
        return icons[name] || '';
    }

    // Returns Tailwind CSS classes for entity labels
    function getLabelColorClass(type) {
        const colors = {
            "ORG": "entity-label-ORG",
            "PERSON": "entity-label-PERSON",
            "GPE": "entity-label-GPE",
            "UNKNOWN": "entity-label-UNKNOWN"
        };
        return colors[type] || colors["UNKNOWN"];
    }

    // --- Card Rendering Functions ---

    function renderContentCard(sentiment) {
        contentCard.innerHTML = `
            <div class="p-5">
                <h3 class="card-title">${getIcon('content')} Content Analysis</h3>
                <div class="space-y-3">
                    <div class="card-item">
                        <span class="card-item-label">Overall Sentiment</span>
                        <span class="card-item-value">${sentiment.Sentiment || 'N/A'}</span>
                    </div>
                    <div class="card-item">
                        <span class="card-item-label">Subjectivity</span>
                        <span class="card-item-value">${sentiment.Subjectivity || 'N/A'}</span>
                    </div>
                </div>
            </div>
        `;
    }

    function renderEntitiesCard(entities) {
        let entitiesHtml = '<p class="text-gray-400 text-sm">No prominent entities found.</p>';

        if (entities && entities.length > 0) {
            entitiesHtml = entities.map(entity => `
                <li class="entity-item">
                    <span class="entity-name">${entity.name} (Count: ${entity.count})</span>
                    <span class="entity-label ${getLabelColorClass(entity.type)}">${entity.type}</span>
                </li>
            `).join('');
            entitiesHtml = `<ul class="entity-list">${entitiesHtml}</ul>`;
        }

        entitiesCard.innerHTML = `
            <div class="p-5">
                <h3 class="card-title">${getIcon('entities')} Named Entities</h3>
                ${entitiesHtml}
            </div>
        `;
    }

    function renderLinksCard(links) {
        linksCard.innerHTML = `
            <div class="p-5">
                <h3 class="card-title">${getIcon('links')} Link Analysis</h3>
                <div class="space-y-3">
                    <div class="card-item">
                        <span class="card-item-label">Internal Links</span>
                        <span class="card-item-value">${links.internal !== undefined ? links.internal : 'N/A'}</span>
                    </div>
                    <div class="card-item">
                        <span class="card-item-label">External Links</span>
                        <span class="card-item-value">${links.external !== undefined ? links.external : 'N/A'}</span>
                    </div>
                </div>
            </div>
        `;
    }

    // This function handles the complex logic for the spam/warning card
    function renderSpamCard(spamObject, genericAnchorCount) {
        let warnings = [];

        // Check for spam warnings from the spamObject
        if (spamObject) {
            if (spamObject.keywordStuffing) {
                warnings.push(`<strong>Keyword Stuffing:</strong> ${spamObject.keywordStuffing}`);
            }
            if (spamObject.hiddenText) {
                // Build a detailed list of all hidden text instances
                let hiddenTextHtml = `<strong>Hidden Text:</strong> Found ${spamObject.hiddenText.count} instance(s):<ul class="ml-4 mt-2 space-y-1">`;
                spamObject.hiddenText.instances.forEach((instance, index) => {
                    hiddenTextHtml += `<li class="text-sm text-gray-300">[${index + 1}] ${instance}</li>`;
                });
                hiddenTextHtml += `</ul>`;
                warnings.push(hiddenTextHtml);
            }
        }

        // Check for generic anchor text warnings
        if (genericAnchorCount > 0) {
            warnings.push(`<strong>Generic Anchor Text:</strong> Found ${genericAnchorCount} generic link(s) (e.g., "click here").`);
        }

        let cardContent;
        if (warnings.length > 0) {
            // We have warnings, build the warning list
            cardContent = `
                <span class="status-badge status-badge-warning">
                    ${getIcon('warning')}
                    Warnings Found
                </span>
                <ul class="warning-list mt-4 space-y-2">
                    ${warnings.map(warning => `
                        <li class="warning-item">
                            ${getIcon('warningItem')}
                            <span class="warning-text">${warning}</span>
                        </li>
                    `).join('')}
                </ul>
            `;
        } else {
            // No warnings, show the "all clear" message
            cardContent = `
                <span class="status-badge status-badge-success">
                    ${getIcon('success')}
                    All Clear
                </span>
                <p class="text-gray-300 mt-4 text-sm">
                    No obvious spamdexing techniques or SEO issues were detected.
                </p>
            `;
        }

        spamCard.innerHTML = `
            <div class="p-5">
                <h3 class="card-title">${getIcon('spam')} Spamdexing Report</h3>
                ${cardContent}
            </div>
        `;
    }

    // --- Start the process ---
    loadReport();
});

