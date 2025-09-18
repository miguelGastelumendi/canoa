/**
 * @preserve
 * scm_export.js
 * version 0.1
 * 2025.09.01 --
 * Miguel Gastelumendi -- mgd
*/
// @ts-check
/* cSpell:locale en pt-br
 * cSpell:ignore
 */
/// <reference path="./ts-check.js" />

// SEP grid arrangement
document.addEventListener('DOMContentLoaded', () => {

   /**
    * Saves the current order of image sources to localStorage.
    */
   function saveGridOrder() {
      // Get all image elements within the grid in their current order
      const images = reticle.querySelectorAll('#grid-container .reticule-item img');

      // Create an array of the image src attributes
      const imageOrder = Array.from(images).map(img => img.src);

      // Save the array to localStorage as a JSON string
      // localStorage.setItem('imageGridOrder', JSON.stringify(imageOrder));
      // alert('Grid order saved!'); // Provide user feedback
   }

   /**
    * Loads the image order from localStorage and applies it to the grid.
   function loadGridOrder() {
      const savedOrder = localStorage.getItem('imageGridOrder');

      if (savedOrder) {
         const imageOrder = JSON.parse(savedOrder);
         const images = document.querySelectorAll('#grid-container .reticule-item img');

         // Re-assign the src for each image based on the saved order
         images.forEach((img, index) => {
            if (imageOrder[index]) {
               img.src = imageOrder[index];
            }
         });
      }
   }
   */

   // --- DRAG AND DROP LOGIC (from before) ---
   /** @type {HTMLSpanElement | null} */
   let draggedItem = null;


   function initializeDragAndDrop() {

      const gridImages = /** @type {HTMLSpanElement[]} */ (Array.from(document.querySelectorAll('.reticule-item-hot')));
      /**
       * Compare the Schema or Sep of tho items.
       * @param {number} part
       * @param {HTMLSpanElement} a
       * @param {HTMLSpanElement} b
       * @returns {boolean}
       */
      const same = (part, a, b) => a.firstElementChild?.id.split(':')[part] === b.firstElementChild?.id.split(':')[part];
      const SCHEMA = 0
      const SEP= 1

      /**
       * Determines if a item can be dropped.
       * That is, if both belong to the same schema
       * @param {HTMLSpanElement} item
       * @returns {boolean}
       */
      const canDrop = (item) => (draggedItem != null) && (draggedItem !== item) && same(SCHEMA, draggedItem, item);


      gridImages.forEach(item => {
         item.addEventListener('dragstart', () => {
            draggedItem = item;
            setTimeout(() => { (item instanceof HTMLElement) && (item.style.opacity = '0.5'); }, 0);
         });

         item.addEventListener('dragend', () => {
            setTimeout(() => { (item instanceof HTMLElement) && (item.style.opacity = '1'); draggedItem = null; }, 0);
         });

         item.addEventListener('dragover', (e) => {
            // How to signal if drop is allowed
            if (canDrop(item)) {
               e.preventDefault();
               item.classList.add('over');
            } else {
               item.classList.remove('over');
            }
         });

         item.addEventListener('dragleave', () => {
            item.classList.remove('over');
         });

         item.addEventListener('drop', (e) => {
            e.preventDefault();
            item.classList.remove('over');
            if (canDrop(item)) {
               let draggedContent = draggedItem.innerHTML;
               draggedItem.innerHTML = item.innerHTML;
               item.innerHTML = draggedContent;
            }
         });
      });
   }

   initializeDragAndDrop();


});


//-------------
// == Ag Grid
const gridOptions = {
   rowSelection: 'single',
   onGridReady: (params) => {
      const firstRow = params.api.getDisplayedRowAtIndex(cargo[cargoKeys.index]);
      if (firstRow) {
         setTimeout(() => { firstRow.setSelected(true); setActiveRow(firstRow, firstRow.rowIndex) }, 20);
      }
   },
   onCellFocused: (event) => {
      let row = (event.rowIndex === null) || !event.api ? null : event.api.getDisplayedRowAtIndex(event.rowIndex);
      setActiveRow(row, event.rowIndex)
   }
   , rowData: gridRows
   , columnDefs: [
      { field: colCode, flex: 1, hide: true },
      { field: colSep, flex: 1, hide: true },
      { field: colScm, flex: 1, hide: true },
      { field: colMeta[3].n, headerName: colMeta[3].h, hide: true, flex: 1 },
      { field: colMeta[4].n, headerName: colMeta[4].h, hide: false, flex: 4 },
      {
         field: colMeta[5].n, headerName: colMeta[5].h, hide: false, flex: 3,
         valueFormatter: params => new Date(params.value).toLocaleString(dateFormat),
      },
      { field: colMeta[6].n, headerName: colMeta[6].h, hide: false, flex: 2 }
   ]
}; // gridOptions

const setActiveRow = (row, rowIx) => {
   if (!row) { return; }
   /*  cargo[cargoKeys.index] = rowIx;
     cargo[cargoKeys.code] = row.data[colCode]
     if (icon.src != row.data[colIconUrl]) {
        icon.src = row.data[colIconUrl];
     } */
}

//-------------
//== Init
const gridContainer = document.getElementById(gridID);
const api = /** type {Object} */(agGrid.createGrid(gridContainer, gridOptions));
//== eof
// eof