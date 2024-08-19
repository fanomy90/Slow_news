const apiKey = "c3d9500417df01e0513292a8b7357c43";
const apiUrl = "https://api.openweathermap.org/data/2.5/weather?q=";

const searchInput = document.querySelectorAll(".search-box input");
const searchButton = document.querySelectorAll(".search-box .search");
const refreshButton = document.querySelectorAll(".search-box .refresh");
// const refreshButton = document.querySelectorAll(".refresh-box button");

// Функция для обновления интерфейса с данными о погоде
function updateWeatherUI(data) {
    document.querySelectorAll(".city").forEach(cityElement => {
        cityElement.innerHTML = data.name;
    });
    document.querySelectorAll(".temp").forEach(tempElement => {
        tempElement.innerHTML = Math.round(data.main.temp) + "&#8451";
    });
    document.querySelectorAll(".humidity").forEach(humidityElement => {
        humidityElement.innerHTML = data.main.humidity + " %";
    });
    document.querySelectorAll(".wind").forEach(windElement => {
        windElement.innerHTML = Math.round(data.wind.speed) + " км/ч";
    });
    // время последнего обновления прогноза
    const lastRefresh = localStorage.getItem('lastRefresh');
    if (lastRefresh) {
        console.log(`Last refresh: ${formatTime(lastRefresh)}`);
        document.querySelectorAll(".last-refresh").forEach(refreshElement => {
            refreshElement.innerHTML = `Погода ${formatTime(lastRefresh)}`;
        });
    }
    // отображение погоды в шапке аккордеона
    document.querySelectorAll(".accordionCity").forEach(accordionCityElement => {
        accordionCityElement.innerHTML = data.name;
    });
    document.querySelectorAll(".accordionTemp").forEach(accordionTempElement => {
        accordionTempElement.innerHTML = Math.round(data.main.temp) + "&#8451";
    });
    document.querySelectorAll(".accordionHumidity").forEach(accordionHumidityElement => {
        accordionHumidityElement.innerHTML = data.main.humidity + " %";
    });
    document.querySelectorAll(".accordionWind").forEach(accordionWindElement => {
        accordionWindElement.innerHTML = Math.round(data.wind.speed) + " км/ч";
    });

    const weatherMain = data.weather[0].main;
    let iconClass = '';

    if (weatherMain == "Clear") {
        iconClass = "fa-solid fa-sun";
    } else if (weatherMain == "Rain") {
        iconClass = "fa-solid fa-cloud-rain";
    } else if (weatherMain == "Mist") {
        iconClass = "fa-solid fa-smog";
    } else if (weatherMain == "Drizzle") {
        iconClass = "fa-solid fa-cloud-rain";
    } else if (weatherMain == "Clouds") {
        iconClass = "fa-solid fa-cloud";
    }

    document.querySelectorAll(".weather-image i").forEach(iconElement => {
        iconElement.className = iconClass;
    });
    document.querySelectorAll(".accordion-weather-image i").forEach(accordionIconElement => {
        accordionIconElement.className = iconClass;
    });

    document.querySelectorAll(".weather").forEach(weather => {
        weather.style.display = "block";
    });
    document.querySelectorAll(".errorCity").forEach(errorCity => {
        errorCity.style.display = "none";
    });
}

// Функция для проверки погоды
async function checkWeather(city) {
    const response = await fetch(apiUrl + city + `&units=metric&appid=${apiKey}`);
    const data = await response.json();
    console.log(data, "data");
    // console.log(data.name, "city");

    if (response.status == 404) {
        document.querySelectorAll(".errorCity").forEach(errorCity => {
            errorCity.style.display = "block";
        });
        document.querySelectorAll(".weather").forEach(weather => {
            weather.style.display = "none";
        });
        return;
    }

    // Сохраняем данные в localStorage
    const currentTime = new Date().toISOString();
    localStorage.setItem('weatherData', JSON.stringify(data));
    // localStorage.setItem('lastCity', city);
    localStorage.setItem('lastCity', data.name);
    localStorage.setItem('lastRefresh', currentTime);

    // Обновляем интерфейс с новыми данными
    updateWeatherUI(data);
}

// Функция для форматирования времени (необязательно, для отображения)
function formatTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString();
}

// Обработка кнопки поиска погоды по городам
searchButton.forEach((button, index) => {
    button.addEventListener("click", () => {
        checkWeather(searchInput[index].value);
        searchInput[index].value = "";
    });
});

// Обработка нажатия Enter
searchInput.forEach((input, index) => {
    input.addEventListener("keydown", (e) => {
        if (e.keyCode === 13) {
            checkWeather(input.value);
            input.value = "";
        }
    });
});

// Обработка кнопки обновления погоды по последнему городу
refreshButton.forEach((button, index) => {
    button.addEventListener("click", () => {
        const lastCity = localStorage.getItem('lastCity');
        if (lastCity) {
            // console.log(`${lastCity} lastCity`);
            checkWeather(lastCity);
        }
        // else {
        //     checkWeather(searchInput[index].value);
        //     searchInput[index].value = "";
        // }
    });
});

// Аккордеон погоды
document.addEventListener('DOMContentLoaded', function () {
    // Проверяем наличие данных в localStorage
    const savedWeatherData = localStorage.getItem('weatherData');
    if (savedWeatherData) {
        const data = JSON.parse(savedWeatherData);
        updateWeatherUI(data);
    }

    const accordionButtons = document.querySelectorAll('.news-panel-bottom.weatherAccordion');
    accordionButtons.forEach(button => {
        button.addEventListener('click', function () {
            const content = this.nextElementSibling;
            content.classList.toggle('show');
            document.querySelectorAll('.accordionWeather-content').forEach(c => {
                if (c !== content) {
                    c.classList.remove('show');
                }
            });
        });
    });
});
