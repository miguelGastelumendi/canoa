/**
 * @preserve
 * ts-check.js
 * 2024.10.25
 * Miguel Gastelumendi -- mgd
 *
 * A dummy variable declarations files for @ts-check
 * As an example, see sep_mgmt.js
*/
// cSpell:ignore mgmt Rprt
// @ts-check

var agGrid = /** @type {Object} */ null;
var gridID = /** @type {string} */ '';
var initialList = /** @type {String[]} */[];
var colMeta = /** @type {Object[]} */[];
var rowData = /** @type {JSON} */ '';
var itemNone = /** @type {string} */ '';
var itemRemove = /** @type {string} */ '';

var btnGridSubmit = /** @type {HTMLInputElement} */(document.getElementById("myb"));
var dateFormat = /** @type {string} */ '';

const colIconSrc = /** @type {string} */ '';
const colSepNew = /** @type {string} */ '';
const colSepCurr = /** @type {string} */ '';
const formAdd = /** @type {string} */ '';
const formEdit = /** @type {string} */ '';
const formCantEdit = /** @type {string} */ '';

// received_files_mgmt.js
const isAdm = /** @type {bool} */ false;
const defButtons = () => {
    return [
        /** @type {!HTMLButtonElement} */ (/** @type {unknown} */ (null)),
        /** @type {HTMLButtonElement} */ (/** @type {unknown} */ (null))
    ];
}
/* eof */
