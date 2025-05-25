/**
 * @preserve
 * sep_crud.js
 * version 0.4
 * 2025.05.23 --
 * Miguel Gastelumendi -- mgd
*/
// @ts-check
/* cSpell:locale en pt-br
 * cSpell:ignore mgmt
 */

/// <reference path="./ts-check.js" />

let activeRow = null;
let removeCount = 0
const icon = /** @type {HTMLImageElement} */(document.getElementById(iconID))

//-------------
// == Basic Grid
const gridOptions = {
    rowSelection: 'single',
    onGridReady: (params) => {
        const api = params.api
        const firstRowNode = api.getDisplayedRowAtIndex(0);
        if (firstRowNode) { setTimeout(() => { firstRowNode.setSelected(true); }, 20); }
    },
    onCellFocused: (event) => {
        activeRow = (event.rowIndex === null) ? null : api.getDisplayedRowAtIndex(event.rowIndex);
        if (activeRow && (icon.src != activeRow.data[colIconUrl])) {
            icon.src = activeRow.data[colIconUrl];
            console.log(icon.src);
        }
    }
    , rowData: gridRows
    , columnDefs: [
        { field: colMeta[0].n, flex: 1, hide: true },
        { field: colMeta[1].n, flex: 1, hide: true },
        { field: colMeta[2].n, headerName: colMeta[2].h, hide: false, flex: 3 },
        { field: colMeta[3].n, headerName: colMeta[3].h, hide: false, flex: 4 },
        { field: colMeta[4].n, headerName: colMeta[4].h, hide: false, flex: 3 },
    ]
}; // gridOptions


//-------------
//== Init
const gridContainer = document.querySelector('#' + gridID);
const api = /** type {Object} */(agGrid.createGrid(gridContainer, gridOptions));


//-------------

// eof