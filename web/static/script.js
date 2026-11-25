function toggleSidebar() {
    const sidebar = document.querySelector(".sidebar");
    const main = document.querySelector(".main");
    if (!sidebar || !main) return;
    const collapsed = sidebar.classList.toggle("collapsed");
    main.classList.toggle("expanded", collapsed);
}

function filterTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    if (!input || !table) return;
    const filter = input.value.toLowerCase();
    for (const row of Array.from(table.querySelectorAll("tbody tr"))) {
        row.hidden = !row.textContent.toLowerCase().includes(filter);
    }
}

function confirmAction(message) {
    return window.confirm(message || "Are you sure?");
}
