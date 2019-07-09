function showFakeReviewRateChart(rate) {
    // rate 是指虚假评分的比例
    $('#fakeReviewRateChart').highcharts({
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false
        },
        title: {
            text: '虚假评论比例'
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: true,
                    format: '<b>{point.name}</b>: {point.percentage:.1f}%',
                    style: {
                        color: (Highcharts.theme && Highcharts.theme.constrastTextColor) || 'black'
                    }
                },
                states: {
                    hover: {
                        enabled: false
                    }
                },
                slicedOffset: 20,
                point: {
                    events: {
                        mouseOver: function() {
                            this.slice();
                        },
                        mouseOut: function() {
                            this.slice();
                        },
                        click: function() {
                            return false;
                        }
                    }
                }
            }
        },
        series: [{
            type: 'pie',
            name: 'fake review rate',
            data: [
                ['real', 1 - rate],
                ['fake', rate]
            ]
        }]
    });
}

function showReviewSocreChart(points) {
    $('#reviewScoreChart').highcharts({
        chart: {
            type: 'scatter'
        },
        title: {
            text: '评论得分散点图'
        },
        yAxis: {
            title: {
                text: '评论数'
            }
        },
        xAxis: {
            title: {
                text: '相似度得分',
                y: 20,
                x: -30,
                offset: 0,
                align: 'low'
            }
        },
        tooltip: {
            shared: true,
            pointFormat: '<b>[{point.x}, {point.y}]</b>'
        },
        plotOptions: {
            scatter: {
                marker: {
                    marker: {
                        states: {
                            hover: {
                                enabled: false,
                                lineWidth: 0
                            }
                        }
                    }
                }
            },
            series: {
                cursor: 'default'
            }
        },
        series: [{
            data: points,
            name: 'hello'
        }]
    });
}

showFakeReviewRateChart(0.2);
showReviewSocreChart([[174.0, 65.6], [175.3, 71.8], [193.5, 80.7], [186.5, 72.6], [187.2, 78.8],
                      [181.5, 74.8], [184.0, 86.4], [184.5, 78.4], [175.0, 62.0], [184.0, 81.6],
                      [180.0, 76.6], [177.8, 83.6], [192.0, 90.0], [176.0, 74.6], [174.0, 71.0],
                      [184.0, 79.6], [192.7, 93.8], [171.5, 70.0], [173.0, 72.4], [176.0, 85.9],
                      [176.0, 78.8], [180.5, 77.8], [172.7, 66.2], [176.0, 86.4], [173.5, 81.8],
                      [178.0, 89.6], [180.3, 82.8], [180.3, 76.4], [164.5, 63.2], [173.0, 60.9]]);
