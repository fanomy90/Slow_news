const apiKey = "c3d9500417df01e0513292a8b7357c43";
const apiUrl = `https://api.openweathermap.org/data/2.5/weather?q=`;

const weatherIcon = document.querySelector(".weather-image i");
const searchInput = document.querySelector(".search-box input");
const searchButton = document.querySelector(".search-box button");
const weather = document.querySelector(".weather");
const errorCity = document.querySelector(".errorCity");
const accordionWeatherIcon = document.querySelector(".accordion-weather-image i");

async function checkWeather(city) {
    const response = await fetch(apiUrl + city + `&units=metric&appid=${apiKey}`);
    if (response.status == 404) {
        errorCity.style.display = "block";
        weather.style.display = "none";
    }
    const data = await response.json();
    console.log(data, "data");
    // основные теги блока погоды
    document.querySelector(".city").innerHTML = data.name;
    document.querySelector(".temp").innerHTML = Math.round(data.main.temp) + "&#8451";
    document.querySelector(".humidity").innerHTML = data.main.humidity + " %";
    document.querySelector(".wind").innerHTML = Math.round(data.wind.speed) + " км/ч";
    // отображение погоды в шапке аккордеона
    document.querySelector(".accordionCity").innerHTML = data.name;
    document.querySelector(".accordionTemp").innerHTML = Math.round(data.main.temp) + "&#8451";
    document.querySelector(".accordionHumidity").innerHTML = data.main.humidity + " %";
    document.querySelector(".accordionWind").innerHTML = Math.round(data.wind.speed) + " км/ч";

    // смена иконки погоды
    if(data.weather[0].main == "Clear") {
        weatherIcon.className = "fa-solid fa-sun";
        accordionWeatherIcon.className = "fa-solid fa-sun";
    } else if (data.weather[0].main == "Rain") {
        weatherIcon.className = "fa-solid fa-cloud-rain";
        accordionWeatherIcon.className = "fa-solid fa-cloud-rain";
    } else if (data.weather[0].main == "Mist") {
        weatherIcon.className = "fa-solid fa-mist";
        accordionWeatherIcon.className = "fa-solid fa-mist";
    } else if (data.weather[0].main == "Drizzle") {
        weatherIcon.className = "fa-solid fa-drizzle";
        accordionWeatherIcon.className = "fa-solid fa-drizzle";
    }
    weather.style.display = "block";
    errorCity.style.display = "none";
}
// обработка кнопки поиска погоды по городам
searchButton.addEventListener("click", () => {
    checkWeather(searchInput.value);
    searchInput.value = "";
});
// отработка нажатия enter
searchInput.addEventListener("keydown", (e) => {
    if(e.keyCode === 13) {
        checkWeather(searchInput.value);
        searchInput.value = "";
    }
});
// аккордеон погоды
document.addEventListener('DOMContentLoaded', function () {
    // Находим все элементы с классом weatherAccordion
    const accordionButtons = document.querySelectorAll('.news-panel-bottom.weatherAccordion');

    accordionButtons.forEach(button => {
        button.addEventListener('click', function () {
            // Находим следующий элемент (контент аккордеона)
            const content = this.nextElementSibling;
            // Переключаем класс show
            content.classList.toggle('show');
            // Закрываем другие аккордеоны
            document.querySelectorAll('.accordionWeather-content').forEach(c => {
                if (c !== content) {
                    c.classList.remove('show');
                }
            });
        });
    });
});