/**
 * @preserve
 * received_files_mgmt.js
 * version 0.4
 * 2024.10.18 -- 31, 2025.03
 * Miguel Gastelumendi -- mgd
*/
// @ts-check
/* cSpell:locale en pt-br
 * cSpell:ignore Rprt gridOptions
 */

/// <reference path="./ts-check.js" />

//-------------
// == Basic Grid
const gridOptions = {
    rowSelection: 'single',
    onGridReady: (params) => {
        const firstRow = params.api.getDisplayedRowAtIndex(0);
        if (firstRow) { setTimeout(() => { setActiveRow(firstRow); firstRow.setSelected(true); }, 20); }
    },
    onCellFocused: (event) => {
        let row = (event.rowIndex === null) || !event.api ? null : event.api.getDisplayedRowAtIndex(event.rowIndex);
        setActiveRow(row)
    },
    rowData: gridRows,
    columnDefs: [
        { field: colMeta[0].n, flex: 0, hide: true },
        { field: colMeta[1].n, flex: 0, hide: true },
        { field: colMeta[2].n, flex: 0, hide: true },
        { field: colMeta[3].n, headerName: colMeta[3].h, flex: 1, hide: true },
        {
            field: colMeta[4].n, headerName: colMeta[4].h, flex: 0,
            cellClassRules: { 'grid-item-none': params => params.value == itemNone },
        },
        {
            field: colMeta[5].n, headerName: colMeta[5].h, flex: 1,
            cellClassRules: {
                'grid-item-none': params => {
                    const rowNode = params.api.getRowNode(params.rowIndex);
                    return rowNode ? !(rowNode.data.report_found || rowNode.data.data_f_found) : false;
                },
            },
        },
        { field: colMeta[6].n, headerName: colMeta[6].h, flex: 1 },
        {
            field: colMeta[7].n, headerName: colMeta[7].h, flex: 1,
            valueFormatter: params => (params.value ? new Date(params.value).toLocaleString(dateFormat) : ''),
            filter: true,
        },
        {
            field: colMeta[8].n, headerName: colMeta[8].h, flex: 1,
            type: 'rightAligned'
        },
        {
            field: colMeta[9].n, headerName: colMeta[9].h, flex: 1,
            type: 'rightAligned'
        }
    ]
};

//-------------
//== Init
const gridContainer = document.getElementById(gridID);
agGrid.createGrid(gridContainer, gridOptions);


// eof