// // document.addEventListener("DOMContentLoaded", async () => {
// //     const taskList = document.getElementById("task-list");
// //     const response = await fetch("/api/tasks", {
// //       headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
// //     });
// //     const tasks = await response.json();
// //     tasks.forEach((task) => {
// //       const li = document.createElement("li");
// //       li.innerHTML = `<a href="/task_detail.html?task_id=${task.id}">${task.name}</a>`;
// //       taskList.appendChild(li);
// //     });
// //   });


// // Utility function to format date
// const formatDate = (dateString) => {
//     return dateString ? new Date(dateString).toLocaleString() : 'N/A';
// };

// // Task list component
// const createTaskElement = (task) => {
//     const div = document.createElement('div');
//     div.className = 'bg-white p-4 rounded shadow';
//     div.innerHTML = `
//         <div class="flex justify-between items-center">
//             <h3 class="text-lg font-semibold">${task.title}</h3>
//             <span class="px-2 py-1 rounded ${task.is_done ? 'bg-green-200' : 'bg-yellow-200'}">
//                 ${task.is_done ? 'Completed' : 'Pending'}
//             </span>
//         </div>
//         <p class="text-gray-600 mt-2">${task.description || 'No description'}</p>
//         <div class="mt-4 text-sm text-gray-500">
//             <p>Created: ${formatDate(task.created_at)}</p>
//             <p>Updated: ${formatDate(task.updated_at)}</p>
//             ${task.completed_at ? `<p>Completed: ${formatDate(task.completed_at)}</p>` : ''}
//         </div>
//         <div class="mt-4 flex gap-2">
//             <button onclick="viewTask(${task.id})" class="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600">
//                 View
//             </button>
//             ${(localStorage.getItem('userRole') === 'lead' || task.developer === parseInt(localStorage.getItem('userId'))) ? `
//                 <button onclick="editTask(${task.id})" class="px-3 py-1 bg-yellow-500 text-white rounded hover:bg-yellow-600">
//                     Edit
//                 </button>
//                 <button onclick="deleteTask(${task.id})" class="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600">
//                     Delete
//                 </button>
//             ` : ''}
//         </div>
//     `;
//     return div;
// };

// // Load tasks
// const loadTasks = async () => {
//     try {
//         const response = await fetch('/api/tasks/', {
//             headers: {
//                 'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
//             }
//         });
        
//         if (response.ok) {
//             const tasks = await response.json();
//             const taskList = document.getElementById('task-list');
//             taskList.innerHTML = '';
//             tasks.forEach(task => {
//                 taskList.appendChild(createTaskElement(task));
//             });
//         } else {
//             window.location.href = '/login.html';
//         }
//     } catch (error) {
//         console.error(error);
//         alert('Error loading tasks');
//     }
// };

// // Create task
// const createTaskModal = async () => {
//     const modal = document.createElement('div');
//     modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center';
//     modal.innerHTML = `
//         <div class="bg-white p-6 rounded-lg w-96">
//             <h3 class="text-xl font-bold mb-4">Create New Task</h3>
//             <form id="create-task-form">
//                 <div class="mb-4">
//                     <label class="block text-sm font-medium mb-1">Title</label>
//                     <input type="text" name="title" required class="w-full px-3 py-2 border rounded">
//                 </div>
//                 <div class="mb-4">
//                     <label class="block text-sm font-medium mb-1">Description</label>
//                     <textarea name="description" class="w-full px-3 py-2 border rounded"></textarea>
//                 </div>
//                 <div class="flex justify-end gap-2">
//                     <button type="button" onclick="this.closest('.fixed').remove()" 
//                             class="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600">
//                         Cancel
//                     </button>
//                     <button type="submit" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
//                         Create
//                     </button>
//                 </div>
//             </form>
//         </div>
//     `;
//     document.body.appendChild(modal);

//     document.getElementById('create-task-form').addEventListener('submit', async (e) => {
//         e.preventDefault();
//         try {
//             const response = await fetch('/api/tasks/', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                     'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
//                 },
//                 body: JSON.stringify({
//                     title: e.target.title.value,
//                     description: e.target.description.value
//                 })
//             });

//             if (response.ok) {
//                 modal.remove();
//                 loadTasks();
//             } else {
//                 alert('Error creating task');
//             }
//         } catch (error) {
//             console.error(error);
//             alert('Error creating task');
//         }
//     });
// };

// // Delete task
// const deleteTask = async (taskId) => {
//     if (confirm('Are you sure you want to delete this task?')) {
//         try {
//             const response = await fetch(`/api/tasks/${taskId}/`, {
//                 method: 'DELETE',
//                 headers: {
//                     'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
//                 }
//             });

//             if (response.ok) {
//                 loadTasks();
//             } else {
//                 alert('Error deleting task');
//             }
//         } catch (error) {
//             console.error(error);
//             alert('Error deleting task');
//         }
//     }
// };

// // Initialize tasks page
// if (document.getElementById('task-list')) {
//     loadTasks();
//     document.getElementById('create-task')?.addEventListener('click', createTaskModal);
// }

// // View task
// const viewTask = (taskId) => {
//     window.location.href = `/task_detail.html?id=${taskId}`;
// };

// // Load task detail
// const loadTaskDetail = async () => {
//     const params = new URLSearchParams(window.location.search);
//     const taskId = params.get('id');
    
//     if (taskId) {
//         try {
//             const response = await fetch(`/api/tasks/${taskId}/`, {
//                 headers: {
//                     'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
//                 }
//             });

//             if (response.ok) {
//                 const task = await response.json();
//                 const detailDiv = document.getElementById('task-detail');
//                 detailDiv.appendChild(createTaskElement(task));
//             } else {
//                 alert('Error loading task details');
//                 window.location.href = '/tasks.html';
//             }
//         } catch (error) {
//             console.error(error);
//             alert('Error loading task details');
//             window.location.href = '/tasks.html';
//         }
//     }
// };

// // Initialize task detail page
// if (document.getElementById('task-detail')) {
//     loadTaskDetail();
//     document.getElementById('back-to-tasks')?.addEventListener('click', () => {
//         window.location.href = '/tasks.html';
//     });
// }