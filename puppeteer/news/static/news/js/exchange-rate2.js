
// сервис по получению курса валют
// https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/eur.json
// расшифровка валюты тут
// https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies.min.json
// курс на определенную дату
// https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@2024-08-15/v1/currencies/eur.json
// курсы криптовалют
// https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/btc.json
// что то тоже про крипту
// https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/btc.min.json

const baseURL = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/";
// let exchangeRate = document.getElementById("exchangeRate");
// let marquee = document.getElementById("marquee");

async function checkExchange(rates, exc) {
    try {
        const response = await fetch(baseURL + rates + `.json`);
        if (!response.ok) {
            console.log(response.status, "response.status");
            return;
        }
        const data = await response.json();
        // console.log(data, "data");
        const ratesExc = {};

        // Очищаем предыдущие результаты
        let exchangeRates = document.querySelectorAll(".exchangeRate");
        exchangeRates.forEach(exchangeRate => {
            exchangeRate.innerHTML = '';
        });
        let marqueeContent = '';

        exc.forEach(currency => {
            if (data[rates] && data[rates][currency]) {
                ratesExc[currency] = 1 / data[rates][currency];
                // выведем список курса валют в шаблон
                exchangeRates.forEach(exchangeRate => {
                    exchangeRate.innerHTML += `<li class="currency-item">${currency}: ${ratesExc[currency].toFixed(2)}</li>`;
                });
                
                marqueeContent += `${currency}: ${ratesExc[currency].toFixed(2)} &nbsp; | &nbsp; `;
            } else {
                console.log(`${currency} not found in the data`);
            }
        });
        // Настройка и заполнение для всех элементов .marquee
        let marquees = document.querySelectorAll(".marquee");
        marquees.forEach(marquee => {
            marquee.innerHTML = marqueeContent + marqueeContent;
            const marqueeWidth = marquee.scrollWidth / 2;
            marquee.style.width = `${marqueeWidth}px`;
            const containerWidth = marquee.parentElement.offsetWidth;
            marquee.style.animationDuration = `${20 * (marqueeWidth / containerWidth)}s`;
        });
        // console.log(ratesExc, `rates in ${rates}`);

    } catch (error) {
        console.error('Error:', error);
    }
}
let rates = "rub"
let exc = ["eur", "usd", "cny", "kzt", "gbp", "btc"];
checkExchange(rates, exc);

// аккордеон курса валют
document.addEventListener('DOMContentLoaded', function () {
    // Находим все элементы с классом weatherAccordion
    const accordionButtons = document.querySelectorAll('.news-panel-upper.exchangeAccordion');

    accordionButtons.forEach(button => {
        button.addEventListener('click', function () {
            // Находим следующий элемент (контент аккордеона)
            const content = this.nextElementSibling;
            // Переключаем класс show
            content.classList.toggle('show');
            // Закрываем другие аккордеоны
            document.querySelectorAll('.accordionExchange-content').forEach(c => {
                if (c !== content) {
                    c.classList.remove('show');
                }
            });
        });
    });
});