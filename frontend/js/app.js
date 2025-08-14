// API Base URL
const API_BASE_URL = 'http://127.0.0.1:5000';

// Uygulama durumu
let currentUser = null;
let currentCompany = null;
let documents = [];
let chatMessages = [];

// Sayfa yüklendiğinde
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
});

// Uygulamayı başlat
function initializeApp() {
    const savedUser = localStorage.getItem('currentUser');
    const savedCompany = localStorage.getItem('currentCompany');

    if (savedUser && savedCompany) {
        currentUser = JSON.parse(savedUser);
        currentCompany = JSON.parse(savedCompany);
        showMainApp();
        loadDashboard();
    } else {
        showLogin();
    }
}

// Event listener'lar
function setupEventListeners() {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) loginForm.addEventListener('submit', handleLogin);

    const registerForm = document.getElementById('registerForm');
    if (registerForm) registerForm.addEventListener('submit', handleRegister);

    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
    }
}

// Login
async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        showLoading(true);
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ email, password })
        });
        const result = await response.json();

        if (response.ok) {
            currentUser = result.user;
            currentCompany = result.company;
            localStorage.setItem('authToken', result.token);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            localStorage.setItem('currentCompany', JSON.stringify(currentCompany));
            showMainApp();
            await loadDashboard();
            showAlert('Başarıyla giriş yapıldı!', 'success');
        } else {
            showAlert(result.error || 'Giriş yapılırken hata oluştu!', 'danger');
        }
    } catch (err) {
        console.error('Login error:', err);
        showAlert('Giriş yapılırken bir hata oluştu!', 'danger');
    } finally {
        showLoading(false);
    }
}

// Register
async function handleRegister(e) {
    e.preventDefault();
    const companyName = document.getElementById('companyName').value;
    const companyEmail = document.getElementById('companyEmail').value;
    const username = document.getElementById('username').value;
    const userEmail = document.getElementById('userEmail').value;
    const password = document.getElementById('registerPassword').value;

    try {
        showLoading(true);
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ companyName, companyEmail, username, userEmail, password })
        });
        const result = await response.json();

        if (response.ok) {
            showAlert('Kayıt başarılı! Şimdi giriş yapabilirsiniz.', 'success');
            showLogin();
        } else {
            showAlert(result.error || 'Kayıt olurken hata oluştu!', 'danger');
        }
    } catch (err) {
        console.error('Register error:', err);
        showAlert('Kayıt olurken bir hata oluştu!', 'danger');
    } finally {
        showLoading(false);
    }
}

// Sayfalar
function showLogin() {
    document.getElementById('loginPage').style.display = 'flex';
    document.getElementById('registerPage').style.display = 'none';
    document.getElementById('mainApp').style.display = 'none';
}

function showRegister() {
    document.getElementById('loginPage').style.display = 'none';
    document.getElementById('registerPage').style.display = 'flex';
    document.getElementById('mainApp').style.display = 'none';
}

function showMainApp() {
    document.getElementById('loginPage').style.display = 'none';
    document.getElementById('registerPage').style.display = 'none';
    document.getElementById('mainApp').style.display = 'block';
    showPage('dashboard');
}

function showPage(pageName) {
    const pages = ['dashboardPage', 'documentsPage', 'chatPage'];
    pages.forEach(id => (document.getElementById(id).style.display = 'none'));
    document.getElementById(pageName + 'Page').style.display = 'block';

    switch (pageName) {
        case 'dashboard': loadDashboard(); break;
        case 'documents': loadDocuments(); break;
        case 'chat': loadChat(); break;
    }
    // Üste kaydır (Belgeler tıklayınca aşağıda kalmasın)
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Dashboard
async function loadDashboard() {
    try {
        const token = localStorage.getItem('authToken');
        if (!token) { showLogin(); return; }
        const res = await fetch(`${API_BASE_URL}/api/documents/stats`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            const s = await res.json();
            document.getElementById('totalDocuments').textContent = s.total_documents || 0;
            document.getElementById('processedDocuments').textContent = s.processed_documents || 0;
            document.getElementById('chatSessions').textContent = chatMessages.length;
        }
    } catch (e) {
        console.error('Dashboard stats error:', e);
    }
}

// Belgeler
async function loadDocuments() {
    try {
        const token = localStorage.getItem('authToken');
        const res = await fetch(`${API_BASE_URL}/api/documents`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) throw new Error('Belgeler yüklenemedi');
        const result = await res.json();
        documents = result.documents || [];

        const el = document.getElementById('documentsTable');
        if (documents.length === 0) {
            el.innerHTML = `
              <div class="text-center py-5">
                <i class="fas fa-folder-open fa-3x text-muted mb-3"></i>
                <p class="text-muted">Henüz belge yüklenmemiş</p>
                <button class="btn btn-primary" onclick="showUploadModal()">
                  <i class="fas fa-plus me-2"></i>İlk Belgenizi Yükleyin
                </button>
              </div>`;
            return;
        }

        let html = '<div class="table-responsive"><table class="table table-hover"><thead><tr>';
        html += '<th>Dosya Adı</th><th>Tür</th><th>Boyut</th><th>Durum</th><th>Tarih</th><th>İşlemler</th>';
        html += '</tr></thead><tbody>';
        documents.forEach(doc => {
            html += `
              <tr>
                <td>
                  <div class="d-flex align-items-center">
                    <div class="file-icon ${doc.file_type}">
                      <i class="fas fa-file-${getFileIcon(doc.file_type)}"></i>
                    </div>
                    ${doc.original_filename}
                  </div>
                </td>
                <td><span class="badge bg-secondary">${doc.file_type.toUpperCase()}</span></td>
                <td>${formatFileSize(doc.file_size)}</td>
                <td>${doc.is_processed ? '<span class="badge bg-success">İşlendi</span>' : '<span class="badge bg-warning">İşleniyor</span>'}</td>
                <td>${formatDate(doc.created_at)}</td>
                <td>
                  <button class="btn btn-sm btn-outline-primary me-1" onclick="viewDocument(${doc.id})"><i class="fas fa-eye"></i></button>
                  <button class="btn btn-sm btn-outline-danger" onclick="deleteDocument(${doc.id})"><i class="fas fa-trash"></i></button>
                </td>
              </tr>`;
        });
        html += '</tbody></table></div>';
        el.innerHTML = html;
    } catch (e) {
        console.error('Load documents error:', e);
        document.getElementById('documentsTable').innerHTML = `
          <div class="text-center py-5">
            <i class="fas fa-exclamation-triangle fa-3x text-danger mb-3"></i>
            <p class="text-danger">Belgeler yüklenirken hata oluştu</p>
          </div>`;
    }
}

// Upload Modal
function showUploadModal() {
    const modal = new bootstrap.Modal(document.getElementById('uploadModal'));
    modal.show();
}

// Dosya yükleme
async function uploadFiles() {
    const fileInput = document.getElementById('fileInput');
    const files = fileInput.files;
    if (files.length === 0) { showAlert('Lütfen dosya seçin!', 'warning'); return; }

    try {
        showLoading(true);
        const fd = new FormData();
        for (let f of files) fd.append('files', f);

        const token = localStorage.getItem('authToken');
        const res = await fetch(`${API_BASE_URL}/api/documents/upload`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: fd
        });
        const result = await res.json();

        if (res.ok) {
            bootstrap.Modal.getInstance(document.getElementById('uploadModal')).hide();
            fileInput.value = '';
            showAlert(result.message, 'success');
            await loadDocuments();
            await loadDashboard();
        } else {
            showAlert(result.error || 'Dosya yüklenirken hata oluştu!', 'danger');
        }
    } catch (e) {
        console.error('Upload error:', e);
        showAlert('Dosya yüklenirken bir hata oluştu!', 'danger');
    } finally {
        showLoading(false);
    }
}

function viewDocument(docId) {
    showAlert('Belge görüntüleme özelliği yakında eklenecek!', 'info');
}

async function deleteDocument(docId) {
    if (!confirm('Bu belgeyi silmek istediğinizden emin misiniz?')) return;
    try {
        showLoading(true);
        const token = localStorage.getItem('authToken');
        const res = await fetch(`${API_BASE_URL}/api/documents/${docId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const result = await res.json();
        if (res.ok) {
            showAlert('Belge başarıyla silindi!', 'success');
            await loadDocuments();
            await loadDashboard();
        } else {
            showAlert(result.error || 'Belge silinirken hata oluştu!', 'danger');
        }
    } catch (e) {
        console.error('Delete error:', e);
        showAlert('Belge silinirken hata oluştu!', 'danger');
    } finally {
        showLoading(false);
    }
}

// Yardımcılar (alert/loading/icon/format)
function showAlert(message, type) {
    const el = document.createElement('div');
    el.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    el.style.cssText = 'top:20px;right:20px;z-index:9999;min-width:300px;';
    el.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
    document.body.appendChild(el);
    setTimeout(()=>{ el.remove(); }, 5000);
}

function showLoading(show) {
    let el = document.getElementById('globalLoader');
    if (show) {
        if (!el) {
            el = document.createElement('div');
            el.id = 'globalLoader';
            el.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.5);z-index:9999;display:flex;align-items:center;justify-content:center;';
            el.innerHTML = '<div class="spinner-border text-primary" role="status"></div>';
            document.body.appendChild(el);
        }
        el.style.display = 'flex';
    } else if (el) el.style.display = 'none';
}

function getFileIcon(t) {
    const m = { pdf:'pdf', doc:'word', docx:'word', xls:'excel', xlsx:'excel', png:'image', jpg:'image', jpeg:'image', gif:'image', txt:'alt' };
    return m[t] || 'file';
}

function formatFileSize(b) {
    if (b === 0) return '0 Bytes';
    const k = 1024, s = ['Bytes','KB','MB','GB']; const i = Math.floor(Math.log(b)/Math.log(k));
    return parseFloat((b/Math.pow(k,i)).toFixed(2)) + ' ' + s[i];
}

function formatDate(s) { return new Date(s).toLocaleDateString('tr-TR'); }

function loadChat() {
    const c = document.getElementById('chatMessages');
    if (c.children.length <= 1) addChatMessage('Merhaba! Belgelerinizle ilgili sorularınızı sorabilirsiniz.', 'assistant');
}
function addChatMessage(m, t) {
    const c = document.getElementById('chatMessages');
    const d = document.createElement('div'); d.className = `chat-message ${t}`; d.textContent = m;
    c.appendChild(d); c.scrollTop = c.scrollHeight;
}
function addTypingIndicator(){ const c=document.getElementById('chatMessages'); const d=document.createElement('div'); d.className='chat-message assistant typing-indicator'; d.innerHTML='<div class="loading-spinner"></div> Yazıyor...'; c.appendChild(d); c.scrollTop=c.scrollHeight; }
function removeTypingIndicator(){ const t=document.querySelector('.typing-indicator'); if(t) t.remove(); }

function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    localStorage.removeItem('currentCompany');
    currentUser = currentCompany = null; documents = []; chatMessages = [];
    showLogin();
    showAlert('Başarıyla çıkış yapıldı!', 'info');
}
