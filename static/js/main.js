// Main JavaScript for Ticket Reservation System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Seat selection functionality
    initializeSeatSelection();
    
    // Payment method selection
    initializePaymentMethods();
    
    // Form validation
    initializeFormValidation();
    
    // Auto-dismiss alerts
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

function initializeSeatSelection() {
    // Skip if seat map page is active
    if (window.seatMapPageActive) {
        console.log('Skipping main.js seat selection - seat map page active');
        return;
    }

    const seats = document.querySelectorAll('.seat.available');
    const selectedSeats = [];
    const maxSeats = 6; // Maximum seats per booking
    
    seats.forEach(seat => {
        seat.addEventListener('click', function() {
            const seatId = this.dataset.seatId;
            
            if (this.classList.contains('selected')) {
                // Deselect seat
                this.classList.remove('selected');
                const index = selectedSeats.indexOf(seatId);
                if (index > -1) {
                    selectedSeats.splice(index, 1);
                }
            } else if (selectedSeats.length < maxSeats) {
                // Select seat
                this.classList.add('selected');
                selectedSeats.push(seatId);
            } else {
                alert(`You can select maximum ${maxSeats} seats.`);
            }
            
            updateSelectedSeatsDisplay();
        });
    });
    
    function updateSelectedSeatsDisplay() {
        const selectedSeatsContainer = document.getElementById('selected-seats');
        const continueBtn = document.getElementById('continue-booking');
        
        if (selectedSeatsContainer) {
            selectedSeatsContainer.innerHTML = '';
            
            selectedSeats.forEach(seatId => {
                const seat = document.querySelector(`[data-seat-id="${seatId}"]`);
                const seatNumber = seat.textContent;
                const seatType = seat.dataset.seatType;
                
                const seatInfo = document.createElement('div');
                seatInfo.className = 'badge bg-primary me-2 mb-2';
                seatInfo.innerHTML = `Seat ${seatNumber} (${seatType})`;
                selectedSeatsContainer.appendChild(seatInfo);
            });
        }
        
        if (continueBtn) {
            continueBtn.disabled = selectedSeats.length === 0;
            continueBtn.onclick = function() {
                proceedToBooking(selectedSeats);
            };
        }
    }
}

function proceedToBooking(selectedSeats) {
    const scheduleId = document.getElementById('schedule-id').value;
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/bookings/create/';
    
    // Add CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrfToken;
    form.appendChild(csrfInput);
    
    // Add schedule ID
    const scheduleInput = document.createElement('input');
    scheduleInput.type = 'hidden';
    scheduleInput.name = 'schedule_id';
    scheduleInput.value = scheduleId;
    form.appendChild(scheduleInput);
    
    // Add selected seats
    selectedSeats.forEach(seatId => {
        const seatInput = document.createElement('input');
        seatInput.type = 'hidden';
        seatInput.name = 'seat_ids';
        seatInput.value = seatId;
        form.appendChild(seatInput);
    });
    
    document.body.appendChild(form);
    form.submit();
}

function initializePaymentMethods() {
    const paymentCards = document.querySelectorAll('.payment-method-card');
    const paymentMethodInput = document.getElementById('payment-method-input');
    
    if (paymentCards.length && paymentMethodInput) {
        paymentCards.forEach(card => {
            card.addEventListener('click', function() {
                // Remove active class from all cards
                paymentCards.forEach(c => c.classList.remove('active'));
                
                // Add active class to selected card
                this.classList.add('active');
                
                // Set the value of the hidden input
                paymentMethodInput.value = this.dataset.method;
            });
        });
    }
}

function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        });
    });
}

// Search form enhancements
function initializeSearchForm() {
    const originInput = document.getElementById('origin');
    const destinationInput = document.getElementById('destination');
    const departureDateInput = document.getElementById('departure_date');
    
    // Set minimum date to today
    if (departureDateInput) {
        const today = new Date().toISOString().split('T')[0];
        departureDateInput.min = today;
    }
    
    // Swap origin and destination
    const swapBtn = document.getElementById('swap-locations');
    if (swapBtn) {
        swapBtn.addEventListener('click', function() {
            const temp = originInput.value;
            originInput.value = destinationInput.value;
            destinationInput.value = temp;
        });
    }
}

// Loading spinner
function showLoading() {
    const spinner = document.querySelector('.loading-spinner');
    if (spinner) {
        spinner.style.display = 'block';
    }
}

function hideLoading() {
    const spinner = document.querySelector('.loading-spinner');
    if (spinner) {
        spinner.style.display = 'none';
    }
}

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatTime(timeString) {
    const time = new Date(`2000-01-01T${timeString}`);
    return time.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

