/**

Copyright (c) 2016, Virginia Tech
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
 following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the authors and should not be
interpreted as representing official policies, either expressed or implied, of the FreeBSD Project.

This material was prepared as an account of work sponsored by an agency of the United States Government. Neither the
United States Government nor the United States Department of Energy, nor Virginia Tech, nor any of their employees,
nor any jurisdiction or organization that has cooperated in the development of these materials, makes any warranty,
express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness or
any information, apparatus, product, software, or process disclosed, or represents that its use would not infringe
privately owned rights.

Reference herein to any specific commercial product, process, or service by trade name, trademark, manufacturer, or
otherwise does not necessarily constitute or imply its endorsement, recommendation, favoring by the United States
Government or any agency thereof, or Virginia Tech - Advanced Research Institute. The views and opinions of authors
expressed herein do not necessarily state or reflect those of the United States Government or any agency thereof.

VIRGINIA TECH – ADVANCED RESEARCH INSTITUTE
under Contract DE-EE0006352

#__author__ = "BEMOSS Team"
#__credits__ = ""
#__version__ = "2.0"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2014-09-12 12:04:50"
#__lastUpdated__ = "2016-03-14 11:23:33"

**/

$( document ).ready(function() {

    $.csrftoken();

    $('.widget-content').on('click', '#add_new_holiday', function(e) {
        e.preventDefault();

        var table =$('#holidays').children()[1];
        console.log(table);


        var tr_id = $('#holidays tbody tr:last').attr('id');
        console.log( tr_id);
        tr_id = tr_id.split("_");
        tr_id = tr_id[1];

        if (tr_id == '') {
            tr_id = 0;
        }
        var new_tr_id = parseInt(tr_id) + 1 ;

        var row = table.insertRow();
        row.id = "hd_" + new_tr_id;
		var cell1 = row.insertCell(0);
		var cell2 = row.insertCell(1);
		var cell3 = row.insertCell(2);
        var cell4 = row.insertCell(3);
        cell1.className = 'col-sm-4';
        cell2.className = 'col-sm-4';
        cell3.className = 'col-sm-2';
        cell4.className = 'col-sm-2';
        cell4.id = 'addtd_' + new_tr_id;

        cell1.innerHTML = "<div class='col-md-10'> <div class='input-group date' id='date_" + new_tr_id + "'>" + "" +
                    "<input type='text' class='form-control' data-date-format='YYYY/MM/DD'/>" +
                    "<span class='input-group-addon'><i class='icon icon-calendar'></i>" +
                    "</span></div></div>";
		cell2.innerHTML = "<input type='text' placeholder='Holiday Description' id='hd_desc-" + new_tr_id + "'" +
                                        " class='form-control' value=''>";
        cell3.innerHTML = "<button class='btn btn-sm btn-danger delete_td' type='button' id='delete_" + new_tr_id + "'>X</button>";
        cell4.innerHTML = "<button class='btn  btn-success add_td' type='button' id='add_" + new_tr_id + "'>Add</button>";
        $('#date_' + new_tr_id).datetimepicker({
                    icons: {
                        time: "fa fa-clock-o",
                        date: "fa fa-calendar",
                        up: "icon icon-chevron-up",
                        down: "icon icon-chevron-down"
                    },
                    pickTime: false
                });


    });

    $('.widget-content').on('click', "button[id^='delete_']" , function(e) {
        e.preventDefault();

        var tp_id = this.id;
        tp_id = tp_id.split("_");
        var delete_id = tp_id[1];

        var values = {
            "id": delete_id
        };

        var jsonText = JSON.stringify(values);
        $.ajax({
            url: '/dashboard/delete_holiday/',
            type: 'POST',
            data: jsonText,
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function (data) {
                if (data.status == "success") {
                    $("#hd_" + delete_id).remove();
                    $('.bottom-right').notify({
                        message: { text: 'Holiday removed from BEMOSS.' },
                        type: 'blackgloss',
                        fadeOut: { enabled: true, delay: 5000 }
                    }).show();
                }
            },
            error: function (data) {
                $('.bottom-right').notify({
                    message: { text: 'Holiday could not be removed at the moment. Try again later. ' },
                    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 5000 }
                }).show();
            }
        });

    });

    $('.widget-content').on('click', "button[id^='add_']" , function(e) {
        e.preventDefault();

        var tp_id = this.id;
        tp_id = tp_id.split("_");
        var add_id = tp_id[1];

        var values = {
            "id": add_id,
            "date": $("#date_" + add_id).data("DateTimePicker").getDate()._d.toJSON(),
            "desc":$("#hd_desc-" + add_id).val()
        };

        var jsonText = JSON.stringify(values);
        $.ajax({
            url: '/dashboard/add_holiday/',
            type: 'POST',
            data: jsonText,
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function (data) {
                if (data.status == "success") {
                    $("#addtd_" + add_id).html("");
                    $('.bottom-right').notify({
                        message: { text: 'Holiday added to BEMOSS.' },
                        type: 'blackgloss',
                        fadeOut: { enabled: true, delay: 5000 }
                    }).show();
                }
            },
            error: function (data) {
                $('.bottom-right').notify({
                    message: { text: 'Holiday could not be added at the moment. Try again later. ' },
                    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 5000 }
                }).show();
            }
        });

    });

    $("#bloc_submit").click(function(e) {
        e.preventDefault();
        var pattern=/^[0-9]{5}$/;
        var b_location = $("#b_loc").val();
        if (!pattern.test(b_location)) {

            $(".help-block").show();
        } else {
            var values = {
                "b_loc": b_location
            };

            var jsonText = JSON.stringify(values);
            $.ajax({
                url: '/dashboard/update_zip/',
                type: 'POST',
                data: jsonText,
                contentType: "application/json; charset=utf-8",
                dataType: 'json',
                success: function (data) {
                    if (data == "success") {

                        $('.bottom-right').notify({
                            message: { text: 'Building location updated.' },
                            type: 'blackgloss',
                            fadeOut: { enabled: true, delay: 5000 }
                        }).show();
                    }
                },
                error: function (data) {
                    $('.bottom-right').notify({
                        message: { text: 'Building location could not be updated at the moment. Try again later. ' },
                        type: 'blackgloss',
                        fadeOut: { enabled: true, delay: 5000 }
                    }).show();
                }
            });
        }
    });
});
