//инициализируем Swiper
new Swiper('.image-slider', {
    slidesPerView: 'auto',
    centeredSlides: true,
    spaceBetween: 10,
    loop: true,
    autoplay: {
        delay: 3000,
        disableOnInteraction: false,
    },
    speed: 800,
    effect: 'slide',
    fadeEffect: {
    crossFade: true
    },
    //стрелки
    navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev'
    },
    //навигация
    pagination: {
        el: '.swiper-pagination',
        //буллеты
        clickable: true,
        //динамические буллеты
        dynamicBullets: true,
        //прогрессбар
        //type: 'progressbar',
    },
    //Скролл
    scrolbar: {
        el: '.swiper-scrollbar',
        draggable: true
    },
    on: {
        init: function () {
            this.slideToLoop(1, 1); // Начать с первого слайда
        }
    }
});
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

