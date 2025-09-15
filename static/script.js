document.getElementById('predict-btn').addEventListener('click', async () => {
    const cityInput = document.getElementById('city-input').value;
    const weatherDisplay = document.querySelector('.weather-display');
    const errorDisplay = document.querySelector('.error-message');

    if (!cityInput) {
        errorDisplay.style.display = 'block';
        document.getElementById('error-text').textContent = 'Please enter a city name.';
        weatherDisplay.style.display = 'none';
        return;
    }

    errorDisplay.style.display = 'none';
    weatherDisplay.style.display = 'block';

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ city: cityInput })
        });
        const data = await response.json();

        if (response.ok) {
            document.getElementById('city-name').textContent = data.weather_info.city.toUpperCase();
            document.getElementById('temp').textContent = `${data.weather_info.temperature}°C`;
            document.getElementById('humidity').textContent = `${data.weather_info.humidity}%`;
            document.getElementById('pressure').textContent = `${data.weather_info.pressure} hPa`;
            document.getElementById('prediction-text').textContent = data.prediction;
        } else {
            errorDisplay.style.display = 'block';
            document.getElementById('error-text').textContent = data.error;
            weatherDisplay.style.display = 'none';
        }
    } catch (error) {
        errorDisplay.style.display = 'block';
        document.getElementById('error-text').textContent = 'Could not connect to the server. Try again later.';
        weatherDisplay.style.display = 'none';
    }
});
// Fade-in animation after prediction
function showWeather() {
    const weatherDisplay = document.querySelector('.weather-display');
    weatherDisplay.style.display = 'block';
    weatherDisplay.style.opacity = 0;
    setTimeout(() => {
        weatherDisplay.style.opacity = 1;
    }, 50);
}
