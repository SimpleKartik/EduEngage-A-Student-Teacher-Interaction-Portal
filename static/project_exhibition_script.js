// Sample data for groups (this can be replaced with a database call)  
let groups = [];  

// Function to create a group  
function createGroup() {  
    const groupName = prompt("Enter the name of the group:");  
    if (groupName) {  
        groups.push(groupName);  
        document.getElementById("groupMessage").textContent = `Group "${groupName}" created successfully!`;  
    } else {  
        document.getElementById("groupMessage").textContent = "Group creation cancelled.";  
    }  
}  

// Function to view current groups  
function viewGroups() {  
    if (groups.length === 0) {  
        document.getElementById("groupMessage").textContent = "No groups available.";  
    } else {  
        const groupList = groups.map((group, index) => `${index + 1}. ${group}`).join('<br>');  
        document.getElementById("groupMessage").innerHTML = `Current Groups:<br>${groupList}`;  
    }  
}