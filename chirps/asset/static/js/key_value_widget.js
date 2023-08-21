document.addEventListener('DOMContentLoaded', () => {
    const keyValueContainers = document.querySelectorAll('.key-value-container');

    keyValueContainers.forEach((container, index) => {
        const addButton = container.nextElementSibling;

        // Add a data attribute to the button to prevent multiple event listeners
        if (!addButton.hasAttribute('data-initialized')) {
            addButton.setAttribute('data-initialized', 'true');

            addButton.addEventListener('click', () => {
                addKeyValuePair(container);
            });

            // Initialize with existing pairs from the hidden input value
            const hiddenInput = container.parentElement.querySelector('input[type="hidden"]');
            if (hiddenInput.value) {
                const pairs = JSON.parse(hiddenInput.value);
                for (const key in pairs) {
                    addKeyValuePair(container, key, pairs[key]);
                }
            }
        }
    });
});


function addKeyValuePair(container, key = '', value = '') {
    if (!container) {
        console.error('Container not found');
        return;
    }
    const keyInput = document.createElement('input');
    keyInput.type = 'text';
    keyInput.placeholder = 'Key';
    keyInput.value = key;
    keyInput.className = 'form-control mr-2';

    const valueInput = document.createElement('input');
    valueInput.type = 'text';
    valueInput.placeholder = 'Value';
    valueInput.value = value;
    valueInput.className = 'form-control mr-2';

    // Make the value %query% uneditable
    if (value === '%query%') {
        valueInput.setAttribute('disabled', 'disabled');
    }

    const removeButton = document.createElement('button');
    removeButton.type = 'button';
    removeButton.textContent = 'Remove';
    removeButton.className = 'btn btn-danger';

    const pair = document.createElement('div');
    pair.className = 'form-inline mb-2';
    pair.appendChild(keyInput);
    pair.appendChild(valueInput);
    pair.appendChild(removeButton);
    container.appendChild(pair);

    // Add tooltip icon and message for the 'body' field with key 'data'
    if (container.id.includes('body') && value === '%query%') {
        const tooltipIcon = document.createElement('i');
        tooltipIcon.className = 'fas fa-info-circle ml-2';
        tooltipIcon.setAttribute('data-toggle', 'tooltip');
        tooltipIcon.setAttribute('title', 'Chirps sends a POST request to the API endpoint.\n\nThe value %query% will be replaced by the request text.\n\nPlease update the key to match what is expected in the request.');

        pair.appendChild(tooltipIcon);

        // Initialize the tooltip
        $(tooltipIcon).tooltip();
    }

    removeButton.addEventListener('click', () => {
        container.removeChild(pair);
        updateHiddenInput(container);
    });

    keyInput.addEventListener('input', () => {
        updateHiddenInput(container);
    });

    valueInput.addEventListener('input', () => {
        updateHiddenInput(container);
    });
}
