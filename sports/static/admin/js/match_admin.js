// Function to update team options based on selected sport
function updateTeamOptions() {
    const sportSelect = document.getElementById('id_sport');
    const team1Select = document.getElementById('id_team1');
    const team2Select = document.getElementById('id_team2');
    
    if (sportSelect && team1Select && team2Select) {
        // Add event listener to sport select
        sportSelect.addEventListener('change', function() {
            const sport = this.value;
            
            if (sport) {
                // Fetch teams for the selected sport
                fetch(`/admin/sports/team/?sport=${sport}`)
                    .then(response => response.json())
                    .then(data => {
                        // Update team1 options
                        team1Select.innerHTML = '';
                        data.teams.forEach(team => {
                            const option = document.createElement('option');
                            option.value = team.id;
                            option.textContent = team.name;
                            team1Select.appendChild(option);
                        });
                        
                        // Update team2 options
                        team2Select.innerHTML = '';
                        data.teams.forEach(team => {
                            const option = document.createElement('option');
                            option.value = team.id;
                            option.textContent = team.name;
                            team2Select.appendChild(option);
                        });
                    })
                    .catch(error => console.error('Error:', error));
            } else {
                // Clear teams if no sport selected
                team1Select.innerHTML = '';
                team2Select.innerHTML = '';
            }
        });
        
        // Trigger change event if sport is already selected
        if (sportSelect.value) {
            sportSelect.dispatchEvent(new Event('change'));
        }
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    updateTeamOptions();
});