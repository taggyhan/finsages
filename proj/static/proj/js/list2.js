document.addEventListener('DOMContentLoaded', function() {
    setupPagination('inflow', 5);
    setupPagination('outflow', 5);

    const amountInput = document.getElementById('amount');
    if (amountInput) {
        amountInput.addEventListener('input', validateAmountInput);
    }

    const updateButton = document.querySelector('#update-transaction-form button[type="button"]');
    if (updateButton) {
        updateButton.addEventListener('click', handleUpdateTransaction);
    }
});

function validateAmountInput() {
    this.value = this.value.replace(/[^0-9\.]/g, '')  // Remove any character that is not a number or decimal point
                           .replace(/(\..*)\./g, '$1')  // Remove any additional decimal points
                           .replace(/(\.\d{2})./g, '$1');  // Limit to two digits after the decimal point

    const amountError = document.getElementById('amount-error');
    if (!this.value.match(/^\d*\.?\d{0,2}$/)) {
        amountError.textContent = 'Please enter a valid amount (numbers only, max two decimals).';
    } else {
        amountError.textContent = '';  // Clear error message
    }
}

function setupPagination(tableId, rowsPerPage) {
    const table = document.getElementById(`${tableId}-table`);
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    let currentPage = 1;
    const pageCount = Math.ceil(rows.length / rowsPerPage);

    window[`paginate${tableId}`] = function(direction) {
        const errorDiv = document.getElementById(`${tableId}-error`);
        if (direction === 'next' && currentPage < pageCount) {
            currentPage++;
        } else if (direction === 'prev' && currentPage > 1) {
            currentPage--;
        } else {
            errorDiv.textContent = `You are at the ${direction === 'next' ? 'last' : 'first'} page.`;
            return;
        }
        renderPage();
        errorDiv.textContent = ''; // Clear any error message
    };

    function renderPage() {
        const start = (currentPage - 1) * rowsPerPage;
        const end = start + rowsPerPage;
        tbody.innerHTML = ''; // Clear existing table rows
        rows.slice(start, end).forEach(row => tbody.appendChild(row));
    }

    renderPage(); // Initial page render
}

function closeUpdateForm() {
    document.getElementById('updateForm').classList.add('hidden');
}

function openUpdateForm(transactionId) {
    // Get the row element
    const row = document.getElementById(`transaction-${transactionId}`);
    
    // Extract date, amount, and description
    const date = row.querySelector(`td.date`).textContent.trim();
    const amount = row.querySelector(`td.amount`).textContent.trim().replace(currency_symbol, '');
    const description = row.querySelector(`td.description`).textContent.trim();

    // Populate the form fields
    document.getElementById('update-id').value = transactionId;
    document.getElementById('date').value = formatDateForInput(date);
    document.getElementById('amount').value = amount;
    document.getElementById('description').value = description;
    
    // Show the update form
    document.getElementById('updateForm').classList.remove('hidden');
}

function formatDateForInput(dateString) {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function formatDateForDisplay(dateString) {
    const date = new Date(dateString);
    const day = date.getDate();
    const month = date.toLocaleString('default', { month: 'long' });
    const year = date.getFullYear();
    return `${month} ${day}, ${year}`;
}

function handleDeleteTransaction() {
    const transactionId = document.getElementById('update-id').value;

    // Get CSRF token
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    // Send AJAX request to delete the transaction in the backend
    fetch(`../delete-transaction/${transactionId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken,
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove the transaction row from the table
            const row = document.getElementById(`transaction-${transactionId}`);
            row.remove();

            // Close the update form
            closeUpdateForm();

            // Show success popup
            showPopup('Transaction deleted successfully!');
        } else {
            console.error('Error deleting transaction:', data.error);
        }
    })
    .catch(error => {
        console.error('Error deleting transaction:', error);
    });
}

function handleUpdateTransaction() {
    const transactionId = document.getElementById('update-id').value;
    const dateInput = document.getElementById('date');
    const amount = document.getElementById('amount').value;
    const description = document.getElementById('description').value;

    // Validate date
    if (!dateInput.value) {
        alert('Date cannot be empty.');
        return;
    }
    const date = dateInput.value;

    // Get CSRF token
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    // Send AJAX request to update the transaction in the backend
    fetch('../update-transaction/', {
        method: 'POST',
        body: new URLSearchParams({
            'id': transactionId,
            'date': date,
            'amount': amount,
            'description': description,
            'csrfmiddlewaretoken': csrfToken
        }),
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the frontend with the new values
            const transaction = data.transaction;
            const row = document.getElementById(`transaction-${transaction.id}`);
            row.querySelector('td.date').textContent = formatDateForDisplay(transaction.date);
            row.querySelector('td.amount').textContent = `${currency_symbol}${transaction.amount}`;
            row.querySelector('td.description').textContent = transaction.description;

            // Close the update form
            closeUpdateForm();
            showPopup('Transaction updated successfully!');
        } else {
            console.error('Error updating transaction:', data.error);
        }
    })
    .catch(error => {
        console.error('Error updating transaction:', error);
    });
}

function showPopup(message) {
    const popup = document.createElement('div');
    popup.textContent = message;
    popup.className = 'fixed bottom-0 right-0 mb-4 mr-4 px-4 py-2 bg-green-500 text-white rounded';
    document.body.appendChild(popup);

    setTimeout(() => {
        popup.remove();
    }, 2000);
}