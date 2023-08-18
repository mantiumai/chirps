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

function updateHiddenInput(container) {
    const pairs = {};
    const keyValuePairs = container.querySelectorAll('div.form-inline');

    keyValuePairs.forEach(pair => {
        const keyInput = pair.querySelector('input:first-child');
        const valueInput = pair.querySelector('input:nth-child(2)');
        pairs[keyInput.value] = valueInput.value;
    });

    const hiddenInput = container.parentElement.querySelector('input[type="hidden"]');
    hiddenInput.value = JSON.stringify(pairs);
}
