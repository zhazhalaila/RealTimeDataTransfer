function renderSensors(data) {
    $('#sensors').empty();
    var translate = {'temperature': '温度', 'humidity': '湿度', 'mq2': '烟雾检测值'};
    data.forEach(function (element) {
        var sensor = element['sensor_value'];
        var sensor_text = '';
        Object.keys(sensor).forEach(function(key) {
                sensor_text += translate[key];
                sensor_text += ': ';
                sensor_text += sensor[key];
                sensor_text += ' ';
        });
        $('#sensors').append(
            '<table class="table table-hover">'
                + '<tr>'
                    + '<td width="35px">'
                        + '<a href="/user/' + element['owner_name'] + '">'
                            + '<img src="' + element['sensor_owner_avatar'] + '"/>'
                        + '</a>'
                    + '<td>'
                        + '<a href="/user/' + element['owner_name'] + '">'
                            + element['owner_name'] + ' '
                        + '</a>'
                        + moment(element['sensor_time']).fromNow()
                        + '<br>'
                        + sensor_text
                    + '<td>'
                + '<tr>'
            + '</table>'

        );
    });
}

function renderNewPage(url) {
    $.ajax({
        url: url,
        type: 'GET',
        success: function(data) {
            renderSensors(data['items']);
            if (!data['_links']['next']) {
                $('#next_url').hide();
            } else {
                $('#next_url').show();
                $('#next_url').attr('href', data['_links']['next']);
            }
            if (!data['_links']['prev']) {
                $('#prev_url').hide();
            } else {
                $('#prev_url').show();
                $('#prev_url').attr('href', data['_links']['prev']);
            }
        }
    })
}

$('#next_url').click(function(event) {
    event.preventDefault();
    url = $(this).attr('href');
    renderNewPage(url);
})

$('#prev_url').click(function(event) {
    event.preventDefault();
    url = $(this).attr('href');
    renderNewPage(url);
})