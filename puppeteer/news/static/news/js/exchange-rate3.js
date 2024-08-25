
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
const historyURL = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@";
// let exchangeRate = document.getElementById("exchangeRate");
// let marquee = document.getElementById("marquee");

function normalizeDate(date, shift=0) {
    // выполняем сдвиг даты если нужно
    date.setDate(date.getDate() + shift);
    // Получаем компоненты даты
    let year = date.getFullYear();
    let month = (date.getMonth() + 1).toString().padStart(2, '0'); // Месяцы в JavaScript от 0 до 11
    let day = date.getDate().toString().padStart(2, '0');
    // Формируем строку в формате YYYY-MM-DD
    return `${year}-${month}-${day}`;
}
function formatTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString();
}
async function checkExchange(rates, exc) {
    try {
        // получаем текущщий курс валюты
        const response = await fetch(baseURL + rates + `.json`);
        if (!response.ok) {
            console.log(response.status, "response.status");
            return;
        }
        const data = await response.json();
        // получаем испторические данные
        const yesterdayDate = normalizeDate((new Date()), -2);
        // console.log(yesterdayDate, "yesterdayDate");
        const historyResponse = await fetch(historyURL + yesterdayDate + `/v1/currencies/` + rates + `.json`);
        if (!historyResponse.ok) {
            console.log(historyResponse.status, "historyesponse.status");
            return;
        }
        const historyData = await historyResponse.json();
        // console.log(data, "data");
        // console.log(historyData, "historyData");
        const ratesExc = {};
        const historyRatesExc = {};

        // Очищаем предыдущие результаты
        let exchangeRates = document.querySelectorAll(".exchangeRate");
        exchangeRates.forEach(exchangeRate => {
            exchangeRate.innerHTML = '';
        });
        let marqueeContent = '';
        
        let refreshDate = document.querySelectorAll(".rates-refresh").forEach(refreshElement => {
            refreshElement.innerHTML = `на ${formatTime(new Date().toISOString())}`;
        });

        exc.forEach(currency => {
            const currentRate = data[rates] && data[rates][currency];
            const previousRate = historyData[rates] && historyData[rates][currency];

            if (currentRate && previousRate) {
                ratesExc[currency] = 1 / currentRate;
                historyRatesExc[currency] = 1 / previousRate;

                // let change = currentRate - previousRate;
                let change2 = ratesExc[currency] - historyRatesExc[currency];
                console.log(`${currency}: ${change2}`)
                // let percentageChange = ((change / previousRate) * 100).toFixed(2);
                let percentageChange = ((change2 / historyRatesExc[currency]) * 100).toFixed(2);
                console.log(`${currency}: ${percentageChange}`)

                // Определяем цвет и знак
                let changeClass, changeSymbol;
                if (change2 > 0) {
                    changeClass = 'rate-up';
                    changeSymbol = '⬆️ +';
                } else if (change2 < 0) {
                    changeClass = 'rate-down';
                    changeSymbol = '⬇️ -';
                } else {
                    changeClass = 'rate-neutral';
                    changeSymbol = '❓'; // Можно использовать другой знак
                    // changeSymbol = '';
                }

                // Выводим информацию
                exchangeRates.forEach(exchangeRate => {
                    exchangeRate.innerHTML += `
                        <li class="currency-item ${changeClass}">
                            ${currency}: ${ratesExc[currency].toFixed(2)} ${rates}
                            <span class="${changeClass}">${changeSymbol}${Math.abs(change2).toFixed(4)} (${Math.abs(percentageChange)}%)</span>
                        </li>`;
                });

                console.log(`${yesterdayDate} ${currency}: ${historyRatesExc[currency].toFixed(2)} ${rates}`)
                console.log(`${new Date()} ${currency}: ${ratesExc[currency].toFixed(2)} ${rates}`)
                
                // marqueeContent += `${currency}: ${ratesExc[currency].toFixed(2)}  &nbsp; | &nbsp; `;
                marqueeContent += `${currency}: ${ratesExc[currency].toFixed(2)} <span class="${changeClass}">${changeSymbol}${Math.abs(change2).toFixed(4)} (${Math.abs(percentageChange)}%)</span> &nbsp; | &nbsp; `;
                // marqueeContent += `<p clacc="currency-item ${changeClass}"> ${currency}: ${ratesExc[currency].toFixed(2)} ${rates} <span class="${changeClass}">${changeSymbol}${Math.abs(change).toFixed(2)} (${Math.abs(percentageChange)}%)</span></p>  &nbsp; | &nbsp; `;
                // marqueeContent += `${currency}: ${ratesExc[currency].toFixed(2)} ${rates} <span class="${colorClass}">${arrowIcon} ${rateDifferenceString}</span> &nbsp; | &nbsp; `;
                
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
        // const yesterdayDate = normalizeDate((new Date()), -1);
        // console.log(yesterdayDate);
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