//


document.addEventListener('DOMContentLoaded', function() {
    const classMap = JSON.parse(colorImg.dataset.class)
    const inputHgt = colorInp.offsetHeight + 'px';
    const invalidClass = "is-invalid"
    const imgDefaultColor = window.getComputedStyle(colorImg).color;
    const validateColor = () => {
        valid = /^#[0-9A-Fa-f]{6}$/.test(colorInp.value);
        btnSubmit.disabled = !valid;
        if (valid) {
            colorInp.classList.remove(invalidClass);
        } else {
            colorInp.classList.add(invalidClass);
        }
        return valid
    }
    const setImageColor = (toDefault) => {
        const clr = (toDefault || !validateColor()) ? imgDefaultColor : colorInp.value;
        colorImg.style.color = clr;
    }

    colorImg.classList.add(classMap[colorInp.type]);

    ['mouseenter', 'focus', 'keyup'].forEach(event => {
        colorInp.addEventListener(event, () => setImageColor(false))
        colorBtn.addEventListener(event, () => setImageColor(false))
    });

    ['mouseleave', 'blur'].forEach(event => {
        colorInp.addEventListener(event, () => setImageColor(true))
        colorBtn.addEventListener(event, () => setImageColor(true))
    });


    colorBtn.addEventListener('click', function() {
        colorImg.classList.remove(classMap[colorInp.type])
        if (colorInp.type === 'color') {
            colorInp.type = 'text';
        } else if (validateColor()) {
            colorInp.type = 'color';
            colorInp.style.height = inputHgt;
        } else {
            colorImg.classList.add(classMap[colorInp.type])
            return
        }
        colorImg.classList.add(classMap[colorInp.type]);
        setImageColor(true)
    });
});

// eof
