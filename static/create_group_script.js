const studentsData = {  
    "21": ["Aarav Sharma", "Vivaan Gupta", "Reyansh Patel", "Krishna Iyer", "Vihaan Rao"],  
    "22": ["Anaya Verma", "Saanvi Yadav", "Diya Reddy", "Ishita Joshi", "Neha Bansal"],  
    "23": ["Rahul Sen", "Mohit Sethi", "Harsh Agarwal", "Aakash Chauhan", "Akshay Mishra"],  
    "24": ["Priya Singh", "Komal Thakur", "Shreya Dave", "Tanishq Sharma", "Alok Patil"],  
};  

let selectedMembers = [];  

function updateTeamLeaderOptions() {  
    const batchSelect = document.getElementById("batchSelect").value;  
    const teamLeaderSelect = document.getElementById("teamLeaderSelect");  
    teamLeaderSelect.innerHTML = '<option value="">--Select Team Leader--</option>'; // Reset options  

    if (batchSelect) {  
        studentsData[batchSelect].forEach(student => {  
            const option = document.createElement("option");  
            option.value = student;  
            option.textContent = student;  
            teamLeaderSelect.appendChild(option);  
        });  
    }  
}  

function updateTeamMembersOptions() {  
    const batchSelect = document.getElementById("batchSelect").value;  
    const memberListDiv = document.getElementById("memberList");  
    memberListDiv.innerHTML = ''; // Reset options  
    selectedMembers = []; // Reset selected members  

    if (batchSelect) {  
        studentsData[batchSelect].forEach(student => {  
            const memberItem = document.createElement("div");  
            memberItem.textContent = student;  
            memberItem.classList.add("member-item");  
            memberItem.onclick = () => selectMember(student);  
            memberListDiv.appendChild(memberItem);  
        });  
    }  
}  

function clearTeamMembers() {  
    selectedMembers = []; // Reset selected members  
    document.getElementById("memberSearch").value = ""; // Clear search input  
    document.getElementById("memberList").innerHTML = ""; // Clear member list  
    document.getElementById("groupMessage").textContent = ""; // Clear messages  
}  

function filterMembers() {  
    const searchValue = document.getElementById("memberSearch").value.toLowerCase();  
    const memberListDiv = document.getElementById("memberList");  
    const batchSelect = document.getElementById("batchSelect").value;  

    if (batchSelect) {  
        memberListDiv.innerHTML = ''; // Clear previous list  

        studentsData[batchSelect].forEach(student => {  
            if (student.toLowerCase().includes(searchValue)) {  
                const memberItem = document.createElement("div");  
                memberItem.textContent = student;  
                memberItem.classList.add("member-item");  
                memberItem.onclick = () => selectMember(student);  
                memberListDiv.appendChild(memberItem);  
            }  
        });  
    }  
}  

function selectMember(member) {  
    if (selectedMembers.length < 4) {  
        if (!selectedMembers.includes(member)) {  
            selectedMembers.push(member);  
            updateSelectedMembersDisplay();  
        }  
        if (selectedMembers.length === 4) {  
            document.getElementById("groupMessage").textContent = "Maximum member limit reached (4 members).";  
        }  
    }  
}  

function updateSelectedMembersDisplay() {  
    const memberListDiv = document.getElementById("memberList");  
    const memberItems = memberListDiv.getElementsByClassName("member-item");  
    for (let item of memberItems) {  
        item.classList.remove("selected");  
    }  
    selectedMembers.forEach(member => {  
        Array.from(memberItems).forEach(item => {  
            if (item.textContent === member) {  
                item.classList.add("selected");  
            }  
        });  
    });  
}  

function submitGroup() {  
    const teamLeader = document.getElementById("teamLeaderSelect").value;  

    // Check if team leader is selected  
    if (!teamLeader) {  
        document.getElementById("groupMessage").textContent = "Please select a team leader.";  
        return;  
    }  

    // Total group members validation  
    if (selectedMembers.length > 4) {  
        document.getElementById("groupMessage").textContent = "You can select a maximum of 4 team members.";  
        return;  
    }  

    // Store group info in local storage  
    const groupInfo = { leader: teamLeader, members: [...selectedMembers] };  
    let groups = JSON.parse(localStorage.getItem('groups')) || [];  
    groups.push(groupInfo);  
    localStorage.setItem('groups', JSON.stringify(groups));  

    document.getElementById("groupMessage").textContent = `Group created successfully! Team Leader: ${teamLeader}.`;  
    clearTeamMembers(); // Reset fields after submission  
}