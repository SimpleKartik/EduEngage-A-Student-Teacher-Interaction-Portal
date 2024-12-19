function viewCabinStatus(name, department, teacherId) {
    window.location.href = `/view_cabin_status?name=${encodeURIComponent(name)}&department=${encodeURIComponent(department)}&id=${teacherId}`;
} 