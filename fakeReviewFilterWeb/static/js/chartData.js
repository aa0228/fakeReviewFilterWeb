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

function showReviewScoreChart(points) {
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


function showSimScoreInfoChart(div, title, points) {
    div.highcharts({
        chart: {
            type: 'scatter'
        },
        title: {
            text: title
        },
        yAxis: {
            title: {
                text: '评论数'
            }
        },
        xAixs: {
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
            name: '数量'
        }]
    });
}
