document.addEventListener('DOMContentLoaded', function() {
    var sportSelect = document.getElementById('id_sport');
    var tournamentSelect = document.getElementById('id_tournament');
    var team1Select = document.getElementById('id_team1');
    var team2Select = document.getElementById('id_team2');
    
    if (sportSelect && team1Select && team2Select) {
        // Store all team options with their data-sport attributes
        function initializeTeamOptions() {
            // Add data-sport attribute to all team options if not present
            [team1Select, team2Select].forEach(function(select) {
                Array.from(select.options).forEach(function(option) {
                    if (option.value && !option.hasAttribute('data-sport')) {
                        // Extract sport from option text (format: "Team Name (Sport)")
                        var match = option.text.match(/\((.*?)\)/);
                        if (match && match[1]) {
                            option.setAttribute('data-sport', match[1].trim().toLowerCase());
                        }
                    }
                });
            });
        }
        
        // Initialize team options
        initializeTeamOptions();
        
        // Function to filter teams by sport
        function filterTeamsBySport(sport) {
            var sportLower = sport ? sport.toLowerCase() : '';
            
            // Filter team1 options
            var team1Options = Array.from(team1Select.options);
            team1Select.innerHTML = '';
            team1Options.forEach(function(option) {
                if (option.value === '') {
                    // Keep the empty option (usually "-- Select --")
                    team1Select.appendChild(option.cloneNode(true));
                } else if (!sportLower || option.getAttribute('data-sport') === sportLower) {
                    team1Select.appendChild(option.cloneNode(true));
                }
            });
            
            // Filter team2 options
            var team2Options = Array.from(team2Select.options);
            team2Select.innerHTML = '';
            team2Options.forEach(function(option) {
                if (option.value === '') {
                    // Keep the empty option (usually "-- Select --")
                    team2Select.appendChild(option.cloneNode(true));
                } else if (!sportLower || option.getAttribute('data-sport') === sportLower) {
                    team2Select.appendChild(option.cloneNode(true));
                }
            });
        }
        
        // Function to filter tournaments by sport
        function filterTournamentsBySport(sport) {
            if (!tournamentSelect) return;
            
            var sportLower = sport ? sport.toLowerCase() : '';
            var tournamentOptions = Array.from(tournamentSelect.options);
            tournamentSelect.innerHTML = '';
            
            tournamentOptions.forEach(function(option) {
                if (option.value === '') {
                    // Keep the empty option
                    tournamentSelect.appendChild(option.cloneNode(true));
                } else if (!sportLower || option.getAttribute('data-sport') === sportLower) {
                    tournamentSelect.appendChild(option.cloneNode(true));
                }
            });
        }
        
        // Add data-sport attribute to tournament options
        if (tournamentSelect) {
            Array.from(tournamentSelect.options).forEach(function(option) {
                if (option.value && !option.hasAttribute('data-sport')) {
                    var match = option.text.match(/\((.*?)\)/);
                    if (match && match[1]) {
                        option.setAttribute('data-sport', match[1].trim().toLowerCase());
                    }
                }
            });
        }
        
        // Add change event listener to sport field
        sportSelect.addEventListener('change', function() {
            var sport = this.value;
            filterTeamsBySport(sport);
            filterTournamentsBySport(sport);
        });
        
        // Add change event listener to tournament field
        if (tournamentSelect) {
            tournamentSelect.addEventListener('change', function() {
                var tournamentId = this.value;
                if (tournamentId) {
                    var selectedOption = this.options[this.selectedIndex];
                    if (selectedOption && selectedOption.hasAttribute('data-sport')) {
                        var sport = selectedOption.getAttribute('data-sport');
                        if (sportSelect.value !== sport) {
                            sportSelect.value = sport;
                            filterTeamsBySport(sport);
                            filterTournamentsBySport(sport);
                        }
                    }
                }
            });
        }
        
        // Initial filter based on selected sport
        filterTeamsBySport(sportSelect.value);
        filterTournamentsBySport(sportSelect.value);
    }
});