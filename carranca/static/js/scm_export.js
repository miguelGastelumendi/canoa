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


document.addEventListener('DOMContentLoaded', () => {
   let draggedItem = null;

   /**
    * Saves the current order of image sources to localStorage.
    */
   function saveGridOrder() {
      // Get all image elements within the grid in their current order
      const images = reticle.querySelectorAll('#grid-container .reticule-item img');

      // Create an array of the image src attributes
      const imageOrder = Array.from(images).map(img => img.src);

      // Save the array to localStorage as a JSON string
      localStorage.setItem('imageGridOrder', JSON.stringify(imageOrder));
      alert('Grid order saved!'); // Provide user feedback
   }

   /**
    * Loads the image order from localStorage and applies it to the grid.
    */
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

   // --- DRAG AND DROP LOGIC (from before) ---
   function initializeDragAndDrop() {
      const gridItems = document.querySelectorAll('.reticule-item');

      gridItems.forEach(item => {
         item.addEventListener('dragstart', function() {
            draggedItem = this;
            setTimeout(() => { this.style.opacity = '0.5'; }, 0);
         });

         item.addEventListener('dragend', function() {
            setTimeout(() => { this.style.opacity = '1'; draggedItem = null; }, 0);
         });

         item.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('over');
         });

         item.addEventListener('dragleave', function() {
            this.classList.remove('over');
         });

         item.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('over');
            if (draggedItem !== this) {
               let draggedContent = draggedItem.innerHTML;
               draggedItem.innerHTML = this.innerHTML;
               this.innerHTML = draggedContent;
            }
         });
      });
   }

   // --- INITIALIZATION ---

   // 1. Load any saved order when the page is ready
   // loadGridOrder();

   // 2. Set up the drag-and-drop functionality
   initializeDragAndDrop();


});

// eof