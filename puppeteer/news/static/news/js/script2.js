//инициализируем Swiper
new Swiper('.image-slider', {
    slidesPerView: 'auto', // Adjust this value as needed
    centeredSlides: true, // Center the active slide
    spaceBetween: 20,
    loop: true,
    autoplay: {
        delay: 3000,
        disableOnInteraction: false,
    },
    speed: 800, // Adjust the speed (in milliseconds)
    effect: 'slide', // Use the 'fade' effect for smoother transitions
    fadeEffect: {
    crossFade: true // Enable cross-fade effect for smoother transitions
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