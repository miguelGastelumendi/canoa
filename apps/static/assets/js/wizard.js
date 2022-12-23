//  wizard.js
//  Miguel Gastelumendi version 0.2.0 2022.12.22 -- 23
// @ts-check


/**
 * This callback should return true to go
 * @callback fOnNext
 * @returns {boolean}
 */

/**
 * @typedef {Object} wzdControl
 * @param {Function} messageInfo
 * @param {Function} messageError
 * :
 * :
*/
//const mdlControl = {};

const wzdControl = {
  selectedBtnIx: -1,
  nextPageHref: '',  // Wizard page has ony one target
  jsoData: null,
  displayMode: 0,
  /** @type {fOnNext?} */
  fOnNext: null,
  ge: (/** @type {string} */ sId) => /** @type{HTMLElement} */(document.getElementById(sId)),
  getBtn: (/** @type {number} */ ix) => wzdControl.ge(wzdControl.getBtnId(ix)),
  getBtnId: (/** @type {number} */ ix) => `btn${ix}`,
  setBody: (/** @type {string} */ sBody) => wzdControl.ge('idWzdBody').innerHTML = '' + sBody,

  modalReady: () => (typeof mdlControl == 'object'),
  showSelected: (/** @type {number} */ ix) => {
    const eleUsDisplay = wzdControl.ge('idWzdUsDisplay');
    eleUsDisplay.innerHTML = `Selecionado: <b>${wzdControl.jsoData[ix].caption}</b>`;
    eleUsDisplay.classList.remove('visually-hidden');
  },
  //-- Button select
  selectBtn: (/** @type {number} */ ix) => {
    if (wzdControl.selectedBtnIx == ix) { return; }
    wzdControl.showSelected(ix);
    let eleBtn = wzdControl.getBtn(ix)
    eleBtn.classList.remove('btn-info');
    eleBtn.classList.add('btn-warning');
    if (wzdControl.selectedBtnIx >= 0) {
      eleBtn = wzdControl.getBtn(wzdControl.selectedBtnIx);
      eleBtn.classList.remove('btn-warning');
      eleBtn.classList.add('btn-info');
    }
    wzdControl.selectedBtnIx = ix;
  },
  display: () => {
    const sPath = '../../static/assets/img/modelo_plantio/';
    const htmCol = '<div class="col text-center mb-3">';
    let sHtml;
    switch (wzdControl.displayMode) {
      case wzdControl.mode.CUSTOM:
        sHtml = '<div>';
        break;
      case wzdControl.mode.BUTTONS:
        sHtml = '<div class="d-grid gap-2">';
        wzdControl.jsoData.forEach((itm, i) => {
          sHtml +=
            `<button id="${wzdControl.getBtnId(i)}" class="btn btn-info bg-gradient mx-5" type="button" onclick="wzdControl.selectBtn(${i})">` +
            itm.caption +
            '</button>';
        });
        break;
      case wzdControl.mode.IMAGES:
        sHtml = /* htmlRow */ '<div class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4">';
        wzdControl.jsoData.forEach((itm, i) => {
          let onClick = `onclick="wzdControl.selectImg(${i})`;
          sHtml += htmCol + // <htmCol>
            `<button class="mb-2 btn btn-${(i == wzdControl.selectedBtnIx) ? 'warning' : 'info'} bg-gradient" type="button" style="height:4.2em; width:100%" ${onClick}">${itm.caption}</button>` +
            `<a ${onClick}"> <img src="${sPath}${itm.fileName}.png" alt="${itm.fileName}"></a>` +
            '</div>'; /* </htmCol>  */
        });
        break;
      default:
        sHtml = '<div>';
    }
    sHtml += '</div>'; // htmlRow
    wzdControl.setBody(sHtml)
  },
  next : () => {
    let sHref= '';
    let jsBtn
    if (wzdControl.fOnNext && !wzdControl.fOnNext()){
      // Not this time 8-|
    } else if (wzdControl.displayMode == wzdControl.mode.CUSTOM) {
      sHref = wzdControl.nextPageHref;
    } else if (wzdControl.selectedBtnIx < 0) {
      wzdControl.messageInfo('Por favor, selecione uma das opções.')
    } else if ((jsBtn = wzdControl.jsoData[wzdControl.selectedBtnIx]).href) {
      sHref = jsBtn.href;
    } else if (!wzdControl.nextPageHref) {
      wzdControl.messageError(`Não está definido o próximo passo de '${jsBtn.caption}'.`)
    } else if (jsBtn.id) {
      sHref = `${wzdControl.nextPageHref}?id=${jsBtn.id}`;
    } else {
      sHref = jsBtn.href || wzdControl.nextPageHref;
    }
    if (sHref) window.location.href = sHref;
  },
  messageInfo: (sMsg, sTitle) => {
    if (wzdControl.modalReady()) {
      mdlControl.message(sMsg, sTitle)
    } else {
      alert(sMsg)
    }
  },
  messageError: (sMsg, sTitle, fOnError) => {
    if (fOnError) { fOnError(); }
    if (wzdControl.modalReady()) {
      mdlControl.messageError(sMsg, sTitle)
    } else {
      wzdControl.messageInfo(sMsg, sTitle)
    }
  },

  mode: { BUTTONS: 1, IMAGES: 2, CUSTOM: 3 },
  /* ---------------------------------
     Client must call one of this procs
     to initialize the Wizard
  */

  /**
   * Initialize wizard
   * @param {Object} jsonData
   * @param {string} sMode  ['buttons' | todo ...]
   * @param {fOnNext?} [onNext]
   */
  initPage: (jsonData, eMode, onNext = null) => {
    wzdControl.jsoData = jsonData;
    wzdControl.displayMode = eMode;
    wzdControl.OnNext = /** @type {fOnNext} */ (onNext);
    wzdControl.display();
    wzdControl.ge('idWzdBtnOk').disabled = false;
  },

  /**
   * Initialize wizard for custom, all is in your handas
   * @param {string} sNextPage address of next page
   * @param {fOnNext} onNext callback to accept next button
   */
  initCustom: (sNextPage, onNext) => {
    wzdControl.displayMode = wzdControl.mode.CUSTOM
    wzdControl.fOnNext = onNext;
    wzdControl.nextPageHref = sNextPage;
    wzdControl.ge('idWzdBtnOk').disabled = false;
  }
}
//{# eof #}