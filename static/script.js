function selectRole(role) {  
    if (role === 'student') {  
        window.location.href = '/student_login.html'; // Redirect to student login page  
    } else if (role === 'teacher') {  
        window.location.href = '/teacher_login.html'; // Redirect to teacher login page  
    }  
}  

// Function to handle student login  
function loginStudent(event) {  
    event.preventDefault();
    
    const username = document.getElementById('studentUsername').value;
    const password = document.getElementById('studentPassword').value;
    const messageElement = document.getElementById('studentMessage');
    
    // Clear any previous messages
    messageElement.textContent = '';
    
    fetch('/login/student', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/student_dashboard.html';
        } else {
            messageElement.textContent = data.message || 'Login failed. Please check your credentials.';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        messageElement.textContent = 'An error occurred during login. Please try again.';
    });
    
    return false;
}  

// Function to handle teacher login  
function loginTeacher(event) {  
    event.preventDefault();
    const username = document.getElementById('teacherUsername').value;
    const password = document.getElementById('teacherPassword').value;
    
    fetch('/login/teacher', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = data.redirect;
        } else {
            document.getElementById('teacherMessage').textContent = data.message;
        }
    });
}
const facultyData = [  
    { name: "Dr. John Smith", department: "Computer Science" },  
    { name: "Prof. Jane Doe", department: "Mechanical Engineering" },  
    { name: "Dr. Emily Johnson", department: "Electrical Engineering" },  
    { name: "Dr. Michael Brown", department: "Civil Engineering" },  
    { name: "Prof. Sarah Davis", department: "Biotechnology" }  
];  

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
                <button class="cabin-status-button" onclick="checkCabinStatus('${faculty.name}')">Cabin Status</button>  
            `;  
            resultsDiv.appendChild(facultyItem);  
        });  
    } else {  
        resultsDiv.innerHTML = "<p>No faculty found.</p>";  
    }  
}  

function checkCabinStatus(facultyName) {  
    alert(`Checking cabin status for ${facultyName}`);  
    // You can replace this alert with real functionality to check cabin status  
}


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

function viewCabinStatus(name, department) {  
    // Redirect to the cabin status page with query parameters  
    window.location.href = `cabin_status.html?name=${encodeURIComponent(name)}&department=${encodeURIComponent(department)}`;  
}
