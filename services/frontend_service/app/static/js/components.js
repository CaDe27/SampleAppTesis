
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
    moviesGrid.innerHTML = ''
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
    const formattedRating = Number(movie.avg_rating).toFixed(2);
    return `
        <div class="col-12 col-sm-6 col-md-4 mb-4">
            <div class="card" style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
                <img src="${movie.movie_url}" class="card-img-top" style="width: 200px; height: 300px; object-fit: cover; display: block; margin: auto;" alt="${movie.title}">
                <div class="card-body">
                    <h5 class="card-title">${movie.title}</h5>
                    <p class="card-text">Price: $${(Math.round(movie.price_USD * 100) / 100).toFixed(2)}</p>
                    <p class="card-text">Average Rating: ${formattedRating}/5</p>
                    <p class="card-text">Release Year: ${movie.release_date}</p>
                    <div class="quantity-controls" data-movie-id="${movie.movieId}">
                        <button class="decrease-quantity btn btn-outline-secondary btn-sm">-</button>
                        <span class="quantity-display">${parseInt(movie.movieId) in cartQuantities? cartQuantities[parseInt(movie.movieId)] : 0}</span>
                        <button class="increase-quantity btn btn-outline-secondary btn-sm">+</button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function updateCartDisplay(cart) {
    const cartItemsContainer = document.getElementById('cartItems');
    cartItemsContainer.innerHTML = ''; // Clear current cart items

    // Create a <ul> element to hold list of cart items
    const list = document.createElement('ul');
    list.className = 'cart-items-list';

    let total = 0;
    Object.keys(cart).forEach(movieId => {
        const movie = cart[movieId];
        const movieTotal = movie.quantity * movie.price;
        cartQuantities[parseInt(movieId)] = movie.quantity

        total += movieTotal;
        if(movie.quantity > 0){
            // Create <li> element for each cart item
            const itemElement = document.createElement('li');
            itemElement.className = 'cart-item';
            itemElement.innerHTML = `
                <div>${movie.title} - Quantity: ${movie.quantity}</div>
                <div>${movieTotal.toFixed(2)}</div>
            `;
            list.appendChild(itemElement); // Append <li> to the <ul>
        }
    });
    // Append the entire list to the cartItemsContainer
    cartItemsContainer.appendChild(list);

    // Update the total display
    document.getElementById('cartTotal').textContent = total.toFixed(2);
    updateCurrencyDisplay();
}

function updateQuantity(button, change) {
    const container = button.closest('.quantity-controls');
    const quantityDisplay = container.querySelector('.quantity-display');
    let currentQuantity = parseInt(quantityDisplay.textContent, 10);
    const newQuantity = currentQuantity + change;

    if (newQuantity >= 0) { // Prevents quantity from going below 0
        quantityDisplay.textContent = newQuantity;

        // Retrieve additional information from the card
        const cardBody = button.closest('.card-body');
        const title = cardBody.querySelector('.card-title').textContent;
        const price = cardBody.querySelector('.card-text').textContent.match(/\$([\d\.]+)/)[1]; // Extracts price

        // Make an AJAX request to update the quantity in the server
        const movieId = container.getAttribute('data-movie-id');
        sendQuantityUpdate(movieId, change, price, title);
    }
    if(newQuantity === 0){
        const movieId = container.getAttribute('data-movie-id');
        delete cartQuantities[movieId];
    }
}

function sendQuantityUpdate(movieId, change, price, title) {
    const data = { movie_id: movieId, change: change, price: price, title: title};
    fetch('update_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        updateCartDisplay(data.cart); // Update the cart display
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function fetchCartData(callback) {
    fetch('/get_cart')
        .then(response => response.json())
        .then(data => {
            updateCartDisplay(data.cart); // Update your cart display based on this data
            callback();
        })
        .catch(error => console.error('Error fetching cart data:', error));
}

function requestMoviesContainingName(){
    var query = $(this).val();
    if (query.length > 2) { // To reduce unnecessary requests
        $.ajax({
            url: '/search_movies?query=' + encodeURIComponent(query),
            type: 'GET',
            success: function(response) {
                // Process and display the search results
                showMovies(response);
            },
            error: function(error) {
                console.log(error);
            }
        });
    }
}

function updateAd() {
    fetch('/api/get_ad')
        .then(response => response.json()) // Parse the JSON response
        .then(data => {
            const topAdImage = document.getElementById('topAdImage');
            topAdImage.src = data.top_image_url;
            topAdImage.alt = "Top Ad Image";
            
            // Update the title
            const adTitle = document.getElementById('adTitle');
            adTitle.textContent = data.title;
            
            // Update the ad description/text
            const adDescription = document.getElementById('adDescription');
            adDescription.textContent = data.text;
            
            // Update the bottom image
            const bottomAdImage = document.getElementById('bottomAdImage');
            bottomAdImage.src = data.bottom_image_url;
            bottomAdImage.alt = "Bottom Ad Image";

            // Update the banner's background color
            const adBanner = document.getElementById('adBanner');
            adBanner.style.backgroundColor = data.color;
        })
        .catch(error => console.error('Error fetching ad:', error));
}

function updateCurrencyDisplay() {
    const currency = document.getElementById('currencySelector').value;
    const url = new URL('/api/get_conversion', window.location.origin);
    url.searchParams.append('currency', currency);
    fetch(url, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
        }
    })
        .then(response => response.json())
        .then(data => {
            const conversion = data.conversion;
            document.getElementById('currencyRate').textContent = conversion.toFixed(2);
            document.getElementById('currencyUnit').textContent = currency;
            updateTotalPrice(conversion);
        })
        .catch(error => console.error('Error fetching currency rates:', error));
}

function updateTotalPrice(rate) {
    const currency = document.getElementById('currencySelector').value;
    const cartTotal = document.getElementById('cartTotal').textContent;
    const totalPrice = (cartTotal * rate).toFixed(2);
    document.getElementById('cartTotalCurrency').textContent = `${currencySymbol(currency)}${totalPrice}`;
}

function currencySymbol(currency) {
    switch(currency) {
        case 'USD': return '$';
        case 'EUR': return '€';
        case 'JPY': return '¥';
        default: return '$';
    }
}

function submitPayment() {
    const paymentForm = document.getElementById('paymentForm');
    const email = paymentForm.elements[0].value;
    const cardNumber = paymentForm.elements[1].value;
    const cvv = paymentForm.elements[2].value;
    console.log(cardNumber, cvv);
    // Simulated payment request
    fetch('api/process_payment', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({cardNumber, cvv})
    })
    .then(response => response.json())
    .then(data => {
        if (data.message == "Success") {
            // Simulate sending an email
            fetch('api/send_email', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email})
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('paymentStatus').innerText = 'Payment successful and email sent!';
            });
        } else {
            document.getElementById('paymentStatus').innerText = 'Payment failed: Insufficient funds';
        }
    })
    .catch((error) => {
        document.getElementById('paymentStatus').innerText = 'Payment error';
        console.error('Error:', error);
    });
}