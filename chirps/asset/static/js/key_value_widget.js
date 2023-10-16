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

function addKeyValuePair(container, key = '', value = '', parentPair = null) {
    if (!container) {
        console.error('Container not found');
        return;
    }
    const keyInput = document.createElement('input');
    keyInput.type = 'text';
    keyInput.placeholder = 'Key';
    keyInput.value = key;
    keyInput.className = 'form-control mr-2 key-input';

    const valueInput = document.createElement('input');
    valueInput.type = 'text';
    valueInput.placeholder = 'Value';
    valueInput.value = value;
    valueInput.className = 'form-control mr-2 value-input';

    const addButton = document.createElement('button');
    addButton.type = 'button';
    addButton.textContent = 'Add Nested Key-Value Pair';
    addButton.className = 'btn btn-secondary add-nested-key-value-pair';

    const removeButton = document.createElement('button');
    removeButton.type = 'button';
    removeButton.textContent = 'Remove';
    removeButton.className = 'btn btn-danger remove-key-value-pair ml-2';

    const pair = document.createElement('div');
    pair.className = 'form-inline mb-2 key-value-input';
    pair.appendChild(keyInput);
    pair.appendChild(valueInput);
    pair.appendChild(addButton);
    pair.appendChild(removeButton);

    if (parentPair) {
        parentPair.appendChild(pair);
        pair.dataset.parentKey = parentPair.querySelector('.key-input').value;
        pair.classList.add('nested-key-value');

        // Add margin-left to visually show the nesting
        pair.style.marginLeft = '20px';

        // Remove the value field of the parent pair
        const parentValueInput = parentPair.querySelector('.value-input');
        parentPair.removeChild(parentValueInput);
    } else {
        container.appendChild(pair);
    }

    keyInput.addEventListener('input', () => {
        updateHiddenInput(container);
    });

    valueInput.addEventListener('input', () => {
        updateHiddenInput(container);
    });

    addButton.addEventListener('click', () => {
        addKeyValuePair(container, '', '', pair);
    });

    removeButton.addEventListener('click', () => {
        (parentPair || container).removeChild(pair);
        updateHiddenInput(container);
    });
}

function updateHiddenInput(container) {
    function processKeyValuePairs(parentNode, parentKey = '') {
        const keyValuePairs = parentNode.querySelectorAll(
            parentKey ? `.key-value-input[data-parent-key="${parentKey}"]` : '.key-value-input:not([data-parent-key])'
        );

        const pairs = {};

        keyValuePairs.forEach(pair => {
            const keyInput = pair.querySelector('.key-input');
            const valueInput = pair.querySelector('.value-input');

            if (keyInput.value && valueInput.value) {
                pairs[keyInput.value] = valueInput.value;
                const nestedPairs = processKeyValuePairs(pair, keyInput.value);

                if (Object.keys(nestedPairs).length > 0) {
                    pairs[keyInput.value] = nestedPairs;
                }
            }
        });

        return pairs;
    }

    const pairs = processKeyValuePairs(container);

    const hiddenInput = container.parentElement.querySelector('input[type="hidden"]');
    hiddenInput.value = JSON.stringify(pairs);
}
