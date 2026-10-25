// Auto-hide messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelector('.messages');
    if (messages) {
        setTimeout(function() {
            messages.style.opacity = '0';
            messages.style.transition = 'opacity 0.5s ease';
            setTimeout(function() {
                messages.style.display = 'none';
            }, 500);
        }, 5000);
    }
    
    console.log('KhelStats loaded successfully!');
});

// Search page functionality
document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling to results when filters change
    const filterSelects = document.querySelectorAll('.filter-group select');
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            // Scroll to results section with smooth animation
            document.querySelector('.search-results').scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        });
    });
    
    // Preserve filter values when page reloads
    const urlParams = new URLSearchParams(window.location.search);
    const query = urlParams.get('q');
    const type = urlParams.get('type');
    const status = urlParams.get('status');
    
    // Update page title with search query
    if (query) {
        document.title = `"${query}" - Search Results | KhelStats`;
    }
});

// Profile page functionality
document.addEventListener('DOMContentLoaded', function() {
    // Select all checkboxes when selecting a sport
    const sportCheckboxes = document.querySelectorAll('input[name="favorite_sports"]');
    sportCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const sport = this.value;
            const dropdown = document.getElementById(`${sport}-dropdown`);
            
            if (this.checked && dropdown) {
                dropdown.style.display = 'block';
            } else if (dropdown) {
                dropdown.style.display = 'none';
                
                // Unselect all teams for this sport when sport is deselected
                const teamCheckboxes = dropdown.querySelectorAll('input[name="favorite_teams"]');
                teamCheckboxes.forEach(teamCheckbox => {
                    teamCheckbox.checked = false;
                });
            }
        });
    });
    
    // Select all teams in a category
    function selectAllTeams(sport) {
        const checkboxes = document.querySelectorAll(`#${sport}-teams input[name="favorite_teams"]`);
        checkboxes.forEach(checkbox => {
            checkbox.checked = true;
        });
    }
    
    // Deselect all teams in a category
    function deselectAllTeams(sport) {
        const checkboxes = document.querySelectorAll(`#${sport}-teams input[name="favorite_teams"]`);
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        });
    }
    
    // Add select all/deselect all buttons to each dropdown
    const dropdowns = document.querySelectorAll('.dropdown-content');
    dropdowns.forEach(dropdown => {
        const sport = dropdown.id.split('-')[0];
        const selectAllBtn = document.createElement('button');
        selectAllBtn.type = 'button';
        selectAllBtn.textContent = 'Select All';
        selectAllBtn.className = 'select-all-btn';
        selectAllBtn.onclick = () => selectAllTeams(sport);
        
        const deselectAllBtn = document.createElement('button');
        deselectAllBtn.type = 'button';
        deselectAllBtn.textContent = 'Deselect All';
        deselectAllBtn.className = 'deselect-all-btn';
        deselectAllBtn.onclick = () => deselectAllTeams(sport);
        
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'dropdown-buttons';
        buttonContainer.style.marginTop = '15px';
        buttonContainer.style.display = 'flex';
        buttonContainer.style.gap = '10px';
        
        buttonContainer.appendChild(selectAllBtn);
        buttonContainer.appendChild(deselectAllBtn);
        dropdown.appendChild(buttonContainer);
    });
});

// Add these styles for the buttons
const style = document.createElement('style');
style.textContent = `
.select-all-btn, .deselect-all-btn {
    padding: 6px 12px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    font-weight: bold;
}

.select-all-btn {
    background-color: #30E998;
    color: white;
}

.select-all-btn:hover {
    background-color: #28c47f;
}

.deselect-all-btn {
    background-color: #EF4840;
    color: white;
}

.deselect-all-btn:hover {
    background-color: #d43c35;
}
`;
document.head.appendChild(style);

// Mobile header hide/show on scroll - Optimized for new layout
document.addEventListener('DOMContentLoaded', function() {
    const header = document.querySelector('header');
    let lastScrollY = window.scrollY;
    
    // Check if mobile device
    function isMobile() {
        return window.innerWidth <= 768;
    }
    
    // Header scroll behavior
    if (isMobile() && header) {
        let scrollTimeout;
        
        window.addEventListener('scroll', function() {
            if (!isMobile()) return;
            
            clearTimeout(scrollTimeout);
            
            if (window.scrollY > lastScrollY && window.scrollY > 50) {
                // Scroll down - hide header
                header.classList.add('hidden');
            } else {
                // Scroll up - show header
                header.classList.remove('hidden');
            }
            
            lastScrollY = window.scrollY;
            
            // Auto-show header after stopping scroll
            scrollTimeout = setTimeout(function() {
                header.classList.remove('hidden');
            }, 1500);
        });
    }
    
    // Touch events for mobile
    let touchStartY = 0;
    
    document.addEventListener('touchstart', function(e) {
        if (!isMobile()) return;
        touchStartY = e.touches[0].clientY;
    });
    
    document.addEventListener('touchmove', function(e) {
        if (!isMobile()) return;
        
        const touchY = e.touches[0].clientY;
        const diff = touchStartY - touchY;
        
        if (diff > 15 && window.scrollY > 50) {
            // Swiping down significantly
            header.classList.add('hidden');
        } else if (diff < -15) {
            // Swiping up
            header.classList.remove('hidden');
        }
    });
    
    // Re-check on window resize
    window.addEventListener('resize', function() {
        if (!isMobile()) {
            header.classList.remove('hidden');
        }
    });
    
    // Prevent zoom on search input focus (optional)
    const searchInput = document.querySelector('.search-bar input');
    if (searchInput && isMobile()) {
        searchInput.addEventListener('focus', function() {
            header.classList.remove('hidden');
        });
    }
});

// --- Series Filter Popup Functionality ---
document.addEventListener('DOMContentLoaded', function() {
    const filterToggle = document.getElementById('filter-toggle');
    const filterPopup = document.getElementById('filter-popup');
    const closePopup = document.getElementById('close-popup');
    const clearFiltersBtn = document.getElementById('clear-filters-btn');
    const filterForm = document.getElementById('series-filter-form');

    if (filterToggle && filterPopup && closePopup && clearFiltersBtn && filterForm) {
        
        // Function to open the popup
        function openPopup() {
            filterPopup.style.display = 'block';
            document.body.style.overflow = 'hidden'; // Prevent background scroll
        }

        // Function to close the popup
        function closePopupFunc() {
            filterPopup.style.display = 'none';
            document.body.style.overflow = ''; // Restore background scroll
        }

        // Open popup when filter button is clicked
        filterToggle.addEventListener('click', openPopup);

        // Close popup when 'x' is clicked
        closePopup.addEventListener('click', closePopupFunc);

        // Close popup when clicking outside the content
        filterPopup.addEventListener('click', function(event) {
            if (event.target === filterPopup) {
                closePopupFunc();
            }
        });

        // Clear filters
        clearFiltersBtn.addEventListener('click', function() {
            // Reset form fields
            filterForm.reset();
            // Submit the form to reload the page without filters
            filterForm.submit();
        });

        // Optional: Close popup on pressing Escape key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape' && filterPopup.style.display === 'block') {
                closePopupFunc();
            }
        });
    }
});
// --- End of Series Filter Popup Functionality ---

// ... (rest of existing JavaScript code) ...

// --- Live Matches Horizontal Scroll with Arrows ---
document.addEventListener('DOMContentLoaded', function () {
    const liveMatchesSection = document.querySelector('.live-matches-section');
    if (!liveMatchesSection) return; // Exit if section not found

    const scrollContainer = liveMatchesSection.querySelector('.live-matches-scroll-container');
    const grid = liveMatchesSection.querySelector('.live-matches-grid');
    const leftArrow = liveMatchesSection.querySelector('.nav-arrow-left');
    const rightArrow = liveMatchesSection.querySelector('.nav-arrow-right');

    // Check if all necessary elements are present
    if (!scrollContainer || !grid || !leftArrow || !rightArrow) {
        console.warn("Live matches scroll elements not found.");
        return;
    }

    // Show arrows only if content overflows
    function updateArrowsVisibility() {
        const isOverflowing = scrollContainer.scrollWidth > scrollContainer.clientWidth;
        if (isOverflowing) {
            leftArrow.style.display = 'flex'; // Use flex to match CSS
            rightArrow.style.display = 'flex';
            updateArrowStates(); // Also update disabled states
        } else {
            leftArrow.style.display = 'none';
            rightArrow.style.display = 'none';
        }
    }

    // Update arrow disabled states based on scroll position
    function updateArrowStates() {
        // Check if scrolled to the beginning (disable left arrow)
        if (scrollContainer.scrollLeft <= 0) {
            leftArrow.disabled = true;
        } else {
            leftArrow.disabled = false;
        }

        // Check if scrolled to the end (disable right arrow)
        // Use a small tolerance for floating point inaccuracies
        const tolerance = 1;
        if (scrollContainer.scrollLeft + scrollContainer.clientWidth >= scrollContainer.scrollWidth - tolerance) {
            rightArrow.disabled = true;
        } else {
            rightArrow.disabled = false;
        }
    }

    // Scroll function
    function scrollGrid(direction) {
        const scrollAmount = 320; // Adjust based on card width + gap
        const behavior = 'smooth'; // For smooth scrolling

        if (direction === 'left') {
            scrollContainer.scrollBy({ left: -scrollAmount, behavior });
        } else if (direction === 'right') {
            scrollContainer.scrollBy({ left: scrollAmount, behavior });
        }
    }

    // Event Listeners
    leftArrow.addEventListener('click', () => scrollGrid('left'));
    rightArrow.addEventListener('click', () => scrollGrid('right'));

    // Update arrows on scroll
    scrollContainer.addEventListener('scroll', updateArrowStates);

    // Update arrows on window resize (layout might change)
    window.addEventListener('resize', updateArrowsVisibility);

    // Initial check
    // Use setTimeout to ensure layout is settled, especially if content is loaded dynamically
    setTimeout(() => {
        updateArrowsVisibility();
    }, 100);

    // Optional: If you remove the display:none from CSS arrows, uncomment this:
    // updateArrowsVisibility();

});
// --- End of Live Matches Horizontal Scroll with Arrows ---