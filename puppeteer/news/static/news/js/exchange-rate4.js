const baseURL = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/";
const historyURL = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@";
const refreshExchangeButton = document.querySelectorAll(".exchange-box .refresh");
// данные для формирования курса валют
let rates = "rub"
let exc = ["eur", "usd", "cny", "kzt", "gbp", "btc"];

// Функция для обновления интерфейса с данными о курсах валют
function updateExchangeUI() {
    // получим элемент шаблона
    let exchangeRates = document.querySelectorAll(".exchangeRate");
    // запишем данные из локального хранилища в шаблон
    let exchangeRateData = localStorage.getItem('exchangeRates');
    exchangeRates.forEach(exchangeRate => {
        exchangeRate.innerHTML = exchangeRateData;
    });
    // обновляем отображения данных в кнопке аккордеона
    // выполним предварительную очитстку
    let marqueeContent = '';
    // получим ланные из локального хранилища
    marqueeContent = localStorage.getItem('marqueeContent');
    // запишем данные из локального хранилища в шаблон
    document.querySelectorAll(".marquee").forEach(marquee => {
        marquee.innerHTML = marqueeContent + marqueeContent;
        const marqueeWidth = marquee.scrollWidth / 2;
        marquee.style.width = `${marqueeWidth}px`;
        const containerWidth = marquee.parentElement.offsetWidth;
        marquee.style.animationDuration = `${20 * (marqueeWidth / containerWidth)}s`;
    });
    // время последнего обновления прогноза
    // получим ланные из локального хранилища
    const ratesRefresh = localStorage.getItem('lastRefresh');
    if (ratesRefresh) {
        // запишем данные из локального хранилища в шаблон
        // console.log(`ratesRefresh: ${formatTime(ratesRefresh)}`);
        document.querySelectorAll(".rates-refresh").forEach(refreshElement => {
            refreshElement.innerHTML = `на ${formatTime(ratesRefresh)}`;
        });
    }
}
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
        // получаем текущую дату
        // let refreshDate = new Date();
        // получаем испторические данные
        // const yesterdayDate = normalizeDate(refreshDate, -2);
        const yesterdayDate = normalizeDate(new Date(), -2);
        // console.log(yesterdayDate, "yesterdayDate");
        const historyResponse = await fetch(historyURL + yesterdayDate + `/v1/currencies/` + rates + `.json`);
        if (!historyResponse.ok) {
            console.log(historyResponse.status, "historyesponse.status");
            return;
        }
        const historyData = await historyResponse.json();
        const ratesExc = {};
        const historyRatesExc = {};
        // очищаем предыдущие результаты
        let exchangeRates = '';
        marqueeContent = '';
        // обрабатываем текущие и исторические данные курса валют
        exc.forEach(currency => {
            const currentRate = data[rates] && data[rates][currency];
            const previousRate = historyData[rates] && historyData[rates][currency];
            if (currentRate && previousRate) {
                ratesExc[currency] = 1 / currentRate;
                historyRatesExc[currency] = 1 / previousRate;
                let change = ratesExc[currency] - historyRatesExc[currency];
                let percentageChange = ((change / historyRatesExc[currency]) * 100).toFixed(2);
                // Определяем цвет и знак
                let changeClass, changeSymbol;
                if (change > 0) {
                    changeClass = 'rate-up';
                    changeSymbol = '⬆️ +';
                } else if (change < 0) {
                    changeClass = 'rate-down';
                    changeSymbol = '⬇️ -';
                } else {
                    changeClass = 'rate-neutral';
                    changeSymbol = '❓'; // Можно использовать другой знак
                }
                // собираем курсы валют в виде элементов списка для виджета
                exchangeRates += `
                    <li class="currency-item ${changeClass}">
                        ${currency}: ${ratesExc[currency].toFixed(2)} ${rates}
                        <span class="${changeClass}">${changeSymbol}${Math.abs(change).toFixed(4)} (${Math.abs(percentageChange)}%)</span>
                    </li>`;
                // собираем курсы валют для бегущей строки аккордеона
                marqueeContent += `${currency}: ${ratesExc[currency].toFixed(2)} <span class="${changeClass}">${changeSymbol}${Math.abs(change).toFixed(2)} (${Math.abs(percentageChange)}%)</span> &nbsp; | &nbsp; `;
            } else {
                console.log(`${currency} данные курсов валют не получены`);
            }
        });
        // Сохраняем данные в localStorage
        localStorage.setItem('exchangeRates', exchangeRates);
        localStorage.setItem('marqueeContent', marqueeContent);
        localStorage.setItem('lastRefresh', new Date());
        // Обновляем интерфейс с новыми данными
        updateExchangeUI();
    } catch (error) {
        console.error('Ошибка:', error);
    }
}
// Запуск функции проверки при загрузке страницы
// window.onload = function() {
    document.addEventListener('DOMContentLoaded', function() {
        // Проверка данных в localStorage
        let exchangeRates = localStorage.getItem('exchangeRates');
        let marqueeContent = localStorage.getItem('marqueeContent');
        let lastRefresh = localStorage.getItem('lastRefresh');
        
        if (!exchangeRates || !marqueeContent || !lastRefresh ) {
            console.log("Данных курса валют нет в локальном хранилище - запустим checkExchange");
            checkExchange(rates, exc);
        } else {
            const lastRefreshTime = new Date(lastRefresh).getTime();
            const currentTime = new Date().getTime();
            const deltaTime = currentTime - lastRefreshTime;
    
            if (deltaTime > 3600000) { // 1 час
                console.log("Данные курса валют устарели - запустим checkExchange");
                checkExchange(rates, exc);
            } else {
                console.log("Данные курса валют актуальны - обновляем интерфейс");
                updateExchangeUI();
            }
        }
    
        // Обработка кнопки обновления курса валют
        const refreshExchangeButton = document.querySelectorAll(".exchange-box .refresh");
        refreshExchangeButton.forEach(button => {
            button.addEventListener("click", () => {
                console.log("Данные курса валют принудительно обновлены");
                checkExchange(rates, exc);
            });
        });
    
        // Аккордеон курса валют
        const accordionButtons = document.querySelectorAll('.news-panel-upper.exchangeAccordion');
        accordionButtons.forEach(button => {
            button.addEventListener('click', function () {
                const content = this.nextElementSibling;
                content.classList.toggle('show');
                document.querySelectorAll('.accordionExchange-content').forEach(c => {
                    if (c !== content) {
                        c.classList.remove('show');
                    }
                });
            });
        });
    });