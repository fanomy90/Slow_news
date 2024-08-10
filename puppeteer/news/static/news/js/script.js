// работа кнопки бургер меню
$(document).ready(function() {
    $('.header__burger').click(function(event) {
        $('.header__burger,.header__menu').toggleClass('active');
        $('body').toggleClass('lock');
    });
});
// скрипт для замены тега br на p на странице post.html
document.addEventListener('DOMContentLoaded', function() {
    let contentDiv = document.querySelector('.news-content');
    if (contentDiv) {
        let paragraphs = contentDiv.innerHTML.split('<br>').join('</p><p>');
        paragraphs = '<p>' + paragraphs + '</p>';
        contentDiv.innerHTML = paragraphs;
    }
});
// скрипт для замены тега br на p на странице index.html
document.addEventListener('DOMContentLoaded', function() {
    let contentDivs = document.querySelectorAll('.news-content');
    contentDivs.forEach(function(contentDiv) {
        // Получаем HTML содержимое
        let html = contentDiv.innerHTML;
        // Заменяем <br> на </p><p>, добавляем <p> в начале и конце
        let newHtml = html.split('<br>').join('</p><p>');
        if (newHtml) {
            newHtml = '<p>' + newHtml + '</p>';
        }
        // Устанавливаем новое HTML содержимое
        contentDiv.innerHTML = newHtml;
    });
});

// описываем логику банера с погодой
// const apiKey = "c3d9500417df01e0513292a8b7357c43";
// const apiUrl = `https://api.openweathermap.org/data/2.5/weather?q=`;
// // const apiUrl = `https://api.openweathermap.org/data/2.5/weather?q=moscow&units=metric&appid=${apiKey}`;
// const weatherIcon = document.querySelector(".weather-image i");

// const searchInput = document.querySelector(".search-box input");
// const searchButton = document.querySelector(".search-box button");
// const weather = document.querySelector(".weather");
// const errorCity = document.querySelector(".errorCity");

// async function checkWeather(city) {
//     const response = await fetch(apiUrl + city + `&units=metric&appid=${apiKey}`);
//     if (response.status == 404) {
//         errorCity.style.display = "block";
//         weather.style.display = "none";
//     }
//     const data = await response.json();
//     console.log(data, "data");

//     document.querySelector(".city").innerHTML = data.name;
//     document.querySelector(".temp").innerHTML = Math.round(data.main.temp) + "&#8451";
//     document.querySelector(".humidity").innerHTML = data.main.humidity + " %";
//     document.querySelector(".wind").innerHTML = Math.round(data.wind.speed) + " км/ч";
//     // смена иконки погоды
//     if(data.weather[0].main == "Clear") {
//         weatherIcon.className = "fa-solid fa-sun";
//     } else if (data.weather[0].main == "Rain") {
//         weatherIcon.className = "fa-solid fa-cloud-rain";
//     } else if (data.weather[0].main == "Mist") {
//         weatherIcon.className = "fa-solid fa-mist";
//     } else if (data.weather[0].main == "Drizzle") {
//         weatherIcon.className = "fa-solid fa-drizzle";
//     }
//     weather.style.display = "block";
//     errorCity.style.display = "none";
// }
// // обработка кнопки поиска погоды по городам
// searchButton.addEventListener("click", () => {
//     checkWeather(searchInput.value);
//     searchInput.value = "";
// });
// // отработка нажатия enter
// searchInput.addEventListener("keydown", (e) => {
//     if(e.keyCode === 13) {
//         checkWeather(searchInput.value);
//         searchInput.value = "";
//     }
// });

// // аккордеон погоды
// document.addEventListener('DOMContentLoaded', function () {
//     // Находим все элементы с классом weatherAccordion
//     const accordionButtons = document.querySelectorAll('.news-panel-bottom.weatherAccordion');

//     accordionButtons.forEach(button => {
//         button.addEventListener('click', function () {
//             // Находим следующий элемент (контент аккордеона)
//             const content = this.nextElementSibling;

//             // Переключаем класс show
//             content.classList.toggle('show');

//             // Закрываем другие аккордеоны
//             document.querySelectorAll('.accordionWeather-content').forEach(c => {
//                 if (c !== content) {
//                     c.classList.remove('show');
//                 }
//             });
//         });
//     });
// });

