// // document.getElementById("login-form")?.addEventListener("submit", async (e) => {
// //     e.preventDefault();
// //     const username = document.getElementById("username").value;
// //     const password = document.getElementById("password").value;
// //     const response = await fetch("/api/login", {
// //       method: "POST",
// //       headers: { "Content-Type": "application/json" },
// //       body: JSON.stringify({ username, password }),
// //     });
// //     if (response.ok) {
// //       window.location.href = "/tasks.html";
// //     } else {
// //       alert("Login failed");
// //     }
// //   });
  

// // Handle tokens
// const setTokens = (access, refresh) => {
//     localStorage.setItem('accessToken', access);
//     localStorage.setItem('refreshToken', refresh);
// };

// const setUserData = (user) => {
//     localStorage.setItem('userId', user.id);
//     localStorage.setItem('userRole', user.role);
//     localStorage.setItem('username', user.username);
// };

// // Login form handler
// document.getElementById('login-form')?.addEventListener('submit', async (e) => {
//     e.preventDefault();
//     try {
//         const response = await fetch('/api/login/', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({
//                 username: document.getElementById('username').value,
//                 password: document.getElementById('password').value
//             })
//         });

//         const data = await response.json();
//         if (response.ok) {
//             setTokens(data.access, data.refresh);
//             setUserData(data.user);
//             window.location.href = '/tasks.html';
//         } else {
//             alert(data.detail || 'Login failed');
//         }
//     } catch (error) {
//         alert('Error during login');
//         console.error(error);
//     }
// });

// // Signup form handler
// document.getElementById('signup-form')?.addEventListener('submit', async (e) => {
//     e.preventDefault();
//     try {
//         const response = await fetch('/api/signup/', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({
//                 username: document.getElementById('username').value,
//                 password: document.getElementById('password').value,
//                 role: document.getElementById('role').value
//             })
//         });

//         const data = await response.json();
//         if (response.ok) {
//             alert('Signup successful! Please login.');
//             window.location.href = '/login.html';
//         } else {
//             alert(Object.values(data).flat().join('\n'));
//         }
//     } catch (error) {
//         alert('Error during signup');
//         console.error(error);
//     }
// });

// // Logout handler
// document.getElementById('logout')?.addEventListener('click', async () => {
//     try {
//         const response = await fetch('/api/logout/', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//                 'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
//             },
//             body: JSON.stringify({
//                 refresh: localStorage.getItem('refreshToken')
//             })
//         });

//         if (response.ok) {
//             localStorage.clear();
//             window.location.href = '/login.html';
//         }
//     } catch (error) {
//         console.error(error);
//         localStorage.clear();
//         window.location.href = '/login.html';
//     }
// });