document.addEventListener('DOMContentLoaded', function() {
    setupPagination('inflow', 5);
    setupPagination('outflow', 5);
});
document.getElementById('amount').addEventListener('input', function() {
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
function openUpdateForm(transactionId) {
    // Pre-fill form if needed or fetch data via AJAX
    document.getElementById('update-id').value = transactionId;
    document.getElementById('updateForm').classList.remove('hidden');
}


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

function submitUpdate() {
    var amountInput = document.getElementById('amount').value;
    if (!amountInput.match(/^\d*\.?\d{0,2}$/) || amountInput === "") {
        document.getElementById('amount-error').textContent = 'Please correct errors before submitting.';
        return;  // Stop the function if there are errors
    }
    // Implement AJAX to submit form data
    closeUpdateForm();
    alert('Update Submitted!'); // Placeholder for actual implementation
}