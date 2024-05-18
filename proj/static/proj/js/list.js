document.addEventListener('DOMContentLoaded', function() {
    setupPagination('inflow', 5);
    setupPagination('outflow', 5);

    const amountInput = document.getElementById('amount');
    if (amountInput) {
        amountInput.addEventListener('input', function() {
            // This regular expression allows digits and a single decimal point followed by up to two digits
            this.value = this.value.replace(/[^0-9\.]/g, '')  // Remove any character that is not a number or decimal point
                                   .replace(/(\..*)\./g, '$1')  // Remove any additional decimal points
                                   .replace(/(\.\d{2})./g, '$1');  // Limit to two digits after the decimal point

            // Display error message if the input is still invalid
            if (!this.value.match(/^\d*\.?\d{0,2}$/)) {
                document.getElementById('amount-error').textContent = 'Please enter a valid amount (numbers only, max two decimals).';
            } else {
                document.getElementById('amount-error').textContent = '';  // Clear error message
            }
        });
    }
});

function setupPagination(tableId, rowsPerPage) {
    let table = document.getElementById(`${tableId}-table`);
    let tbody = table.getElementsByTagName('tbody')[0];
    let rows = Array.from(tbody.getElementsByTagName('tr'));
    let currentPage = 1;
    let pageCount = Math.ceil(rows.length / rowsPerPage);

    window[`paginate${tableId}`] = function(direction) {
        let errorDiv = document.getElementById(`${tableId}-error`);
        if (direction === 'next') {
            if (currentPage < pageCount) {
                currentPage++;
            } else {
                errorDiv.textContent = 'You are at the last page.';
                return;
            }
        } else if (direction === 'prev') {
            if (currentPage > 1) {
                currentPage--;
            } else {
                errorDiv.textContent = 'You are at the first page.';
                return;
            }
        }
        renderPage(currentPage);
        errorDiv.textContent = ''; // Clear any error message
    };

    function renderPage(page) {
        let start = (page - 1) * rowsPerPage;
        let end = start + rowsPerPage;
        tbody.innerHTML = ''; // Clear existing table rows
        rows.slice(start, end).forEach(row => tbody.appendChild(row));
    }

    renderPage(currentPage); // Initial page render
}

function closeUpdateForm() {
    document.getElementById('updateForm').classList.add('hidden');
}

function openUpdateForm(transactionId) {
    // Pre-fill form if needed or fetch data via AJAX
    document.getElementById('update-id').value = transactionId;
    document.getElementById('updateForm').classList.remove('hidden');

    const row = document.getElementById(`transaction-${transactionId}`);
    const date = row.querySelector(`#date-${transactionId}`).textContent.trim();
    const amount = row.querySelector(`#amount-${transactionId}`).textContent.trim().replace(currency_symbol, '');
    const description = row.querySelector(`#description-${transactionId}`).textContent.trim();

    document.getElementById('date').value = date;
    document.getElementById('amount').value = amount;
    document.getElementById('description').value = description;
}

function submitUpdate() {
    const form = document.getElementById('update-transaction-form');
    const formData = new FormData(form);

    fetch("{% url 'update_transaction' %}", {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const transaction = data.transaction;
            document.getElementById(`date-${transaction.id}`).textContent = transaction.date;
            document.getElementById(`amount-${transaction.id}`).textContent = `${currency_symbol}${transaction.amount}`;
            document.getElementById(`description-${transaction.id}`).textContent = transaction.description || '';

            closeUpdateForm();
        } else {
            console.error('Error updating transaction:', data.errors);
        }
    })
    .catch(error => {
        console.error('Error updating transaction:', error);
    });
}
