document.addEventListener("DOMContentLoaded", function () {
    const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;

    const comparer = (idx, asc) => (a, b) => (
        (v1, v2) =>
            v1 !== "" && v2 !== "" && !isNaN(v1) && !isNaN(v2)
                ? v1 - v2
                : v1.toString().localeCompare(v2)
    )(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

    $("#myElement").on("click", function () {
        var dishId = $(this).attr("dish-id");
        console.log("Нажат элемент с dish.id =", dishId);
    });

    document.querySelectorAll("th:not(#Photo, #Actions)").forEach((th, index) =>
        th.addEventListener("click", () => {
            const table = th.closest("table");
            const sortDir = table.getAttribute("data-sort-dir") === "asc" ? "desc" : "asc";

            // Установите направление сортировки в атрибут data-sort-dir таблицы
            table.setAttribute("data-sort-dir", sortDir);

            // Удалите индикаторы сортировки
            table.querySelectorAll(".sort-indicator").forEach((indicator) => indicator.remove());

            // Добавьте индикатор текущей сортировки
            const indicator = document.createElement("span");
            indicator.className = "sort-indicator";
            indicator.textContent = sortDir === "asc" ? " ▲" : " ▼";
            th.appendChild(indicator);

            // Сортировка строк таблицы
            Array.from(table.querySelectorAll("tr.dish-separator"))
                .sort(comparer(index, sortDir === "asc"))
                .forEach((tr) => table.querySelector("tbody").appendChild(tr));
        })
    );
});