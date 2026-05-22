/* ============================================
   PHARMACIE H.I.B - JAVASCRIPT MODERNE
   Version: 2.0
   ============================================ */

// ============================================
// 1. ATTENDRE LE CHARGEMENT DU DOM
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('%c💊 Pharmacie H.I.B | Système chargé avec succès', 'color: #1a5f7a; font-size: 14px; font-weight: bold;');
    
    initAnimations();
    initAutoAlerts();
    initDeleteConfirmation();
    initLiveSearch();
    initTooltips();
    initLazyLoading();
    initKeyboardShortcuts();
    initDarkMode();
    initFilters();
    initCartControls();
    initNotifications();
    initCharts();
    initFormValidation();
    initScrollToTop();
});

// ============================================
// 2. ANIMATIONS
// ============================================
function initAnimations() {
    const elements = document.querySelectorAll('.card, .alert, .table, .dashboard-widget');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('fade-in');
                }, index * 100);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    elements.forEach(el => observer.observe(el));
}

// ============================================
// 3. ALERTES AUTO-FERMANTES
// ============================================
function initAutoAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s, transform 0.3s';
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(20px)';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
}

// ============================================
// 4. CONFIRMATION DE SUPPRESSION
// ============================================
function initDeleteConfirmation() {
    const deleteForms = document.querySelectorAll('.delete-form, form[action*="supprimer"]');
    
    deleteForms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const confirmed = confirm('⚠️ Attention ! Êtes-vous sûr de vouloir supprimer cet élément ?\n\nCette action est irréversible.');
            if (!confirmed) {
                e.preventDefault();
            }
        });
    });
    
    const deleteButtons = document.querySelectorAll('.delete-btn, .btn-delete');
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            if (!confirm('⚠️ Confirmer la suppression ?')) {
                e.preventDefault();
            }
        });
    });
}

// ============================================
// 5. RECHERCHE EN DIRECT
// ============================================
function initLiveSearch() {
    const searchInput = document.querySelector('#live-search, .live-search, input[name="search"]');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function(e) {
            const query = e.target.value.toLowerCase();
            const items = document.querySelectorAll('.search-item, .product-item, .table tbody tr');
            
            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(query)) {
                    item.style.display = '';
                    item.style.animation = 'fadeIn 0.3s ease';
                } else {
                    item.style.display = 'none';
                }
            });
            
            // Afficher le nombre de résultats
            const visibleCount = Array.from(items).filter(i => i.style.display !== 'none').length;
            const resultInfo = document.querySelector('.search-result-count');
            if (resultInfo) {
                resultInfo.textContent = `${visibleCount} résultat(s) trouvé(s)`;
            }
        }, 300));
    }
}

// Debounce utility
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

// ============================================
// 6. TOOLTIPS
// ============================================
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip], [title]');
    
    tooltipElements.forEach(el => {
        const title = el.getAttribute('data-tooltip') || el.getAttribute('title');
        if (title && !el.hasAttribute('data-no-tooltip')) {
            el.removeAttribute('title');
            el.setAttribute('data-tooltip', title);
            
            el.addEventListener('mouseenter', showTooltip);
            el.addEventListener('mouseleave', hideTooltip);
        }
    });
}

let activeTooltip = null;

function showTooltip(e) {
    const text = e.target.getAttribute('data-tooltip');
    if (!text) return;
    
    hideTooltip();
    
    activeTooltip = document.createElement('div');
    activeTooltip.className = 'custom-tooltip';
    activeTooltip.textContent = text;
    activeTooltip.style.cssText = `
        position: fixed;
        background: linear-gradient(135deg, #2c3e50, #1a252f);
        color: white;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 12px;
        z-index: 10000;
        white-space: nowrap;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        pointer-events: none;
        animation: fadeIn 0.2s ease;
    `;
    
    document.body.appendChild(activeTooltip);
    
    const rect = e.target.getBoundingClientRect();
    activeTooltip.style.top = rect.top - 30 + window.scrollY + 'px';
    activeTooltip.style.left = rect.left + (rect.width / 2) - (activeTooltip.offsetWidth / 2) + 'px';
}

function hideTooltip() {
    if (activeTooltip) {
        activeTooltip.remove();
        activeTooltip = null;
    }
}

// ============================================
// 7. LAZY LOADING IMAGES
// ============================================
function initLazyLoading() {
    if ('loading' in HTMLImageElement.prototype) {
        const images = document.querySelectorAll('img:not([loading])');
        images.forEach(img => {
            img.loading = 'lazy';
        });
    } else {
        // Fallback for older browsers
        const lazyImages = document.querySelectorAll('img[data-src]');
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        });
        lazyImages.forEach(img => imageObserver.observe(img));
    }
}

// ============================================
// 8. RACCOURCIS CLAVIER
// ============================================
function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // F2 - Nouvelle vente / Reset
        if (e.key === 'F2') {
            e.preventDefault();
            const newSaleBtn = document.querySelector('#new-sale-btn, .btn-new-sale');
            if (newSaleBtn) newSaleBtn.click();
            else showNotification('Appuyez sur "Nouvelle vente"', 'info');
        }
        
        // F3 - Valider / Générer facture
        if (e.key === 'F3') {
            e.preventDefault();
            const validateBtn = document.querySelector('#validate-sale-btn, .btn-validate, button[type="submit"]');
            if (validateBtn) validateBtn.click();
        }
        
        // F5 - Rafraîchir les données
        if (e.key === 'F5') {
            e.preventDefault();
            showNotification('🔄 Rafraîchissement des données...', 'info');
            setTimeout(() => location.reload(), 500);
        }
        
        // Ctrl + S - Sauvegarder
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            const saveBtn = document.querySelector('#save-btn, button[type="submit"]');
            if (saveBtn) saveBtn.click();
        }
        
        // Ctrl + F - Focus recherche
        if (e.ctrlKey && e.key === 'f') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"], #searchInput, .search-input');
            if (searchInput) searchInput.focus();
        }
        
        // Esc - Fermer modals
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                const closeBtn = modal.querySelector('.btn-close, .close');
                if (closeBtn) closeBtn.click();
            });
        }
    });
}

// ============================================
// 9. DARK MODE
// ============================================
function initDarkMode() {
    const toggleBtn = document.querySelector('#dark-mode-toggle, .dark-mode-toggle');
    
    if (toggleBtn) {
        // Vérifier la préférence sauvegardée
        const darkMode = localStorage.getItem('darkMode') === 'true';
        if (darkMode) {
            document.body.classList.add('dark-mode');
            updateDarkModeIcon(true);
        }
        
        toggleBtn.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDark);
            updateDarkModeIcon(isDark);
            showNotification(`${isDark ? '🌙 Mode sombre' : '☀️ Mode clair'} activé`, 'success');
        });
    }
}

function updateDarkModeIcon(isDark) {
    const icon = document.querySelector('#dark-mode-toggle i, .dark-mode-toggle i');
    if (icon) {
        icon.className = isDark ? 'fas fa-sun' : 'fas fa-moon';
    }
}

// ============================================
// 10. FILTRES DYNAMIQUES
// ============================================
function initFilters() {
    const filterCheckboxes = document.querySelectorAll('.filter-checkbox, .category-filter');
    const priceRange = document.querySelector('#price-range');
    const priceValue = document.querySelector('#price-value');
    
    // Price range slider
    if (priceRange && priceValue) {
        priceRange.addEventListener('input', (e) => {
            priceValue.textContent = `${e.target.value} MAD`;
            applyFilters();
        });
    }
    
    // Checkbox filters
    filterCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => applyFilters());
    });
}

function applyFilters() {
    const activeFilters = Array.from(document.querySelectorAll('.filter-checkbox:checked'))
        .map(cb => cb.value);
    
    const maxPrice = document.querySelector('#price-range')?.value || Infinity;
    const products = document.querySelectorAll('.product-card, .product-item');
    
    products.forEach(product => {
        const category = product.dataset.category;
        const price = parseFloat(product.dataset.price) || Infinity;
        
        const categoryMatch = activeFilters.length === 0 || activeFilters.includes(category);
        const priceMatch = price <= maxPrice;
        
        if (categoryMatch && priceMatch) {
            product.style.display = '';
            product.style.animation = 'fadeIn 0.3s ease';
        } else {
            product.style.display = 'none';
        }
    });
    
    const visibleCount = Array.from(products).filter(p => p.style.display !== 'none').length;
    const filterInfo = document.querySelector('.filter-result-count');
    if (filterInfo) {
        filterInfo.textContent = `${visibleCount} produit(s) affiché(s)`;
    }
}

// ============================================
// 11. CONTROLES DU PANIER
// ============================================
function initCartControls() {
    const quantityBtns = document.querySelectorAll('.quantity-btn');
    
    quantityBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const action = btn.dataset.action;
            const productId = btn.dataset.productId;
            
            if (action === 'increase') {
                updateCartQuantity(productId, 1);
            } else if (action === 'decrease') {
                updateCartQuantity(productId, -1);
            }
        });
    });
}

function updateCartQuantity(productId, delta) {
    fetch(`/ventes/update-cart/${productId}/?delta=${delta}`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            showNotification(data.error || 'Erreur lors de la mise à jour', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Erreur de connexion', 'danger');
    });
}

function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
           document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
}

// ============================================
// 12. NOTIFICATIONS
// ============================================
function initNotifications() {
    // Auto-hide notifications after 5 seconds
    const notifications = document.querySelectorAll('.notification-toast');
    notifications.forEach(notif => {
        setTimeout(() => {
            notif.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notif.remove(), 300);
        }, 5000);
    });
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    const icons = {
        success: 'fa-check-circle',
        danger: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    notification.className = `alert alert-${type} notification-toast`;
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        max-width: 400px;
        animation: slideInRight 0.3s ease;
        box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        cursor: pointer;
    `;
    
    notification.innerHTML = `
        <i class="fas ${icons[type] || 'fa-bell'} me-2"></i>
        ${message}
        <button type="button" class="btn-close float-end" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
    
    // Click to dismiss
    notification.addEventListener('click', () => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    });
}

// ============================================
// 13. GRAPHIQUES (Dashboard)
// ============================================
function initCharts() {
    const chartCanvas = document.getElementById('ventesChart');
    
    if (chartCanvas && typeof Chart !== 'undefined') {
        const ctx = chartCanvas.getContext('2d');
        
        // Récupérer les données depuis les attributs data
        const labels = JSON.parse(chartCanvas.dataset.labels || '[]');
        const data = JSON.parse(chartCanvas.dataset.values || '[]');
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Chiffre d\'affaires (MAD)',
                    data: data,
                    backgroundColor: 'rgba(26, 95, 122, 0.2)',
                    borderColor: 'rgba(26, 95, 122, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(39, 174, 96, 1)',
                    pointBorderColor: '#fff',
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${context.raw} MAD`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value + ' MAD';
                            }
                        }
                    }
                }
            }
        });
    }
}

// ============================================
// 14. VALIDATION DE FORMULAIRES
// ============================================
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', (event) => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                showNotification('Veuillez remplir tous les champs obligatoires', 'warning');
            }
            form.classList.add('was-validated');
        });
    });
    
    // Validation en temps réel
    const inputs = document.querySelectorAll('input[required], select[required], textarea[required]');
    inputs.forEach(input => {
        input.addEventListener('blur', () => {
            if (input.value.trim() === '') {
                input.classList.add('is-invalid');
            } else {
                input.classList.remove('is-invalid');
                input.classList.add('is-valid');
            }
        });
    });
}

// ============================================
// 15. SCROLL TO TOP
// ============================================
function initScrollToTop() {
    const btn = document.querySelector('#scroll-to-top');
    
    if (!btn) {
        // Create button if not exists
        const scrollBtn = document.createElement('button');
        scrollBtn.id = 'scroll-to-top';
        scrollBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
        scrollBtn.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: linear-gradient(135deg, #1a5f7a, #2c8cae);
            color: white;
            border: none;
            cursor: pointer;
            display: none;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        `;
        document.body.appendChild(scrollBtn);
        
        scrollBtn.addEventListener('mouseenter', () => {
            scrollBtn.style.transform = 'translateY(-3px)';
            scrollBtn.style.boxShadow = '0 5px 20px rgba(0,0,0,0.3)';
        });
        
        scrollBtn.addEventListener('mouseleave', () => {
            scrollBtn.style.transform = 'translateY(0)';
        });
        
        scrollBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
        
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                scrollBtn.style.display = 'block';
            } else {
                scrollBtn.style.display = 'none';
            }
        });
    }
}

// ============================================
// 16. FORMATAGE DES PRIX
// ============================================
window.formatPrice = function(price) {
    return new Intl.NumberFormat('fr-MA', {
        style: 'currency',
        currency: 'MAD',
        minimumFractionDigits: 2
    }).format(price);
};

// ============================================
// 17. FORMATAGE DES DATES
// ============================================
window.formatDate = function(dateString, format = 'dd/mm/yyyy') {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString;
    
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    
    switch(format) {
        case 'dd/mm/yyyy':
            return `${day}/${month}/${year}`;
        case 'dd/mm/yyyy HH:MM':
            return `${day}/${month}/${year} ${hours}:${minutes}`;
        default:
            return `${day}/${month}/${year}`;
    }
};

// ============================================
// 18. EXPORT DE DONNEES
// ============================================
window.exportToCSV = function(data, filename = 'export.csv') {
    const csv = data.map(row => Object.values(row).join(';')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
};

// ============================================
// 19. PRINT FACTURE
// ============================================
window.printFacture = function(elementId) {
    const printContent = document.getElementById(elementId);
    if (printContent) {
        const originalContent = document.body.innerHTML;
        document.body.innerHTML = printContent.innerHTML;
        window.print();
        document.body.innerHTML = originalContent;
        location.reload();
    }
};

// ============================================
// 20. LOGS DE DEBUG
// ============================================
window.debug = function(message, data = null) {
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        if (data) {
            console.log(`[DEBUG] ${message}:`, data);
        } else {
            console.log(`[DEBUG] ${message}`);
        }
    }
};

// Initial debug
console.log('%c💊 Pharmacie H.I.B | Système de gestion de pharmacie', 'color: #1a5f7a; font-size: 14px; font-weight: bold;');
console.log('%c© 2026 - Tous droits réservés', 'color: #27ae60; font-size: 12px;');