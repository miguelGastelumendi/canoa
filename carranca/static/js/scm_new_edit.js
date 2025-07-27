//
const invalidClass = "is-invalid"
const classMap = JSON.parse(colorImg.dataset.class)

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
const setImageColor = (toDefault, imgDefaultColor) => {
    const clr = (toDefault || !validateColor()) ? imgDefaultColor : colorInp.value;
    colorImg.style.color = clr;
}

const colorBtnToggle = (inputHgt) => {
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
}

document.addEventListener('DOMContentLoaded', function() {
    const inputHgt = colorInp.offsetHeight + 'px';
    const imgDefaultColor = window.getComputedStyle(colorImg).color;

    colorImg.classList.add(classMap[colorInp.type]);

    ['mouseenter', 'focus', 'keyup'].forEach(event => {
        colorInp.addEventListener(event, () => setImageColor(false, imgDefaultColor))
        colorBtn.addEventListener(event, () => setImageColor(false, imgDefaultColor))
    });

    ['mouseleave', 'blur'].forEach(event => {
        colorInp.addEventListener(event, () => setImageColor(true, imgDefaultColor))
        colorBtn.addEventListener(event, () => setImageColor(true, imgDefaultColor))
    });

    colorBtn.addEventListener('click', () => {
        colorBtnToggle(inputHgt);
        setImageColor(true, imgDefaultColor);
    });
});

// eof
