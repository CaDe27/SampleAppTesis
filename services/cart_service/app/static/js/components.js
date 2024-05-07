
function updateSearchComponent(){
    $('#searchBarContainer').addClass('d-none'); // Hide the search bar by default on change
    $('#genreInputsContainer').empty(); // Clear the genre container

    if (this.id === 'genre' || this.id === 'genre-rating') {
        // Make the genre container visible
        $('#genresContainer').removeClass('d-none');
        
        // Define your genres or labels
        const genres = ["Action", "Comedy", "Drama", "Fantasy", "Horror", "Mystery", "Romance", "Thriller", "Western", "Sci-Fi", "Documentary", "Biography", "Musical", "Animation"];

        genres.forEach(genre => {
            if(this.id === 'genre-rating'){
                const inputGroupHtml = `
                        
                    <div class="col-6 col-md-4 col-lg-3 col-xl-2 mb-2">
                        <div class="input-group">
                            <div class="input-group-prepend">
                                <span class="input-group-text" id="${genre}-addon">${genre}</span>
                            </div>
                            <input type="number" class="form-control" placeholder="0" min="0" max="5" step="0.5" aria-label="${genre}" aria-describedby="${genre}-addon">
                        </div>
                    </div>
                `;
                $('#genreInputsContainer').append(inputGroupHtml);
            }
            else{
                const inputGroupHtml = `
                    <div class="col-6 col-md-4 col-lg-3 col-xl-2 mb-2">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="${genre}" name="genre[]" value="${genre}" aria-label="${genre}">
                            <label class="form-check-label" for="${genre}">
                                ${genre}
                            </label>
                        </div>
                    </div>
                `;
                $('#genreInputsContainer').append(inputGroupHtml);
            }
        });
    } else if (this.id === 'movie') {
        // Show the search bar only if 'movie' is selected
        $('#searchBarContainer').removeClass('d-none');
        $('#genresContainer').addClass('d-none');
    }
}

function showMovies(movies){
    const moviesGrid = document.getElementById('moviesGrid'); 
    // Insert each movie into the grid
    movies.forEach(movie => {
        moviesGrid.innerHTML += createMovieCard(movie);
    });
}
function getExampleMovies(){
    // Example movie data
    const movies = [
        {
            title: "Example Movie 1",
            imageUrl: "./../product_catalog_service/movie_images/4054.jpg",
            price: "10.99",
            rating: "★★★★☆",
            year: "2020"
        },
        {
            title: "Example Movie 2",
            imageUrl: "./../../product_catalog_service/movie_images/4054.jpg",
            price: "12.99",
            rating: "★★★☆☆",
            year: "2021"
        }
        // Add more movies as needed
    ];
    return movies;
}

function createMovieCard(movie) {
    return `
        <div class="col-12 col-sm-6 col-md-4 mb-4">
            <div class="card">
                <img src="${movie.imageUrl}" class="card-img-top" alt="${movie.title}">
                <div class="card-body">
                    <h5 class="card-title">${movie.title}</h5>
                    <p class="card-text">Price: $${movie.price}</p>
                    <p class="card-text">Average Rating: ${movie.rating}</p>
                    <p class="card-text">Release Year: ${movie.year}</p>
                </div>
            </div>
        </div>
    `;
}
