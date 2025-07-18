//



document.addEventListener('DOMContentLoaded', function() {
    const colorInp = document.getElementById('colorInp');
    const colorBtn = document.getElementById('colorBtn');
    const colorImg = document.getElementById('colorImg');
    const classMap = JSON.parse(colorImg.dataset.class)
    const inputHgt = colorInp.offsetHeight + 'px';
    const inputPlH = colorInp.placeholder;
    const invalidClass = "is-invalid"
    const validateColor = () => {
        const hexRegex = /^#([0-9A-F]{3}){1,2}$/i;
        valid = colorInp.value && hexRegex.test(colorInp.value);
        if (valid) {
            colorInp.placeholder = inputPlH;
            colorInp.classList.remove(invalidClass);
        } else {
            colorInp.classList.add(invalidClass);
        }
        return valid
    }

    colorImg.classList.add(classMap[colorInp.type]);


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
    });

    colorInp.addEventListener('blur', function() {
        if (colorInp.type === 'text') {
            validateColor();
        }
    });
});
