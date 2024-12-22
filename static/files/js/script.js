const form = document.getElementById('generateForm');
const responseContainer = document.getElementById('response-container');
const loadingSpinner = document.getElementById('loading-spinner');
const caseForm = document.getElementById('caseForm');

form.addEventListener('submit', async (event) => {
    event.preventDefault();

    loadingSpinner.classList.remove('hidden');
    responseContainer.classList.add('hidden');
    responseContainer.classList.remove('success');
    responseContainer.classList.remove('error');

    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => data[key] = value);

    try {
        const response = await fetch('/generate_cases', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        handleGenerateCasesResponse(response);
    } catch (error) {
        displayError({ error: error.message });
    } finally {
        loadingSpinner.classList.add('hidden');
        responseContainer.classList.remove('hidden');
    }
});

caseForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const answers = [];
    const caseElements = caseForm.querySelectorAll('.case-container');

    caseElements.forEach(caseElement => {
        const caseId = caseElement.querySelector('input[name="case_id"]').value;
        const selectedOption = caseElement.querySelector('input[type="radio"]:checked');

        if (selectedOption) {
            answers.push({
                "case_id": caseId,
                "option_id": selectedOption.value
            });
        } else {
            alert('Please select an option for each case.');
            event.preventDefault();
            return; // Prevent submission
        }
    });

    if (confirm('Are you sure you want to submit these answers?')) {
        submitAnswers(answers);
    }
});

async function submitAnswers(answers) {
    loadingSpinner.classList.remove('hidden');
    responseContainer.classList.add('hidden');
    responseContainer.classList.remove('success');
    responseContainer.classList.remove('error');

    try {
        const response = await fetch('/submit_answers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ answers: answers })
        });

        if (!response.ok) {
            displayError(await response.json());
        } else {
            const data = await response.json();
            displayResults(data);
            responseContainer.classList.add('success');
        }
    } catch (error) {
        displayError({ error: error.message });
    } finally {
        loadingSpinner.classList.add('hidden');
        responseContainer.classList.remove('hidden');
    }
}

function displayResults(data) {
    responseContainer.innerHTML = `
        <h2>Results</h2>
        <div class="result-summary">
            <p><strong>Your Score:</strong> ${data.total_score}</p>
            <p><strong>Max Possible Score:</strong> ${data.max_total_score}</p>
        </div>
        <div class="result-details">
    `;

    data.results.forEach(result => {
        responseContainer.innerHTML += `
            <div class="case-result">
                <p><strong>Case ID:</strong> ${result.case_id}</p>
                <p><strong>Your Score:</strong> ${result.score}</p>
                <p><strong>Max Score:</strong> ${result.max_score}</p>
            </div>
        `;
    });

    responseContainer.innerHTML += `</div>`;

    // Add New Game button
    const newGameButton = document.createElement('button');
    newGameButton.id = 'newGameButton';
    newGameButton.textContent = 'New Game';
    newGameButton.addEventListener('click', startNewGame);
    responseContainer.appendChild(newGameButton);
}


function displayCases(data) {
    caseForm.innerHTML = ''; // Clear previous cases
    if (data && data.data && data.data.length > 0) {
        data.data.forEach(optionData => {
            if (optionData && optionData.cases && optionData.cases.length > 0) {
                optionData.cases.forEach((caseItem, index) => {
                    const caseElement = document.createElement('div');
                    caseElement.classList.add('case-container');

                    const caseTitle = document.createElement('div');
                    caseTitle.classList.add('case-title');
                    caseTitle.innerText = caseItem.case;
                    caseElement.appendChild(caseTitle);

                    const hiddenInput = document.createElement('input');
                    hiddenInput.type = 'hidden';
                    hiddenInput.name = 'case_id';
                    hiddenInput.value = caseItem.case_id;
                    caseElement.appendChild(hiddenInput);

                    caseItem.options.forEach(option => {
                        const optionElement = document.createElement('div');
                        optionElement.classList.add('option');

                        const radioInput = document.createElement('input');
                        radioInput.type = 'radio';
                        radioInput.name = caseItem.case_id;
                        radioInput.value = option.option_id;
                        radioInput.id = `option_${option.option_id}`;

                        const label = document.createElement('label');
                        label.htmlFor = `option_${option.option_id}`;
                        label.innerText = `${option.number}. ${option.option}`;

                        optionElement.appendChild(radioInput);
                        optionElement.appendChild(label);
                        caseElement.appendChild(optionElement);
                    });

                    caseForm.appendChild(caseElement);
                });
            } else {
                console.error("Error: Invalid or empty case data received from server.");
            }
        });

        const submitButton = document.createElement('button');
        submitButton.type = 'submit';
        submitButton.classList.add('submit-button');
        submitButton.innerText = 'Submit Answers';
        caseForm.appendChild(submitButton);
    } else {
        displayError({ error: "Invalid or empty response from server" });
    }
}

function startNewGame() {
    // Clear previous game data
    caseForm.innerHTML = '';  // Clear the form
    responseContainer.innerHTML = ''; // Clear the results
    responseContainer.classList.remove('success');
    responseContainer.classList.remove('error');

    // Reset the form and enable input
    form.reset();
    form.querySelector('#language').disabled = false;
    form.querySelector('#sex').disabled = false;
    form.querySelector('#age').disabled = false;
    form.querySelector('button[type="submit"]').disabled = false;

    // Reset the visibility
    loadingSpinner.classList.add('hidden');
    responseContainer.classList.add('hidden');

    location.reload();
}

async function handleGenerateCasesResponse(response) {
    if (!response.ok) {
        const errorData = await response.json();
        displayError(errorData);
    } else {
        const jsonData = await response.json();
        if (jsonData && jsonData.data && jsonData.data.length > 0) {
            displayCases(jsonData);
            responseContainer.classList.add('success');
        } else {
            displayError({ error: "Invalid or empty response from server" });
        }
    }
}

function displayError(errorData) {
    responseContainer.classList.add('error');
    responseContainer.innerHTML = `
        <p><strong>Error:</strong> ${errorData.error}</p>
        <button id="tryAgainButton">Try Again</button>
    `;

    const tryAgainButton = document.getElementById('tryAgainButton');
    tryAgainButton.addEventListener('click', () => {
        responseContainer.innerHTML = '';
        responseContainer.classList.remove('error');
        form.querySelector('#language').disabled = false;
        form.querySelector('#sex').disabled = false;
        form.querySelector('#age').disabled = false;
        form.querySelector('button[type="submit"]').disabled = false;
        responseContainer.classList.add('hidden');
        form.submit();
    });
}
