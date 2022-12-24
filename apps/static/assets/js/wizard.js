/**
 * @preserve
 * Wizard js
 * version 0.7
 * 2022.12.22--24
 * Miguel Gastelumendi -- mgd
*/
// @ts-check

/**
 * This callback should return true to go
 * @callback fOnNext
 * @returns {boolean}
 */

/**
 * @typedef {Object} wzdControl
 * @property {Function} messageInfo
 * @property {Function} messageError
 * :
 * :
*/

const wzdControl = {
  selectedItemIx: -1,
  nextPageHref: '',  // Wizard page has ony one target
  displayMode: 0,
  /** @type {Array<wzdItem>} */
  jsoData: [],
  /** @type {fOnNext?} */
  fOnNext: null,
  ge: (/** @type {string} */ sId) => /** @type{HTMLElement} */(document.getElementById(sId)),
  getBtn: (/** @type {number} */ ix) => wzdControl.ge(wzdControl.getBtnId(ix)),
  getBtnId: (/** @type {number} */ ix) => `btn${ix}`,
  setBody: (/** @type {string} */ sBody) => wzdControl.ge('idWzdBody').innerHTML = '' + sBody,

  //@ts-ignore mdlControl is defined on modal.js
  modalReady: () => (typeof mdlControl == 'object'),

  /** @private */
  showSelected: (/** @type {number} */ ix) => {
    wzdControl.displaySelected(`Selecionado: <b>${wzdControl.jsoData[ix].caption}</b>`);
  },

  /** @private */
  selectItem: (/** @type {number} */ ix) => {
    if (wzdControl.selectedItemIx == ix) { return; }
    wzdControl.showSelected(ix);
    let eleBtn = wzdControl.getBtn(ix)
    eleBtn.classList.remove('btn-info');
    eleBtn.classList.add('btn-warning');
    if (wzdControl.selectedItemIx >= 0) {
      eleBtn = wzdControl.getBtn(wzdControl.selectedItemIx);
      eleBtn.classList.remove('btn-warning');
      eleBtn.classList.add('btn-info');
    }
    wzdControl.selectedItemIx = ix;
  },

  /** @private */
  display: () => {
    const sPath = '../../static/assets/img/modelo_plantio/';
    const htmCol = '<div class="col text-center mb-3">';
    let sHtml;
    switch (wzdControl.displayMode) {
      case wzdControl.mode.CUSTOM:
        return;
      case wzdControl.mode.BUTTONS:
        sHtml = '<div class="d-grid gap-2">';
        wzdControl.jsoData.forEach((itm, i) => {
          sHtml +=
            `<button id="${wzdControl.getBtnId(i)}" class="btn btn-info bg-gradient mx-5" type="button" onclick="wzdControl.selectItem(${i})">` +
            itm.caption +
            '</button>';
        });
        break;
      case wzdControl.mode.IMAGES:
        sHtml = /* htmlRow */ '<div class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4">';
        wzdControl.jsoData.forEach((itm, i) => {
          let onClick = `onclick="wzdControl.selectItem(${i})`;
          sHtml += htmCol + // <htmCol>
            `<button id=${wzdControl.getBtnId(i)} class="mb-2 btn btn-${(i == wzdControl.selectedItemIx) ? 'warning' : 'info'} bg-gradient" type="button" style="height:4.2em; width:100%" ${onClick}">${itm.caption}</button>` +
            `<a ${onClick}"> <img src="${sPath}${itm.fileName}.png" alt="${itm.fileName ? itm.fileName : 'Imagem não disponível'}"></a>` +
            '</div>'; /* </htmCol>  */
        });
        break;
      default:
        sHtml = '<div>';
    }
    sHtml += '</div>'; // htmlRow
    wzdControl.setBody(sHtml)
  },

  /** @private */
  gotoNextPage: () => {
    let sHref = '';
    let jsBtn
    if (wzdControl.fOnNext && !wzdControl.fOnNext()) {
      // Not this time 8-|
    } else if (wzdControl.displayMode == wzdControl.mode.CUSTOM) {
      sHref = wzdControl.nextPageHref;
    } else if (wzdControl.selectedItemIx < 0) {
      wzdControl.messageInfo('Por favor, selecione uma das opções.')
    } else if ((jsBtn = wzdControl.jsoData[wzdControl.selectedItemIx]).href) {
      sHref = jsBtn.href;
    } else if (!wzdControl.nextPageHref) {
      wzdControl.messageError(`Não está definido o próximo passo de '${jsBtn.caption}'.`)
    } else if (jsBtn.id) {
      sHref = `${wzdControl.nextPageHref}?id=${jsBtn.id}`;
    } else {
      sHref = jsBtn.href || wzdControl.nextPageHref;
    }
    if (sHref) setTimeout(() => { window.location.href = sHref }, 0);
  },

  /** @public */
  messageInfo: (sMsg, sTitle) => {
    if (wzdControl.modalReady()) {
      mdlControl.message(sMsg, sTitle)
    } else {
      alert(sMsg)
    }
  },

  /** @public */
  messageError: (sMsg, sTitle, fOnError) => {
    if (fOnError) { fOnError(); }
    if (wzdControl.modalReady()) {
      mdlControl.messageError(sMsg, sTitle)
    } else {
      wzdControl.messageInfo(sMsg, sTitle)
    }
  },

  /**
   * Display HTML text of selected item
   * @param {string} sHtml
   * @public
   */

  displaySelected: (sHtml) => {
    const eleUsDisplay = wzdControl.ge('idWzdUsDisplay');
    eleUsDisplay.innerHTML = '' + sHtml;
    if (sHtml) {
      eleUsDisplay.classList.remove('visually-hidden');
    } else {
      eleUsDisplay.classList.add('visually-hidden');
    }
  },

  /**
   * @enum {number} Wizard items display mode
   * @public
  */
  mode: { BUTTONS: 1, IMAGES: 2, CUSTOM: 3 },

  /**
   * @typedef {Object} wzdItem
   * @property {string} caption display text
   * @property {number} id item`s ID, if informed, it is sent as a parameter
   * @property {string} href address of the next page (if all items have the same one, use 'nextPage')
   * @property {string} fileName image file name
   */

  /**
   * @typedef {Object} wzdConfig
   * @property {Array<wzdItem>} data array of json items
   * @property {number} mode see wzdControl.mode
   * @property {fOnNext?} onNext callback on Next button
   * @property {string} nextPage address of next page
   */
  /**
   * Initialize wizard's page
   * @param {wzdConfig} jsonConfig
   * @public
   */
  initPage: (jsonConfig) => {
    wzdControl.jsoData = jsonConfig.data || [];
    wzdControl.displayMode = jsonConfig.mode;
    wzdControl.fOnNext = jsonConfig.onNext || null;
    wzdControl.nextPageHref = jsonConfig.nextPage || '';
    wzdControl.display();
    wzdControl.ge('idWzdBtnOk').disabled = false;
  },

}
//{# eof #}