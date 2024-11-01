/**
 * @preserve
 * profile_mgmt.js
 * version 0.2
 * 2023.10.18 -- 31
 * Miguel Gastelumendi -- mgd
*/
// @ts-check
/* cSpell:locale en pt-br
 * cSpell:ignore mgmt
 */

/// <reference path="./ts-check.js" />

/** @type {Object} */

let activeRow = null;
let addedList = [];
let assignedList = [];
let selectList = [...initialList];
const ignoreList = [itemRemove, itemNone];

window.addEventListener('beforeunload', (event) => {
    if (assignedList.length > 0) {
        event.preventDefault();
    }
});

//-------------
// == Basic Grid
const gridOptions = {
    //rowSelection: 'single'
    onCellFocused: (event) => { activeRow = (event.rowIndex === null) ? null : api.getDisplayedRowAtIndex(event.rowIndex); }
    , rowData: usersSep
    , columnDefs: [
        { field: "user_id", flex: 1, hide: true },
        { field: "user_name", headerName: colHeaders[0], flex: 1 },
        {
            field: colSepOld,
            headerName: colHeaders[1],
            flex: 2,
            cellClassRules: {
                'grd-item-none': params => params.value === itemNone,
                'grd-item-exist': params => assignedList.includes(params.value) && (params.data[colSepNew] == itemNone),
            },
        },
        {
            field: colSepNew,
            headerName: colHeaders[2],
            flex: 2,
            editable: true,
            cellClass: 'grd-col-sep_new',
            cellClassRules: {
                'grd-item-none': params => params.value === itemNone,
                'grd-item-remove': params => params.value === itemRemove,
                'grd-item-added': params => addedList.includes(params.value),
            },
            cellEditor: 'agSelectCellEditor',
            cellEditorParams: params => {
                const sepOld = params.data[colSepOld]
                let lst = [...selectList].filter(a => a != sepOld);
                if (!lst.includes(params.value) && !ignoreList.includes(params.value)) { lst.push(params.value) }
                lst = sortList(lst).concat((sepOld == itemNone) ? [itemNone] : ignoreList)
                return { values: lst };
            },
            valueSetter: (params) => {
                const oldValue = params.oldValue;
                const newValue = params.newValue;
                if (newValue === oldValue) return false;

                if (!ignoreList.includes(oldValue)) {
                    selectList.push(oldValue)
                    need_refresh(params.api, oldValue) // remove back-color
                    assignedList = assignedList.filter(item => item !== oldValue);
                }
                if (!ignoreList.includes(newValue)) {
                    selectList = selectList.filter(item => item !== newValue);
                    assignedList.push(newValue)
                    need_refresh(params.api, newValue) // set back-color
                }
                params.data.sep_new = newValue;
                return true;
            }
        },
        { field: "when", headerName: colHeaders[3], flex: 1 }
    ]
}; // gridOptions


//-------------
//== Init
const myGridElement = document.querySelector('#grid_container');
const api = /** type {Object} */(agGrid.createGrid(myGridElement, gridOptions));


//-------------
// == Actions
const _itemAdd = (sepNew) => {
    let result = false;
    if (sepNew == '') {
        // ignore
    } else if (exists_sep(sepNew)) {
        alert(`O nome '${sepNew}' já está na lista.`);
    } else {
        sortList(addedList, sepNew);
        sortList(selectList, sepNew);
        activeRow.setDataValue(colSepNew, sepNew);
        result = true;
    }
    return result;
}

const gridAdd = () => {
    if (getActiveCellValue() == '') { return }
    let sep_new = getPrompt('Informe o nome do SEP a ser adicionado');
    _itemAdd(sep_new);
}

const gridEdit = () => {
    const cellValue = getActiveCellValue()
    if (cellValue == '') {
        // ignore
    } else if (initialList.includes(cellValue) || ignoreList.includes(cellValue)) {
        alert('Somente SEP adicionados podem ser editados.')
    } else {
        let sep_new = getPrompt('Informe o nome do SEP (branco para remover)', cellValue);
        if (sep_new !== cellValue) {
            selectList = selectList.filter(item => item !== cellValue);
            addedList = addedList.filter(item => item !== cellValue);
            _itemAdd(sep_new);
        }
    }
}

const gridCargo = ( /** @type {string} */ id) => {
    api.stopEditing();
    const elResponse = /** @type {HTMLInputElement} */(document.getElementById(id));
    if (!elResponse) { return false; }
    // TODO Error msg
    const gridData = [];
    api.forEachNode(node => gridData.push(node.data));
    const cargo = JSON.stringify(
        {
            actions: { none: itemNone, remove: itemRemove },
            grid: gridData,
        }
    );
    elResponse.value = cargo
    assignedList = [] // don't ask on leave
    return true
}
//-------------
// == Helpers
const sortList = (lst, newItem) => {
    if (newItem != null) { lst.push(newItem) }
    lst.sort((a, b) => a.localeCompare(b));
    return lst;
};
const need_refresh = (api, value) => {
    if (assignedList.includes(value)) {
        setTimeout(() => { api.refreshCells({ columns: [colSepOld], force: true }) }, 0)
    }
};
const getPrompt = (msg, _default) => {
    api.stopEditing();
    const text = trim_it(prompt(msg, _default))
    return text
}
const toLowerPlus = (/** @type {string} */ str) => str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
const exists_sep = (/** @type {string} */ item) => {
    const _item = toLowerPlus(item).trim();
    const lst = initialList.concat(ignoreList).concat(addedList);
    const exits = lst.filter(a => toLowerPlus(a) === _item);
    return exits.length > 0;
}
const trim_it = (/** @type {string|null} */ item) => ((item == null) || (item.trim() === '')) ? '' : item.trim();
const getActiveCellValue = () => {
    const cellValue = trim_it(activeRow == null ? null : activeRow.data[colSepNew]);
    if (cellValue == '') {
        alert('Clique na coluna [Novo SEP] na linha onde deseja adicionar ou editar.');
    }
    return cellValue;
}

// eof
