(function ($) {
    "use strict";

    // Spinner
    var spinner = function () {
        setTimeout(function () {
            if ($('#spinner').length > 0) {
                $('#spinner').removeClass('show');
            }
        }, 1);
    };
    spinner();
    
    
    // Initiate the wowjs
    new WOW().init();


    // Sticky Navbar
    $(window).scroll(function () {
        if ($(this).scrollTop() > 45) {
            $('.nav-bar').addClass('sticky-top');
        } else {
            $('.nav-bar').removeClass('sticky-top');
        }
    });
    
    
    // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });
    $('.back-to-top').click(function () {
        $('html, body').animate({scrollTop: 0}, 1500, 'easeInOutExpo');
        return false;
    });


    // Header carousel
    $(".header-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1500,
        items: 1,
        dots: true,
        loop: true,
        nav : true,
        navText : [
            '<i class="bi bi-chevron-left"></i>',
            '<i class="bi bi-chevron-right"></i>'
        ]
    });


    // Testimonials carousel
    $(".testimonial-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        margin: 24,
        dots: false,
        loop: true,
        nav : true,
        navText : [
            '<i class="bi bi-arrow-left"></i>',
            '<i class="bi bi-arrow-right"></i>'
        ],
        responsive: {
            0:{
                items:1
            },
            992:{
                items:2
            }
        }
    });
    
})(jQuery);

window.onload = function() {
    const searchTerms = ['Products', 'Cars', 'Mobiles', 'Bikes', 'Electronics', 'Furnitures','Properties', 'jobs'];
    let currentIndex = 0;

    function changePlaceholder() {
        const inputField = document.getElementById('searchInput');
        if (inputField) {
            // Update placeholder with the current search term
            inputField.placeholder = `Search "${searchTerms[currentIndex]}"`;
            // Move to the next search term
            currentIndex = (currentIndex + 1) % searchTerms.length;
        }
    }

    // Change the placeholder every second
    setInterval(changePlaceholder, 1500);
};

//share button funnction

document.getElementById('shareButton').addEventListener('click', function () {
    if (navigator.share) {
      navigator
        .share({
          title: document.title,
          text: 'Check out this page!',
          url: window.location.href
        })
        .then(() => {
          console.log('Thanks for sharing!')
        })
        .catch(console.error)
    } else {
      // Fallback: Copy to Clipboard
      navigator.clipboard
        .writeText(window.location.href)
        .then(() => {
          alert('Link copied to clipboard!')
        })
        .catch(console.error)
    }
  })


//   check char is less the 500 for text box
function updateCharCount() {
    let textarea = document.getElementById('description')
    let charCount = textarea.value.length
    document.getElementById('charCount').innerText = `${charCount}/500 characters`
  
    if (charCount > 500) {
      textarea.value = textarea.value.substring(0, 500)
    }
  }