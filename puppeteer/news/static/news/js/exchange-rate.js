
// сервис по получению курса валют
// https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/eur.json


// api.ratesapi.io/api/2010-01-12?base=USD&symbols=GBP
// ratesapi-io.p.rapidapi.com/2010-01-12?base=USD

// для rapid нужно карточка и подписка
// const rapid="adfc945e56mshbd2bd8dcd41b1f2p1c9f00jsnc8aae8824e74"
// const url = 'https://ratesapi-io.p.rapidapi.com/2010-01-12?base=USD';
// const options = {
// 	method: 'GET',
// 	headers: {
// 		'x-rapidapi-host': 'ratesapi-io.p.rapidapi.com',
// 		'x-rapidapi-key': `${rapid}`
// 	}
// };

// fetch(url, options)
// 	.then(response => response.json())
// 	.then(data => console.log(data))
// 	.catch(error => console.error('Error:', error));

const exchange="afb5ac4487990ac83c0ee16e9fb03bb2"
const baseURL="http://api.exchangeratesapi.io/v1/latest"
const key="?access_key=afb5ac4487990ac83c0ee16e9fb03bb2"
const base = "&base=EUR"
const symbols = "&symbols=USD,RUB,CNY,KZT"

async function checkExchange() {
    // try {
    //     const response = await fetch(baseURL + key + base + symbols);
    //     if (!response.ok) {
    //         console.log(response.status, "response.status");
    //         return;
    //     }
    //     const data = await response.json();
    //     console.log(data, "data");

    //     // Получаем курс EUR к RUB
    //     const rateEURToRUB = data.rates.RUB;
    //     console.log('Rate EUR to RUB:', rateEURToRUB);

    //     // Создаем объект для хранения курсов
    //     const ratesInRUB = {};

    //     // Пересчитываем курсы всех валют относительно RUB
    //     for (const [currency, rate] of Object.entries(data.rates)) {
    //         if (currency !== 'RUB') {
    //             ratesInRUB[currency] = rateEURToRUB / rate;
    //         }
    //     }

    //     // Добавляем EUR к результатам
    //     ratesInRUB['EUR'] = rateEURToRUB;

    //     // Выводим результат
    //     console.log('Rates with RUB as base (including EUR):', ratesInRUB);
    // } catch (error) {
    //     console.error('Error:', error);
    // }

    // заморозил данные для теста вывода 
    const ratesInRUB = {
        "USD": 89.7983818682067,
        "CNY": 12.579621174952205,
        "KZT": 0.1870881612523563,
        "EUR": 98.892264
        }
        console.log('Rates with RUB as base (including EUR):', ratesInRUB);
}
//ratesInRUB = 
// {
//     "USD": 89.7983818682067,     0.010935646     91,44
//     "CNY": 12.579621174952205,   0.07824579
//     "KZT": 0.1870881612523563,   5.25276601
//     "EUR": 98.892264             0.0099454362    100,55
// }




checkExchange();
