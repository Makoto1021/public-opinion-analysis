color_palette = ["#3e95cd", "#8e5ea2", "#3cba9f", "#e8c3b9", "#c45850", "#6a5acd", "#d2b48c", "#ff6347"]

function plotBarChart(data) {
    console.log(data['politician'])
    console.log(data['score'])
    let myChart = document.getElementById('myChart').getContext('2d');
    let barChart = new Chart(myChart, {
        type: 'bar',
        data: {
            labels: data['politician'],
            datasets: [
                {
                    label: "sentiment",
                    data: data['score'],
                    borderColor: color_palette[0],
                    backgroundColor: color_palette[0],
                    fill: true
                }
            ]
        },
        options: {}
    });
    return barChart;
}