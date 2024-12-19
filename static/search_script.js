// Sample data for faculty (this can be replaced with a database call)
const facultyData = [
    { name: "Dr. John Smith", department: "Computer Science" },
    { name: "Prof. Jane Doe", department: "Mechanical Engineering" },
    { name: "Dr. Emily Johnson", department: "Electrical Engineering" },
    { name: "Dr. Michael Brown", department: "Civil Engineering" },
    { name: "Prof. Sarah Davis", department: "Biotechnology" }
];

// Function to search faculty based on input
function searchFaculty() {
    const input = document.getElementById("facultySearch").value.toLowerCase();
    const resultsDiv = document.getElementById("facultyResults");
    resultsDiv.innerHTML = ""; // Clear previous results

    const filteredFaculty = facultyData.filter(faculty =>
        faculty.name.toLowerCase().includes(input)
    );

    if (filteredFaculty.length > 0) {
        filteredFaculty.forEach(faculty => {
            const facultyItem = document.createElement("div");
            facultyItem.className = "faculty-item";

            facultyItem.innerHTML = `
                <div class="faculty-name">${faculty.name}</div>
                <div>Department: ${faculty.department}</div>
                <button class="cabin-status-button" onclick="viewCabinStatus('${faculty.name}', '${faculty.department}')">Cabin Status</button>
            `;
            resultsDiv.appendChild(facultyItem);
        });
    } else {
        resultsDiv.innerHTML = "<p>No faculty found.</p>";
    }
}

// Function to view cabin status
function viewCabinStatus(name, department) {
    // Redirect to the cabin status page with query parameters
    window.location.href = `cabin_status.html?name=${encodeURIComponent(name)}&department=${encodeURIComponent(department)}`;
}

// Fetch cabin status from the server
function fetchCabinStatus() {
    fetch('/get_cabin_status')
        .then(response => response.json())
        .then(data => {
            const timetable = document.getElementById('timetable').getElementsByTagName('tbody')[0];
            data.forEach(row => {
                const day = row.day;
                const timeSlot = row.time_slot;
                const status = row.status;

                // Find the correct cell based on day and timeSlot
                const dayRow = Array.from(timetable.rows).find(r => r.cells[0].textContent === day);
                if (dayRow) {
                    const timeSlotIndex = getTimeSlotIndex(timeSlot);
                    if (timeSlotIndex !== -1) {
                        const cell = dayRow.cells[timeSlotIndex + 1]; // +1 because the first cell is the day
                        cell.classList.add(status.toLowerCase().replace(' ', '-')); // Add class based on status
                        cell.textContent = status; // Set the text content
                    }
                }
            });
        });
}

// Function to get the index of the time slot
function getTimeSlotIndex(timeSlot) {
    const timeSlots = ['8:30 AM', '10:05 AM', '11:40 AM', '1:15 PM', '2:50 PM', '4:25 PM', '6:00 PM', '7:30 PM'];
    return timeSlots.indexOf(timeSlot);
}

// Function to change the status of a timetable cell
function changeStatus(cell, day, timeSlot) {
    let newStatus;
    if (cell.classList.contains('available')) {
        newStatus = 'Busy';
    } else if (cell.classList.contains('busy')) {
        newStatus = 'Not Available';
    } else {
        newStatus = 'Available';
    }

    // Update the cell status
    cell.classList.toggle('available');
    cell.classList.toggle('busy');
    cell.classList.toggle('not-available');
    cell.textContent = newStatus;

    // Send the updated status to the server
    fetch('/update_cabin_status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            day: day,
            time_slot: timeSlot,
            status: newStatus
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            console.log(data.message);
            // Update the UI with the new cabin status
            updateCabinStatusTable(data.updated_status);
        }
    })
    .catch(error => console.error('Error:', error));
}

function updateCabinStatusTable(updatedStatus) {
    // Logic to update the cabin status table in the UI
    const tableBody = document.getElementById('cabin-status-table-body');
    tableBody.innerHTML = ''; // Clear existing rows

    updatedStatus.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${row.day}</td>
            <td>${row.time_slot}</td>
            <td class="${row.status.toLowerCase()}">${row.status}</td>
        `;
        tableBody.appendChild(tr);
    });
}