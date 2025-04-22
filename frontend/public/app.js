document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const fileName = document.getElementById('fileName');
    const processBtn = document.getElementById('processBtn');
    const statusMessage = document.getElementById('statusMessage');
    const progressBar = document.getElementById('progressBar');
    const resultsDiv = document.getElementById('results');
    const tableContainer = document.getElementById('tableContainer');
    const connectionStatus = document.getElementById('connectionStatus');
    
    let selectedFile = null;
    let taskId = null;
    
    // Socket.IO Connection
    const socket = io('http://localhost:5000', {
        path: '/socket.io',
        transports: ['websocket'],  // Force WebSocket first
        reconnection: true,
        reconnectionAttempts: Infinity,
        reconnectionDelay: 1000,
        timeout: 20000
      });
      
      // Add connection debugging:
      socket.on('connect_error', (err) => {
        console.error('Connection error:', err);
      });
      
      socket.on('connect_timeout', () => {
        console.error('Connection timeout');
      });
      
      socket.on('reconnect_attempt', (attempt) => {
        console.log(`Reconnect attempt #${attempt}`);
      });
    socket.on('connect', () => {
        connectionStatus.textContent = 'Connected';
        connectionStatus.className = 'connection-status connected';
    });

    socket.on('disconnect', () => {
        connectionStatus.textContent = 'Disconnected';
        connectionStatus.className = 'connection-status disconnected';
    });

    // File Selection Handler
    fileInput.addEventListener('change', (event) => {
        selectedFile = event.target.files[0];
        if (!selectedFile) return;
        
        // Validate file type
        const validTypes = [
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ];
        
        if (!validTypes.includes(selectedFile.type)) {
            alert('Please upload a valid Excel file (.xls, .xlsx)');
            fileInput.value = '';
            return;
        }
        
        fileName.textContent = selectedFile.name;
        processBtn.disabled = false;
    });

    // Process File Handler
    processBtn.addEventListener('click', async () => {
        if (!selectedFile) return;
        
        statusMessage.textContent = 'Uploading...';
        statusMessage.className = 'status processing';
        statusMessage.style.display = 'block';

        try {
            const formData = new FormData();
            formData.append('file', selectedFile);
            
            const response = await fetch('http://localhost:5000/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const error = await response.json();
                if (error.missing_columns) {
                    throw new Error(`Missing mandatory columns: ${error.missing_columns.join(', ')}`);
                }
                throw new Error(error.error || 'Upload failed');
            }
            
            const data = await response.json();
            taskId = data.task_id;
            console.log('Processing started with task ID:', taskId);
        } catch (error) {
            statusMessage.textContent = `Error: ${error.message}`;
            statusMessage.className = 'status error';
            console.error('Upload error:', error);
        }
    });

    function displayResults(data) {
        if (!data?.length) {
            tableContainer.innerHTML = '<p>No data available</p>';
            return;
        }
        
        const columns = Object.keys(data[0]);
        let html = `
            <table>
                <thead><tr>${columns.map(c => `<th>${c}</th>`).join('')}</tr></thead>
                <tbody>
                    ${data.map(row => 
                        `<tr>${columns.map(c => `<td>${row[c]}</td>`).join('')}</tr>`
                    ).join('')}
                </tbody>
            </table>
        `;
        
        tableContainer.innerHTML = html;
    }
});