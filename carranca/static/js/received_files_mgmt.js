/**
 * @preserve
 * sep_mgmt.js
 * version 0.4
 * 2024.10.18 -- 31
 * Miguel Gastelumendi -- mgd
*/
// @ts-check
/* cSpell:locale en pt-br
 * cSpell:ignore mgmt
 */

/// <reference path="./ts-check.js" />

let activeRow = null;
const icon = /** @type {HTMLImageElement} */(document.getElementById("dlg_icon"))

window.addEventListener('beforeunload', (event) => {

});

//-------------
// == Basic Grid
const gridOptions = {
    onCellFocused: (event) => {
        activeRow = (event.rowIndex === null) ? null : api.getDisplayedRowAtIndex(event.rowIndex);
        if (activeRow) {

        }
    },
    rowData: rowData,
    columnDefs: [
        { field: colData[0].n, flex: 0, hide: true },
        { field: colData[1].n, flex: 0, hide: true },
        { field: colData[2].n, flex: 0, hide: true },

        { field: colData[3].n, headerName: colData[3].h, flex: 1, filter: true },
        {
            field: colData[4].n, headerName: colData[4].h, flex: 2,
            cellClassRules: {
                'grd-item-none': params => params.value == itemNone
            },
        },
        {
            field: colData[5].n, headerName: colData[5].h, flex: 1,
            cellClassRules: {
                'grd-item-none': params => {
                    const rowNode = params.api.getRowNode(params.rowIndex);
                    return rowNode ? !(rowNode.data.report_found && rowNode.data.file_found) : false;
                },
            },
        },
        { field: colData[6].n, headerName: colData[6].h, flex: 1 },
        {
            field: colData[7].n, headerName: colData[7].h, flex: 2,
            filter: true,
            valueFormatter: params => (params.value ? new Date(params.value).toLocaleString(dateFormat) : ''),
        },
        {
            field: colData[8].n, headerName: colData[8].h, flex: 1,
            type: 'rightAligned'
        },
        {
            field: colData[9].n, headerName: colData[9].h, flex: 1,
            type: 'rightAligned'
        }
    ]
};

//-------------
//== Init
const gridContainer = document.getElementById(gridID);
const api = /** type {Object} */(agGrid.createGrid(gridContainer, gridOptions));

/*
fetch('https://www.ag-grid.com/example-assets/space-mission-data.json')
    .then(response => response.json())
    .then((data: any) => gridApi.setGridOption('rowData', data))
*/
// eof