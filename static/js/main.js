// Main JavaScript for PDF to Coloring Book Converter
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Feather Icons
    feather.replace();
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Form validation helpers
    window.validateForm = function(formId) {
        const form = document.getElementById(formId);
        if (!form) return true;
        
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;
        
        inputs.forEach(function(input) {
            if (!input.value.trim()) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    };
    
    // File size formatter
    window.formatFileSize = function(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };
    
    // Loading spinner utility
    window.showLoading = function(button, text = 'Loading...') {
        const originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            ${text}
        `;
        
        return function() {
            button.disabled = false;
            button.innerHTML = originalText;
            feather.replace();
        };
    };
    
    // Copy to clipboard utility
    window.copyToClipboard = function(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(function() {
                showToast('Copied to clipboard!', 'success');
            }).catch(function() {
                fallbackCopyToClipboard(text);
            });
        } else {
            fallbackCopyToClipboard(text);
        }
    };
    
    function fallbackCopyToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            showToast('Copied to clipboard!', 'success');
        } catch (err) {
            showToast('Failed to copy to clipboard', 'error');
        }
        
        document.body.removeChild(textArea);
    }
    
    // Toast notification utility
    window.showToast = function(message, type = 'info') {
        // Remove existing toasts
        const existingToasts = document.querySelectorAll('.toast-container .toast');
        existingToasts.forEach(toast => toast.remove());
        
        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '1055';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast element
        const toastId = 'toast-' + Date.now();
        const iconMap = {
            'success': 'check-circle',
            'error': 'x-circle',
            'warning': 'alert-triangle',
            'info': 'info'
        };
        
        const colorMap = {
            'success': 'text-success',
            'error': 'text-danger',
            'warning': 'text-warning',
            'info': 'text-info'
        };
        
        const toastHtml = `
            <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header">
                    <i data-feather="${iconMap[type] || 'info'}" class="${colorMap[type] || 'text-info'} me-2"></i>
                    <strong class="me-auto">Notification</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        // Initialize and show toast
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: 5000
        });
        
        feather.replace();
        toast.show();
        
        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', function() {
            toastElement.remove();
        });
    };
    
    // Confirmation dialog utility
    window.confirmAction = function(message, callback, title = 'Confirm Action') {
        if (confirm(`${title}\n\n${message}`)) {
            callback();
        }
    };
    
    // Progress bar utility
    window.updateProgress = function(progressBarId, percentage, text = '') {
        const progressBar = document.getElementById(progressBarId);
        if (progressBar) {
            progressBar.style.width = percentage + '%';
            progressBar.setAttribute('aria-valuenow', percentage);
            if (text) {
                progressBar.textContent = text;
            }
        }
    };
    
    // Smooth scroll to element
    window.scrollToElement = function(elementId, offset = 0) {
        const element = document.getElementById(elementId);
        if (element) {
            const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
            const offsetPosition = elementPosition - offset;
            
            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        }
    };
    
    // Handle navigation active states
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Auto-refresh page elements (for activity status updates)
    if (window.location.pathname.includes('/dashboard')) {
        // Refresh dashboard every 30 seconds to update processing status
        setInterval(function() {
            const badges = document.querySelectorAll('tr .badge');
            const hasProcessing = Array.from(badges).some(function(badge) {
                return badge.textContent.trim() === 'Processing';
            });
            if (hasProcessing) {
                location.reload();
            }
        }, 30000);
    }
    
    // Enhanced file drag and drop functionality
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        const container = input.closest('.card, .form-group, .mb-3') || input.parentElement;
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            container.addEventListener(eventName, preventDefaults, false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            container.addEventListener(eventName, function() {
                container.classList.add('drag-over');
            }, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            container.addEventListener(eventName, function() {
                container.classList.remove('drag-over');
            }, false);
        });
        
        container.addEventListener('drop', function(e) {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
                
                // Trigger change event
                const changeEvent = new Event('change', { bubbles: true });
                input.dispatchEvent(changeEvent);
            }
        }, false);
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
    });
    
    // Enhanced Progress Tracking for PDF Conversion
    function initializeProgressTracking() {
        const form = document.getElementById('convertForm');
        if (!form) return;
        
        form.addEventListener('submit', function(e) {
            const fileInput = document.getElementById('pdf');
            const file = fileInput.files[0];
            
            if (!file) {
                e.preventDefault();
                alert('Please select a PDF file first.');
                return;
            }
            
            // Generate session ID and store it
            const sessionId = generateSessionId();
            const sessionField = document.getElementById('sessionIdField');
            if (sessionField) sessionField.value = sessionId;
            
            // Store in global variable for progress tracking
            window.currentSessionId = sessionId;
            
            // Show processing modal immediately
            const modal = new bootstrap.Modal(document.getElementById('processingModal'));
            modal.show();
            
            // Start progress simulation
            simulateProgress();
        });
    }
    
    function simulateProgress() {
        const progressBar = document.getElementById('progressBar');
        const statusTitle = document.getElementById('statusTitle');
        const statusMessage = document.getElementById('statusMessage');
        const currentStep = document.getElementById('currentStep');
        
        if (!progressBar) return;
        
        // Initial upload simulation
        const initialSteps = [
            { percent: 10, title: "Uploading PDF...", message: "Transferring your file to our servers...", step: "Processing file upload..." },
            { percent: 25, title: "Analyzing PDF Structure...", message: "Reading pages and extracting content...", step: "Scanning PDF pages..." },
        ];
        
        let currentStepIndex = 0;
        
        const updateInitialProgress = () => {
            if (currentStepIndex < initialSteps.length) {
                const step = initialSteps[currentStepIndex];
                
                progressBar.style.width = step.percent + '%';
                progressBar.setAttribute('aria-valuenow', step.percent);
                
                if (statusTitle) statusTitle.textContent = step.title;
                if (statusMessage) statusMessage.textContent = step.message;
                if (currentStep) currentStep.textContent = step.step;
                
                currentStepIndex++;
                setTimeout(updateInitialProgress, 2000);
            } else {
                // Switch to real-time progress tracking
                startRealTimeProgress();
            }
        };
        
        updateInitialProgress();
    }
    
    function startRealTimeProgress() {
        const progressBar = document.getElementById('progressBar');
        const statusTitle = document.getElementById('statusTitle');
        const statusMessage = document.getElementById('statusMessage');
        const currentStep = document.getElementById('currentStep');
        const fileProgressContainer = document.getElementById('fileProgressContainer');
        const fileProgressList = document.getElementById('fileProgressList');
        const detailedProgress = document.getElementById('detailedProgress');
        const currentPageNum = document.getElementById('currentPageNum');
        const totalPagesNum = document.getElementById('totalPagesNum');
        const completedFilesNum = document.getElementById('completedFilesNum');
        
        // Show detailed progress sections
        if (fileProgressContainer) fileProgressContainer.style.display = 'block';
        if (detailedProgress) detailedProgress.style.display = 'block';
        
        // Use stored session ID
        const sessionId = window.currentSessionId || generateSessionId();
        
        // Poll for real-time progress
        const pollProgress = () => {
            fetch(`/convert/progress/${sessionId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        // Fall back to simulation if no real progress found
                        setTimeout(pollProgress, 2000);
                        return;
                    }
                    
                    // Update progress bar
                    const progress = Math.round((data.current_page / data.total_pages) * 80) + 20; // 20-100%
                    progressBar.style.width = progress + '%';
                    
                    // Update status
                    if (statusTitle) statusTitle.textContent = `Processing Page ${data.current_page} of ${data.total_pages}`;
                    if (statusMessage) statusMessage.textContent = data.status;
                    if (currentStep) currentStep.textContent = data.status;
                    
                    // Update counters
                    if (currentPageNum) currentPageNum.textContent = data.current_page;
                    if (totalPagesNum) totalPagesNum.textContent = data.total_pages;
                    if (completedFilesNum) completedFilesNum.textContent = data.completed_files.length;
                    
                    // Update file list
                    if (fileProgressList && data.completed_files.length > 0) {
                        fileProgressList.innerHTML = '';
                        data.completed_files.forEach(file => {
                            const fileItem = document.createElement('div');
                            fileItem.className = 'list-group-item list-group-item-success d-flex align-items-center';
                            fileItem.innerHTML = `
                                <i data-feather="check-circle" class="text-success me-2"></i>
                                <span>${file}</span>
                            `;
                            fileProgressList.appendChild(fileItem);
                        });
                        feather.replace();
                    }
                    
                    // Continue polling if not completed
                    if (data.step !== 'completed') {
                        setTimeout(pollProgress, 1000);
                    } else {
                        // Completion
                        progressBar.style.width = '100%';
                        if (statusTitle) statusTitle.textContent = 'Conversion Complete!';
                        if (statusMessage) statusMessage.textContent = 'Your coloring book is ready for download.';
                        if (currentStep) currentStep.textContent = 'Processing finished successfully!';
                    }
                })
                .catch(error => {
                    console.log('Progress polling error:', error);
                    setTimeout(pollProgress, 2000);
                });
        };
        
        // Start polling after short delay
        setTimeout(pollProgress, 3000);
    }
    
    function generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    function initializeUploadTypeToggle() {
        const pdfType = document.getElementById('pdf_type');
        const imageType = document.getElementById('image_type');
        const pdfSection = document.getElementById('pdfUploadSection');
        const imageSection = document.getElementById('imageUploadSection');
        
        if (!pdfType || !imageType) return;
        
        pdfType.addEventListener('change', function() {
            if (this.checked) {
                pdfSection.style.display = 'block';
                imageSection.style.display = 'none';
                // Clear image files when switching to PDF
                const imageInput = document.getElementById('images');
                if (imageInput) {
                    imageInput.value = '';
                    imageInput.required = false;
                }
                // Make PDF required and ensure it has proper accept attribute
                const pdfInput = document.getElementById('pdf');
                if (pdfInput) {
                    pdfInput.required = true;
                    pdfInput.setAttribute('accept', 'application/pdf,.pdf');
                }
            }
        });
        
        imageType.addEventListener('change', function() {
            if (this.checked) {
                pdfSection.style.display = 'none';
                imageSection.style.display = 'block';
                // Clear PDF file when switching to images
                const pdfInput = document.getElementById('pdf');
                if (pdfInput) {
                    pdfInput.value = '';
                    pdfInput.required = false;
                }
                // Make images required when image mode is selected
                const imageInput = document.getElementById('images');
                if (imageInput) {
                    imageInput.required = true;
                    // Force browser to refresh file input by recreating it
                    const parent = imageInput.parentNode;
                    const newInput = imageInput.cloneNode(true);
                    newInput.setAttribute('accept', 'image/*,.jpg,.jpeg,.png,.gif,.bmp,.tiff,.tif,.webp,.svg,.psd');
                    parent.replaceChild(newInput, imageInput);
                }
            }
        });
    }

    // Initialize progress tracking when page loads
    initializeProgressTracking();
    initializeUploadTypeToggle();
    
    console.log('PDF to Coloring Book Converter - JavaScript initialized');
});

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    // In production, you might want to send this to an error tracking service
});

// Handle network errors
window.addEventListener('online', function() {
    showToast('Connection restored', 'success');
});

window.addEventListener('offline', function() {
    showToast('Connection lost. Please check your internet connection.', 'warning');
});
