"use strict";

// defer гарантирует, что подвал уже существует при выполнении скрипта.
const yearElement = document.getElementById("current-year");
if (yearElement) {
  yearElement.textContent = new Date().getFullYear();
  yearElement.dataset.updatedBy = "javascript";
}
