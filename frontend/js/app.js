// Configuration
const API_BASE_URL = 'http://127.0.0.1:5000';

// Global Variables
let currentUser = null;
let authToken = localStorage.getItem('authToken');

// Initialize App
document.addEventListener('DOMContentLoaded', function() {
    console.log('App initialized');
    
    // Check if user is logged in
    if (authToken) {
        showAuthenticatedState();
        loadUserInfo();
    } else {
        showUnauthenticatedState();
    }
    
    // Initialize event listeners
    initializeEventListeners();
    
    // Handle URL hash navigation
    handleNavigation();
    window.addEventListener('hashchange', handleNavigation);
});

// Navigation System
function handleNavigation() {
    const hash = window.location.hash.substring(1) || 'home';
    showPage(hash);
}

function showPage(pageId) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // Show target page
    const targetPage = document.getElementById(pageId);
    if (targetPage) {
        targetPage.classList.add('active');
        targetPage.classList.add('fade-in');
        
        // Load page-specific data
        switch(pageId) {
            case 'dashboard':
                if (authToken) loadDashboard();
                break;
            case 'documents':
                if (authToken) loadDocuments();
                break;
            case 'chat':
                if (authToken) initializeChat();
                break;
        }
    }
    
    // Update active nav links
    updateActiveNavLinks(pageId);
}

function updateActiveNavLinks(pageId) {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    const activeLink = document.querySelector(`a[href="#${pageId}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
}

// Authentication State Management
function showAuthenticatedState() {
    document.getElementById('nav-login').style.display = 'none';
    document.getElementById('nav-dashboard').style.display = 'block';
    document.getElementById('nav-documents').style.display = 'block';
    document.getElementById('nav-chat').style.display = 'block';
    document.getElementById('nav-logout').style.display = 'block';
}

function showUnauthenticatedState() {
    document.getElementById('nav-login').style.display = 'block';
    document.getElementById('nav-dashboard').style.display = 'none';
    document.getElementById('nav-documents').style.display = 'none';
    document.getElementById('nav-chat').style.display = 'none';
    document.getElementById('nav-logout').style.display = 'none';
}

// Event Listeners
function initializeEventListeners() {
    // Auth Forms
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const chatForm = document.getElementById('chatForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
    
    if (chatForm) {
        chatForm.addEventListener('submit', handleChatMessage);
    }
    
    // File Upload
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');
    const selectFilesBtn = document.getElementById('selectFilesBtn');
    
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }
    
    if (selectFilesBtn) {
        selectFilesBtn.addEventListener('click', () => {
            fileInput.click();
        });
    }
    
    if (uploadArea) {
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('dragleave', handleDragLeave);
        uploadArea.addEventListener('drop', handleFileDrop);
    }
    
    // Search and Filter
    const searchInput = document.getElementById('searchDocuments');
    const filterSelect = document.getElementById('filterDocuments');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(filterDocuments, 300));
    }
    
    if (filterSelect) {
        filterSelect.addEventListener('change', filterDocuments);
    }
    
    // Upload Modal Events
    const uploadModal = document.getElementById('uploadModal');
    if (uploadModal) {
        uploadModal.addEventListener('show.bs.modal', function() {
            resetUploadModal();
        });
    }
}

// Authentication Functions
async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const submitBtn = e.target.querySelector('button[type="submit"]');
    
    try {
        submitBtn.innerHTML = '<div class="spinner me-2"></div>Giriş yapılıyor...';
        submitBtn.disabled = true;
        
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.token;
            localStorage.setItem('authToken', authToken);
            currentUser = data.user;
            
            showSuccess('Giriş başarılı!');
            showAuthenticatedState();
            window.location.hash = 'dashboard';
        } else {
            showError(data.error || 'Giriş başarısız');
        }
    } catch (error) {
        console.error('Login error:', error);
        showError('Bağlantı hatası. Lütfen tekrar deneyin.');
    } finally {
        submitBtn.innerHTML = '<i class="fas fa-sign-in-alt me-2"></i>Giriş Yap';
        submitBtn.disabled = false;
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const company_name = document.getElementById('registerCompany').value;
    const full_name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const submitBtn = e.target.querySelector('button[type="submit"]');
    
    try {
        submitBtn.innerHTML = '<div class="spinner me-2"></div>Kayıt olunuyor...';
        submitBtn.disabled = true;
        
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ company_name, full_name, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess('Kayıt başarılı! Giriş yapabilirsiniz.');
            window.location.hash = 'login';
            document.getElementById('registerForm').reset();
        } else {
            showError(data.error || 'Kayıt başarısız');
        }
    } catch (error) {
        console.error('Register error:', error);
        showError('Bağlantı hatası. Lütfen tekrar deneyin.');
    } finally {
        submitBtn.innerHTML = '<i class="fas fa-user-plus me-2"></i>Kayıt Ol';
        submitBtn.disabled = false;
    }
}

async function logout() {
    try {
        await fetch(`${API_BASE_URL}/api/auth/logout`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        });
    } catch (error) {
        console.error('Logout error:', error);
    }
    
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    showUnauthenticatedState();
    window.location.hash = 'home';
    showSuccess('Çıkış yapıldı');
}

async function loadUserInfo() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            
            const welcomeElement = document.getElementById('userWelcome');
            if (welcomeElement && currentUser) {
                welcomeElement.textContent = `Hoş geldiniz, ${currentUser.full_name}`;
            }
        }
    } catch (error) {
        console.error('Load user info error:', error);
    }
}

// Dashboard Functions
async function loadDashboard() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/documents/stats`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const stats = await response.json();
            updateDashboardStats(stats);
        }
    } catch (error) {
        console.error('Load dashboard error:', error);
    }
}

function updateDashboardStats(stats) {
    document.getElementById('totalDocuments').textContent = stats.total_documents || 0;
    document.getElementById('todayUploads').textContent = stats.today_uploads || 0;
    document.getElementById('totalChats').textContent = stats.total_chats || 0;
    document.getElementById('storageUsed').textContent = formatFileSize(stats.storage_used || 0);
}

// Documents Functions
async function loadDocuments() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/documents/list`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            displayDocuments(data.documents);
        }
    } catch (error) {
        console.error('Load documents error:', error);
        showError('Belgeler yüklenirken hata oluştu');
    }
}

function displayDocuments(documents) {
    const grid = document.getElementById('documentsGrid');
    
    if (!documents || documents.length === 0) {
        grid.innerHTML = `
            <div class="col-12">
                <div class="text-center py-5">
                    <i class="fas fa-folder-open fs-1 text-muted mb-3"></i>
                    <h4 class="text-muted">Henüz belge yok</h4>
                    <p class="text-muted">İlk belgenizi yükleyerek başlayın</p>
                    <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#uploadModal">
                        <i class="fas fa-upload me-2"></i>Belge Yükle
                    </button>
                </div>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = documents.map(doc => `
        <div class="col-md-6 col-lg-4">
            <div class="document-card">
                <div class="card-body">
                    <div class="document-icon">
                        <i class="fas fa-${getFileIcon(doc.file_type)}"></i>
                    </div>
                    <h5 class="card-title">${doc.filename}</h5>
                    <p class="card-text text-muted">
                        <small>${formatFileSize(doc.file_size)} • ${formatDate(doc.upload_date)}</small>
                    </p>
                    <div class="d-flex gap-2">
                        <button class="btn btn-sm btn-outline-primary" onclick="downloadDocument('${doc.id}', '${doc.filename}')">
                            <i class="fas fa-download"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteDocument('${doc.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// File Upload Functions
function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    console.log('Files selected:', files.length);
    
    // Show selected files info
    const selectedFilesInfo = document.getElementById('selectedFilesInfo');
    const fileCount = document.getElementById('fileCount');
    
    if (files.length > 0) {
        fileCount.textContent = files.length;
        selectedFilesInfo.style.display = 'block';
    } else {
        selectedFilesInfo.style.display = 'none';
    }
    
    updateUploadButton(files.length > 0);
}

function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
}

function handleFileDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
    
    const files = Array.from(e.dataTransfer.files);
    console.log('Files dropped:', files.length);
    
    // Set files to input
    const fileInput = document.getElementById('fileInput');
    fileInput.files = e.dataTransfer.files;
    
    // Show selected files info
    const selectedFilesInfo = document.getElementById('selectedFilesInfo');
    const fileCount = document.getElementById('fileCount');
    
    if (files.length > 0) {
        fileCount.textContent = files.length;
        selectedFilesInfo.style.display = 'block';
    } else {
        selectedFilesInfo.style.display = 'none';
    }
    
    updateUploadButton(files.length > 0);
}

function updateUploadButton(hasFiles) {
    const uploadBtn = document.getElementById('uploadBtn');
    uploadBtn.disabled = !hasFiles;
}

async function uploadFiles() {
    const fileInput = document.getElementById('fileInput');
    const files = fileInput.files;
    
    if (files.length === 0) {
        showError('Lütfen en az bir dosya seçin');
        return;
    }
    
    const formData = new FormData();
    for (let file of files) {
        formData.append('files', file);
    }
    
    const progressDiv = document.getElementById('uploadProgress');
    const progressBar = progressDiv.querySelector('.progress-bar');
    const uploadBtn = document.getElementById('uploadBtn');
    
    try {
        progressDiv.style.display = 'block';
        uploadBtn.innerHTML = '<div class="spinner me-2"></div>Yükleniyor...';
        uploadBtn.disabled = true;
        
        // Simulate progress (real progress would need server-side support)
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += 10;
            progressBar.style.width = progress + '%';
            if (progress >= 90) {
                clearInterval(progressInterval);
            }
        }, 200);
        
        const response = await fetch(`${API_BASE_URL}/api/documents/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });
        
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess(`${data.uploaded_count} dosya başarıyla yüklendi`);
            
            // Close modal and reset form
            const modal = bootstrap.Modal.getInstance(document.getElementById('uploadModal'));
            modal.hide();
            resetUploadModal();
            
            // Refresh documents list
            if (window.location.hash === '#documents') {
                loadDocuments();
            }
        } else {
            showError(data.error || 'Yükleme başarısız');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showError('Yükleme sırasında hata oluştu');
    } finally {
        uploadBtn.innerHTML = '<i class="fas fa-upload me-2"></i>Yükle';
        uploadBtn.disabled = false;
        progressDiv.style.display = 'none';
        progressBar.style.width = '0%';
    }
}

function resetUploadModal() {
    const fileInput = document.getElementById('fileInput');
    const selectedFilesInfo = document.getElementById('selectedFilesInfo');
    const progressDiv = document.getElementById('uploadProgress');
    const progressBar = progressDiv.querySelector('.progress-bar');
    const uploadBtn = document.getElementById('uploadBtn');
    
    // Reset file input
    fileInput.value = '';
    
    // Hide selected files info
    selectedFilesInfo.style.display = 'none';
    
    // Hide progress
    progressDiv.style.display = 'none';
    progressBar.style.width = '0%';
    
    // Reset upload button
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<i class="fas fa-upload me-2"></i>Yükle';
}

async function deleteDocument(docId) {
    if (!confirm('Bu belgeyi silmek istediğinizden emin misiniz?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/documents/delete/${docId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            showSuccess('Belge başarıyla silindi');
            loadDocuments();
        } else {
            const data = await response.json();
            showError(data.error || 'Silme başarısız');
        }
    } catch (error) {
        console.error('Delete error:', error);
        showError('Silme sırasında hata oluştu');
    }
}

function downloadDocument(docId, filename) {
    const link = document.createElement('a');
    link.href = `${API_BASE_URL}/api/documents/download/${docId}`;
    link.download = filename;
    link.click();
}

// Chat Functions
function initializeChat() {
    // Chat is already initialized with welcome message
    console.log('Chat initialized');
}

async function handleChatMessage(e) {
    e.preventDefault();
    
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addChatMessage(message, 'user');
    input.value = '';
    
    // Add typing indicator
    const typingId = addTypingIndicator();
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/chat/message`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        removeTypingIndicator(typingId);
        
        if (response.ok) {
            const data = await response.json();
            addChatMessage(data.response, 'ai');
        } else {
            addChatMessage('Üzgünüm, şu anda yanıt veremiyorum. Lütfen daha sonra tekrar deneyin.', 'ai');
        }
    } catch (error) {
        console.error('Chat error:', error);
        removeTypingIndicator(typingId);
        addChatMessage('Bağlantı hatası oluştu. Lütfen tekrar deneyin.', 'ai');
    }
}

function addChatMessage(content, type) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <p>${content}</p>
        </div>
        <div class="message-time">${formatTime(new Date())}</div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function addTypingIndicator() {
    const messagesContainer = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    const typingId = 'typing-' + Date.now();
    
    typingDiv.id = typingId;
    typingDiv.className = 'message ai-message';
    typingDiv.innerHTML = `
        <div class="message-content">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return typingId;
}

function removeTypingIndicator(typingId) {
    const typingElement = document.getElementById(typingId);
    if (typingElement) {
        typingElement.remove();
    }
}

// Search and Filter Functions
function filterDocuments() {
    const searchTerm = document.getElementById('searchDocuments').value.toLowerCase();
    const filterType = document.getElementById('filterDocuments').value;
    
    // This would filter the displayed documents
    // For now, just reload all documents
    loadDocuments();
}

// Utility Functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('tr-TR');
}

function formatTime(date) {
    return date.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
}

function getFileIcon(fileType) {
    const icons = {
        'pdf': 'file-pdf',
        'docx': 'file-word',
        'doc': 'file-word',
        'xlsx': 'file-excel',
        'xls': 'file-excel',
        'jpg': 'file-image',
        'jpeg': 'file-image',
        'png': 'file-image',
        'gif': 'file-image'
    };
    return icons[fileType?.toLowerCase()] || 'file';
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showSuccess(message) {
    showNotification(message, 'success');
}

function showError(message) {
    showNotification(message, 'error');
}

function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 100px; right: 20px; z-index: 9999; min-width: 300px;';
    
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}
