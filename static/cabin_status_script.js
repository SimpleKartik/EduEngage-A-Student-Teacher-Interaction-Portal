document.addEventListener('DOMContentLoaded', function() {
    loadCabinStatus();
});

function loadCabinStatus() {
    fetch('/get_teacher_cabin_status')
        .then(response => response.json())
        .then(data => {
            updateCabinStatusTable(data);
        })
        .catch(error => console.error('Error:', error));
}

function updateCabinStatusTable(statusData) {
    const tableBody = document.querySelector('#cabin-status-table tbody');
    tableBody.innerHTML = '';
    
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    const timeSlots = ['8:30 AM', '10:05 AM', '11:40 AM', '1:15 PM', '2:50 PM', '4:25 PM', '6:00 PM'];
    
    days.forEach(day => {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${day}</td>`;
        
        timeSlots.forEach(timeSlot => {
            const status = statusData.find(s => s.day === day && s.time_slot === timeSlot);
            const currentStatus = status ? status.status : 'Available';
            
            row.innerHTML += `
                <td class="status-cell ${currentStatus}">
                    <select class="status-select" 
                            onchange="updateStatus('${day}', '${timeSlot}', this.value)"
                            data-day="${day}"
                            data-time-slot="${timeSlot}">
                        <option value="Available" ${currentStatus === 'Available' ? 'selected' : ''}>Available</option>
                        <option value="Busy" ${currentStatus === 'Busy' ? 'selected' : ''}>Busy</option>
                        <option value="Not-Available" ${currentStatus === 'Not-Available' ? 'selected' : ''}>Not Available</option>
                    </select>
                </td>
            `;
        });
        
        tableBody.appendChild(row);
    });
}

function updateStatus(day, timeSlot, status) {
    fetch('/update_cabin_status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            day: day,
            time_slot: timeSlot,
            status: status
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const messageDiv = document.getElementById('updateMessage');
            messageDiv.textContent = 'Status updated successfully!';
            setTimeout(() => {
                messageDiv.textContent = '';
            }, 3000);
            
            // Update the cell color
            const cell = document.querySelector(`select[data-day="${day}"][data-time-slot="${timeSlot}"]`).parentNode;
            cell.className = `status-cell ${status}`;
        } else {
            alert('Error updating status: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating status');
    });
}