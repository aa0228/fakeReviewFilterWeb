$.ajaxSetup({async: false});

function queryParse() {
    var productTypeId = $('#productTypeNameInput').val();
    var url = $('#productInput').val();

    $.get('/parse', {productTypeId: productTypeId, productLink: url}, function(data, status) {
        if(status != 'success') {
            alert('服务器发生了一个错误!');
            return;
        }

        alert(data);

        // 相关信息
        $('#productName').attr('href', url).text(data.productName);
        $('#totalReviewCount').text(data.totalReviewCount);
        $('#fakeReviewCount').text(data.fakeReviewCount);
        $('#advice').text(data.advice);

        // 绘图
        showFakeReviewRateChart(data.fakeReviewCount / data.totalReviewCount);
        showSimScoreInfoChart($('#scoreSimInfoChart'), '评级相似度散点图',
                              data.scoreSimScoreInfo);
        showSimScoreInfoChart($('#textSimInfoChart'), '文本相似度散点图',
                              data.textSimScoreInfo);
        showSimScoreInfoChart($('#emotionSimInfoChart'), '情感相似度散点图',
                              data.emotionSimScoreInfo);

        // 显示评论
        showReviews(data.reviews);

    }, 'json');
}

$(document).ready(function() {

    $('#submitButton').click(function() {
        queryParse();

        $('div.header').css('display', 'block');
        $('div#result').css('display', 'block');
        $('div.inputDiv').css('display', 'none');
        $('#cover').slideUp();

        return false;
    });
});
