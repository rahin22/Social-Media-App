// Scroll Top Button

function showScrollTop() {
    if (document.body.scrollTop > 400 || document.documentElement.scrollTop > 400) {
        document.getElementById('scrollTop').style.opacity = '1';
        document.getElementById('scrollTop').style.visibility = 'visible';
    } else {
        document.getElementById('scrollTop').style.opacity = '0';
        document.getElementById('scrollTop').style.visibility = 'hidden';
    }
}

window.addEventListener('scroll', showScrollTop)

function scrollToTop() {
    window.scrollTo(0, 0);
}


// Search Bar Logic

document.addEventListener('DOMContentLoaded', function () {
    const searchForm = document.getElementById('search-form');
    const searchInput = searchForm.querySelector('.search-input');
    const searchDropdown = searchForm.querySelector('.search-dropdown');
    const searchResultsUl = searchDropdown.querySelector('.search-results');

    searchInput.addEventListener('input', function () {
        const query = searchInput.value.trim();

        if (query.length === 0) {
            showPromptDropdown();
            return;
        }

        var xhttp = new XMLHttpRequest();
        xhttp.open('GET', `/search?query=${query}`);
        xhttp.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        xhttp.onreadystatechange = function () {
            if (xhttp.readyState === XMLHttpRequest.DONE) {
                if (xhttp.status === 200) {
                    const data = JSON.parse(xhttp.responseText);
                    const results = data.results;
                    if (results.length === 0) {
                        hideDropdown();
                        return;
                    }
                    showDropdown(results);
                } else {
                    hideDropdown();
                }
            }
        };

        xhttp.send();
    });

    searchInput.addEventListener('focus', function () {
        if (searchInput.value.trim().length === 0) {
            showPromptDropdown();
        }
    });

    function showDropdown(results) {
        searchResultsUl.innerHTML = '';
        searchResultsUl.style.visibility = 'visible';
        results.forEach(result => {
            const li = document.createElement('li');
            const username = result[0];
            const encodedPfp = result[2];

            const link = document.createElement('a');
            link.href = `/profiles/${username}`;
            link.innerHTML =
                `<img src="data:image/jpeg;base64,${encodedPfp}" id="search-pic" class="profile-pic" style="width: 30px; height: 30px;">
            <span>${username}</span>`;
            link.style.textDecoration = 'none';
            li.appendChild(link);
            searchResultsUl.appendChild(li);
        });
        searchDropdown.style.display = 'block';
    }

    function showPromptDropdown() {
        searchResultsUl.innerHTML = '';
        const li = document.createElement('li');
        li.innerText = 'Try Searching a Username...';
        li.style.color = '#888';
        searchResultsUl.appendChild(li);
        searchDropdown.style.display = 'block';
    }

    document.addEventListener('click', function (event) {
        const outClick = searchDropdown.contains(event.target) || searchForm.contains(event.target);
        if (!outClick) {
            hideDropdown();
        }
    });

    function hideDropdown() {
        searchDropdown.style.display = 'none';
    }
});














// Light/Dark Mode Toggle 

let moon = document.getElementById('moon');
let sun = document.getElementById('sun');
let root = document.querySelector(':root');
let create = document.getElementById('create-button')
var dark = false;

function changeToDark() {
    localStorage.setItem('dark', 'true');
    sun.style.visibility = 'hidden';
    sun.style.opacity = '0';
    moon.style.visibility = 'visible';
    moon.style.opacity = '1';
    create.style.color = '#fff'

    root.style.setProperty('--text-color', '#fff');
    root.style.setProperty('--bg-color', '#000');
    root.style.setProperty('--dark-color', '#003c6d');
    root.style.setProperty('--search-bar-color', '#000');
    root.style.setProperty('--hover-color', '#fff');
}

function changeToLight() {
    localStorage.setItem('dark', 'false');
    sun.style.visibility = 'visible';
    sun.style.opacity = '1';
    moon.style.visibility = 'hidden';
    moon.style.opacity = '0';
    create.style.color = '#000'

    root.style.setProperty('--text-color', '#000');
    root.style.setProperty('--bg-color', '#fff');
    root.style.setProperty('--dark-color', '#000');
    root.style.setProperty('--search-bar-color', '#f3f3f3');
    root.style.setProperty('--hover-color', '#003c6d');
}

window.onload = function () {
    var storedTheme = localStorage.getItem('dark');
    if (storedTheme === 'true') {
        changeToDark();
    } else {
        changeToLight();
    }
};





// Post Modal

function openPostModal() {
    var postModal = document.getElementById('postModal');
    var modal = new bootstrap.Modal(postModal);
    modal.show();
}

document.addEventListener('DOMContentLoaded', function () {
    var postContent = document.getElementById('postContent');
    var postLimit = document.getElementById('post_limit');
    var maxCharacters = 280;

    postContent.addEventListener('input', function () {
        var remainingCharacters = maxCharacters - postContent.value.length;
        postLimit.textContent = remainingCharacters + ' characters remaining';

        if (remainingCharacters <= 0) {
            postContent.value = postContent.value.slice(0, maxCharacters);
            remainingCharacters = 0;
            postLimit.textContent = remainingCharacters + ' characters remaining';
        }
    });

    postContent.addEventListener('keydown', function (event) {
        var remainingCharacters = maxCharacters - postContent.value.length;
        if (remainingCharacters <= 0 && event.key !== 'Backspace' && event.key !== 'Delete') {
            event.preventDefault();
        }
    });
});



function previewImage(event) {
    var reader = new FileReader();
    reader.onload = function () {
        var img = $('#imagePreview');
        img.attr('src', reader.result);
        img.css('display', 'block');
    };
    reader.readAsDataURL(event.target.files[0]);
}


$('#postModal').on('hidden.bs.modal', function () {
    var form = document.getElementById('postForm');
    form.reset();
    document.getElementById('imagePreview').style.display = 'none';
    document.getElementById('postContent').value = '';
});


// Post Interactions

document.addEventListener('DOMContentLoaded', function () {
    var likeButtons = document.querySelectorAll('[id^="like-button-"]');
    likeButtons.forEach(function (likeButton) {
        var isLiked = likeButton.dataset.isLiked === 'true';
        if (isLiked) {
            likeButton.className = "ri-heart-fill like";
            likeButton.style.color = "#fe5d9f"
        } else {
            likeButton.className = "ri-heart-line like";
            likeButton.style.color = "var(--text-color)"
        }
    });
});

function pressLike(index) {
    var likeButton = document.getElementById('like-button-' + index);
    console.log(likeButton)
    var postIdToLike = likeButton.dataset.postId;
    console.log(postIdToLike)
    var postID = JSON.stringify({ postID: postIdToLike });
    console.log(postID)

    var xhttp = new XMLHttpRequest();
    xhttp.open('POST', '/likeUpdate', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.onload = function () {
        if (xhttp.status === 200) {
            var response = JSON.parse(xhttp.responseText);
            if (response.is_liked) {
                likeButton.className = "ri-heart-fill like";
                likeButton.style.color = "#fe5d9f"
                likeButton.dataset.isLiked = 'true';
            } else {
                likeButton.className = "ri-heart-line like";
                likeButton.style.color = "var(--text-color)"
                likeButton.dataset.isLiked = 'false';
            }
        }
    }
    xhttp.send(postID);
}


function pressComment(index) {
    var commentButton = document.getElementById('comment-button-' + index);
    var postIdToComment = commentButton.dataset.postId;
    var postID = JSON.stringify({ postID: postIdToComment });
    var loadingBar = document.getElementById('loading-bar');
    loadingBar.style.display = 'block';

    var xhttp = new XMLHttpRequest();
    xhttp.open('POST', '/comment/<postID>', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.onload = function () {
        if (xhttp.status >= 200 && xhttp.status < 300) {
            window.location.href = '/comment/' + postIdToComment;
        } else {
            console.log('Failed', xhttp.statusText);
        }
    };

    xhttp.send(postID);
}


document.addEventListener('DOMContentLoaded', function () {
    var saveButtons = document.querySelectorAll('[id^="save-button-"]');
    saveButtons.forEach(function (saveButton) {
        var isSaved = saveButton.dataset.isSaved === 'true';
        if (isSaved) {
            saveButton.className = "ri-bookmark-fill save";
            saveButton.style.color = "#eed202"
        } else {
            saveButton.className = "ri-bookmark-line save";
            saveButton.style.color = "var(--text-color)"
            console.log('Post is not saved')
        }
    });
});



function pressSave(index) {
    var saveButton = document.getElementById('save-button-' + index);
    var postIdToSave = saveButton.dataset.postId;
    var postID = JSON.stringify({ postID: postIdToSave });

    var xhttp = new XMLHttpRequest();
    xhttp.open('POST', '/savePost', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.onload = function () {
        if (xhttp.status === 200) {
            var response = JSON.parse(xhttp.responseText);
            if (response.is_saved) {
                saveButton.className = "ri-bookmark-fill save";
                saveButton.style.color = "#eed202"
                saveButton.dataset.isSaved = 'true';
            } else {
                saveButton.className = "ri-bookmark-line save";
                saveButton.style.color = "var(--text-color)"
                saveButton.dataset.isSaved = 'false';
            }
        }
    }
    xhttp.send(postID);
}






// Navbar change on scroll to colour

let nav = document.querySelector('nav');

function changeHeader() {
    if (document.body.scrollTop > 50) {
        nav.classList.add('change-header');


    } else if (document.documentElement.scrollTop > 50) {
        nav.classList.add('change-header');
    }
    else {
        nav.classList.remove('change-header');
    }
}
window.addEventListener('scroll', changeHeader)



// Slide In Animations

const inViewport = (entries, observer) => {
    entries.forEach(entry => {
        entry.target.classList.toggle('is-inViewport', entry.isIntersecting);
    })
}

const Obs = new IntersectionObserver(inViewport);
const obsOptions = {};

const ELs_inViewport = document.querySelectorAll('[data-inViewport]');
ELs_inViewport.forEach(EL => {
    Obs.observe(EL, obsOptions);
});

function homeRedir() {
    window.location.href = "/";

}

// Password Visible Toggle

const password = document.getElementById('password')
const toggle = document.querySelector('.ri-eye-off-line')

toggle.addEventListener("click", () => {
    if (password.type === "password") {
        password.type = "text";
        toggle.classList.replace("ri-eye-off-line", "ri-eye-line");
    } else {
        password.type = "password";
        toggle.classList.replace("ri-eye-line", "ri-eye-off-line");
    }
})

document.addEventListener("DOMContentLoaded", function () {
    const oldPasswordToggle = document.querySelector('.oldpasswordtoggle')
    const newPasswordToggle = document.querySelector('.newpasswordtoggle')
    const confirmToggle = document.querySelector('.confirmtoggle')
    const delpasswordToggle = document.querySelector('.delpasswordtoggle')

    function toggleVisibility(fieldId, toggleButton) {
        const field = document.getElementById(fieldId)
        if (field.type === "password") {
            field.type = "text";
            toggleButton.classList.replace("ri-eye-off-line", "ri-eye-line");
        } else {
            field.type = "password";
            toggleButton.classList.replace("ri-eye-line", "ri-eye-off-line");
        }
    }

    oldPasswordToggle.addEventListener("click", () => {
        toggleVisibility('oldpassword', oldPasswordToggle)
    });

    newPasswordToggle.addEventListener("click", () => {
        toggleVisibility('newpassword', newPasswordToggle)
    });

    confirmToggle.addEventListener("click", () => {
        toggleVisibility('confirm', confirmToggle)
    });

    delpasswordToggle.addEventListener("click", () => {
        toggleVisibility('delpassword', delpasswordToggle)
    });

});





// Auto Submit Location Form

function submitForm() {
    document.querySelector('.locations').submit();
}

function submitForm1() {
    document.querySelector('.bookingcategories').submit();
}





