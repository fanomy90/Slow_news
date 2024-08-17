const apiKey = "c3d9500417df01e0513292a8b7357c43";
const apiUrl = `https://api.openweathermap.org/data/2.5/weather?q=`;

const searchInput = document.querySelectorAll(".search-box input");
const searchButton = document.querySelectorAll(".search-box button");

async function checkWeather(city) {
    const response = await fetch(apiUrl + city + `&units=metric&appid=${apiKey}`);
    const data = await response.json();

    if (response.status == 404) {
        document.querySelectorAll(".errorCity").forEach(errorCity => {
            errorCity.style.display = "block";
        });
        document.querySelectorAll(".weather").forEach(weather => {
            weather.style.display = "none";
        });
        return;
    }

    // основные теги блока погоды
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

    // смена иконки погоды
    const weatherMain = data.weather[0].main;
    let iconClass = '';

    if (weatherMain == "Clear") {
        iconClass = "fa-solid fa-sun";
    } else if (weatherMain == "Rain") {
        iconClass = "fa-solid fa-cloud-rain";
    } else if (weatherMain == "Mist") {
        iconClass = "fa-solid fa-smog";  // Заменил на существующий класс
    } else if (weatherMain == "Drizzle") {
        iconClass = "fa-solid fa-cloud-rain";  // Заменил на существующий класс
    } else if (weatherMain == "Clouds") {
        iconClass = "fa-solid fa-cloud";  // Заменил на существующий класс
    }
    console.log(data, "data");
    console.log(iconClass, "iconClass");

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
// обработка кнопки поиска погоды по городам
searchButton.forEach((button, index) => {
    button.addEventListener("click", () => {
        checkWeather(searchInput[index].value);
        searchInput[index].value = "";
    });
});

// отработка нажатия enter
searchInput.forEach((input, index) => {
    input.addEventListener("keydown", (e) => {
        if (e.keyCode === 13) {
            checkWeather(input.value);
            input.value = "";
        }
    });
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