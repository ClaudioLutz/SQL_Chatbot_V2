document.addEventListener('DOMContentLoaded', () => {
    const submitBtn = document.getElementById('submit-btn');
    const questionInput = document.getElementById('question-input');
    const sqlQueryOutput = document.getElementById('sql-query-output');
    const resultsOutput = document.getElementById('results-output');

    submitBtn.addEventListener('click', async () => {
        const question = questionInput.value;
        if (!question) {
            alert('Please enter a question.');
            return;
        }

        sqlQueryOutput.textContent = 'Generating SQL...';
        resultsOutput.innerHTML = '';

        try {
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: question }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            sqlQueryOutput.textContent = data.sql_query;

            if (data.results.error) {
                resultsOutput.innerHTML = `<p style="color: red;">Error: ${data.results.error}</p>`;
            } else if (data.results.rows.length === 0) {
                resultsOutput.innerHTML = '<p>Query returned no results.</p>';
            } else {
                resultsOutput.innerHTML = createTable(data.results.columns, data.results.rows);
            }
        } catch (error) {
            sqlQueryOutput.textContent = 'An error occurred.';
            resultsOutput.innerHTML = `<p style="color: red;">${error.message}</p>`;
            console.error('Error:', error);
        }
    });

    function createTable(columns, rows) {
        let table = '<table><thead><tr>';
        columns.forEach(col => {
            table += `<th>${col}</th>`;
        });
        table += '</tr></thead><tbody>';
        rows.forEach(row => {
            table += '<tr>';
            columns.forEach(col => {
                table += `<td>${row[col]}</td>`;
            });
            table += '</tr>';
        });
        table += '</tbody></table>';
        return table;
    }
});
