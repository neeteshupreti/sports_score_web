document.addEventListener('DOMContentLoaded', function() {
    var sportSelect = document.getElementById('id_sport');
    var team1Select = document.getElementById('id_team1');
    var team2Select = document.getElementById('id_team2');
    
    if (sportSelect && team1Select && team2Select) {
        // Store all team options with their sports
        var teamSports = {};
        
        // Extract sport information from team options
        function extractSportsFromOptions() {
            [team1Select, team2Select].forEach(function(select) {
                Array.from(select.options).forEach(function(option) {
                    if (option.value && option.text.includes('(') && option.text.includes(')')) {
                        var sport = option.text.split('(').pop().split(')')[0].trim();
                        teamSports[option.value] = sport.toLowerCase();
                    }
                });
            });
        }
        
        // Extract sports initially
        extractSportsFromOptions();
        
        // Function to filter teams by sport
        function filterTeamsBySport(sport) {
            var sportLower = sport ? sport.toLowerCase() : '';
            
            // Filter team options
            [team1Select, team2Select].forEach(function(select) {
                var options = Array.from(select.options);
                select.innerHTML = '';
                
                options.forEach(function(option) {
                    if (option.value === '' || !sportLower || 
                        (teamSports[option.value] && teamSports[option.value] === sportLower)) {
                        select.appendChild(option.cloneNode(true));
                    }
                });
            });
        }
        
        // Add change event listener to sport field
        sportSelect.addEventListener('change', function() {
            filterTeamsBySport(this.value);
        });
        
        // Initial filter based on selected sport
        filterTeamsBySport(sportSelect.value);
    }
});