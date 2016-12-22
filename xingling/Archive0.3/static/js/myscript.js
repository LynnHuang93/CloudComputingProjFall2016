$('document').ready( function(){
    var rankhtml= "";
    for (i = 0; i < ranking.length; i++)
    {
        rankhtml= rankhtml + "<li>" +ranking[i] + "</li>";
    };
    $('#ranking-list').html(rankhtml);
});
