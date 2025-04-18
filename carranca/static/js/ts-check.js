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

//
var agGrid = /** @type {Object} */ null;
var gridID = /** @type {string} */ '';
var iconID = /** @type {string} */ '';
var colMeta = /** @type {Object[]} */[];
var userList = /** @type {String[]} */[];
var gridRows = /** @type {JSON} */ '';
var cargoKeys = /** @type {Object[]} */ '';
var itemNone = /** @type {string} */ '';
var itemRemove = /** @type {string} */ '';
var jsData = /** @type {HTMLScriptElement} */ '';

var btnGridSubmit = /** @type {HTMLInputElement} */(document.getElementById("myb"));
var dateFormat = /** @type {string} */ '';

const colIconSrc = /** @type {string} */ '';
const colUserNew = /** @type {string} */ '';
const colUserCurr = /** @type {string} */ '';
const formAdd = /** @type {string} */ '';
const formEdit = /** @type {string} */ '';
const formCantEdit = /** @type {string} */ '';

// received_files_mgmt.js
const isPower = /** @type {bool} */ false;
const defButtons = () => {
    return [
        /** @type {!HTMLButtonElement} */ (/** @type {unknown} */ (null)),
        /** @type {HTMLButtonElement} */ (/** @type {unknown} */ (null))
    ];
}
/* eof */
