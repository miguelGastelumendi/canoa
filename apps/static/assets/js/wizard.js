// {# === wizard-head.js === Miguel Gastelumendi version 0.1 2022.12.22 #}

// jsonBtnData = [ {caption:, id:, href: null }, ...]
let iSelectedBtnIx = -1;
let sNextPageHref = '';  // Wizard page has ony one target
let jsoBtnData = null;
let displayBtn = false;
let displayEmpty = false;
const _modalReady = () => (typeof /* wizard.html */ mdlUserMessage === 'function');
const _ge = (sId) => document.getElementById(sId);

/* idWzdBtnOk event */
const wzdNext = () => {
  let sHref;
  let jsBtn
  if (displayEmpty) {
    sHref = sNextPageHref;
  } else if (iSelectedBtnIx < 0) {
    wzdUserMessage('Por favor, selecione uma das opções.')
  } else if ((jsBtn = jsoData[iSelectedBtnIx]).href) {
    sHref = jsBtn.href;
  } else if (!sNextPageHref) {
    wzdErrorMessage(`Não está definido o próximo passo de '${jsBtn.caption}'.`)
  } else if (jsBtn.id) {
    sHref = `${sNextPageHref}?id=${jsBtn.id}`;
  } else {
    sHref = jsBtn.href || sNextPageHref;
  }
  if (sHref) window.location.href = sHref;
}

const _showSelected= (ix) => {
  const eleUsDisplay = _ge('idWzdUsDisplay');
  eleUsDisplay.innerHTML = `Selecionado: <b>${jsoData[ix].caption}</b>`;
  eleUsDisplay.classList.remove('visually-hidden');
}

const _getBtn = (ix) => document.getElementById(_btnId(ix));
const _btnId = (ix) => `btn${ix}`;

// selects a button
const _selectBtn = (ix) => {
  if (iSelectedBtnIx == ix) { return; }
  _showSelected(ix);
  let eleBtn = _getBtn(ix)
  eleBtn.classList.remove('btn-info');
  eleBtn.classList.add('btn-warning');
  if (iSelectedBtnIx >= 0) {
    eleBtn = _getBtn(iSelectedBtnIx);
    eleBtn.classList.remove('btn-warning');
    eleBtn.classList.add('btn-info');
  }
  iSelectedBtnIx = ix;
}

const _setBody = (sBody) => _ge('idWzdBody').innerHTML = '' + sBody;

const _display = () => {
  const sPath = '../../static/assets/img/modelo_plantio/';
  const htmCol = '<div class="col text-center mb-3">';
  let sHtml;
  if (displayBtn) {
    sHtml = '<div class="d-grid gap-2">';
    jsoData.forEach((itm, i) => {
      sHtml +=
          `<button id="${_btnId(i)}" class="btn btn-info bg-gradient mx-5" type="button" onclick="_selectBtn(${i})">` +
          itm.caption +
          '</button>';
    });
  } else {
    sHtml = /* htmlRow */ '<div class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4">';
    jsoData.forEach((itm, i) => {
      let onClick = `onclick="_selectImg(${i})`;
      sHtml += htmCol + // <htmCol>
        `<button class="mb-2 btn btn-${(i == iSelectedBtnIx) ? 'warning' : 'info'} bg-gradient" type="button" style="height:4.2em; width:100%" ${onClick}">${itm.caption}</button>` +
        `<a ${onClick}"> <img src="${sPath}${itm.fileName}.png" alt="${itm.fileName}"></a>` +
        '</div>'; /* </htmCol>  */
    });
  }
  sHtml += '</div>'; // htmlRow
  _setBody(sHtml);
}

/* messages helpers */
const wzdUserMessage = (sMsg, sTitle) => {
  if (_modalReady()) {
    mdlUserMessage(sMsg, sTitle)
  } else {
    alert(sMsg)
  }
}
const wzdErrorMessage = (sMsg, sTitle, fOnError) => {
  if (fOnError) { fOnError(); }
  if (_modalReady()) {
    mdlUserMessageError(sMsg, sTitle)
  } else {
    wzdUserMessage(sMsg, sTitle)
  }
}

/* ---------------------------------
   Client must call one of this procs
   to initialize the Wizard
*/
/**
 * Initialize wizard for buttons
 * @param {Object} jsonData
 * @param {string} sMode  ['buttons' | todo ...]
 */
const wzdInitPage = (jsonData, sMode) => {
  jsoData = jsonData;
  displayBtn = ((sMode + '').toLowerCase() == 'buttons');
  _display();
  _ge('idWzdBtnOk').disabled = false;
}

/**
 * Initialize wizard for nothing
 * @param {string} sNextPage address of next page
 */
const wzdInitEmpty = (sNextPage) => {
  displayEmpty = true;
  sNextPageHref = sNextPage;
  _ge('idWzdBtnOk').disabled = false;
 }

//{# eof #}