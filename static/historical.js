color_palette = ["#3e95cd", "#8e5ea2", "#3cba9f", "#e8c3b9", "#c45850", "#6a5acd", "#d2b48c", "#ff6347"]

function plotLineChart(x, y) {
    console.log(y)

    var datasets = []
    length = Object.keys(y).length;
    console.log(length)
    for (var politician in y) {
        datasets.push(
            {
                data: y[politician],
                label: politician,
                borderColor: color_palette[length],
                fill: false
            }
        );
        length += 1;
    }

    console.log(datasets)

    let lineChart = new Chart(document.getElementById("historical-chart"), {
        type: 'line',
        data: {
            labels: x,
            datasets: datasets
        },
        options: {
            title: {
                display: true,
                text: 'World population per region (in millions)'
            }
        }
    });
    return lineChart;
}


$('select').selectpicker();