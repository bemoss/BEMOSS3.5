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

$(document).ready(function () {
    $.csrftoken();


    // Assign the li ID value to the _alert
    $('#alert_select_id li').click(function (event) {
        alert_id = $(this).attr('id');
    });


    $('.desc_prio').click(function (e) {
        e.preventDefault();// prevent the default anchor functionality



        $('#pr_lvl').text('Priority Level');    // Reset the priority dropdown menu onclick
        $("#ca_panel").css("display", "none");
        $("#temp_range_panel").css("display", "none");
        $("#temp_time_panel").css("display", "none");
        $("#ca_panel_comparator").css("display", "none");
        $("#ca_panel_val").css("display", "none");
        $("#unit_co2").css("display", "none");
        $("#unit_temp").css("display", "none");


    });


    //Dropdown value append
    $('.alert_select li').click(function (event) {
        event.preventDefault();
        var $target = $(event.currentTarget);
        $target.closest('.btn-group')
            .find('[data-bind="label"]').text($target.text())
            .end()
            .children('.dropdown-toggle').dropdown('toggle');

        return false;
    });

    $('#drop_alert').click(function (event) {
        $("#drop_alert").removeClass('btn-danger').addClass('btn-default');
    });


    $('#drop_pr').click(function (event) {
        $("#drop_pr").removeClass('btn-danger');
        $("#drop_pr").addClass('btn-default');
    });

       //Checkbox value append
    $('.bemoss_checkbox').click(function (event) {
        if (undefined == $(this).attr("checked"))
            $(this).attr("checked", "checked");
        else if ($(this).attr("checked") == "checked")
            $(this).removeAttr("checked");

    });

    //Create alert ajax call
    $('#create_alert').click(function (event) {
        event.preventDefault();

        var _alert = alert_id;

        var value = "0";

        /*
         if (_alert == 'Custom') {
         custom_alert = $("#custom_alert").text();
         custom_alert_comparator = $("#custom_alert_comparator").text();
         value = $('#alert_val').val();
         }
         */



        var priority = $('#pr_lvl').text();
        var n_type = new Array();
        $('.bemoss_checkbox').each(function () {
            if ($(this).attr("checked") == "checked") {
                n_type.push(this.id.split("_").join(" "));
            }
        });
        var email = $('#email').val();
        if (undefined != email) {
            email = email.split(",");
        } else {
            email = "";
        }
        var phone = $('#phone').val();
        if (undefined != phone) {
            phone = phone.split(",");
        } else {
            phone = "";
        }
        console.log(n_type);

        var values = {
            "alert": _alert,
            "value": value,
            "priority": priority,
            "Email": email,
            "Text": phone,
            "n_type": n_type
        };
        console.log(values);
        var jsonText = JSON.stringify(values);
        console.log(jsonText);
        $.ajax({
            url: create_alert_url,
            type: 'POST',
            data: jsonText,
            dataType: 'json',
            success: function (data) {
                //window.location.reload(true);
                $('.bottom-right').notify({
                    message: {text: 'The new alert was created'},
                    type: 'blackgloss',
                    fadeOut: {enabled: true, delay: 5000}
                }).show();
                setTimeout(function () {
                    window.location.reload();
                }, 3000);
            },
            error: function (data) {
                if (_alert == "Choose an Alert" || priority == "Priority Level") {
                    if (_alert == "Choose an Alert" && priority != "Priority Level") {
                        $("#drop_alert").removeClass('btn-default');
                        $("#drop_alert").addClass('btn-danger');
                    } else if (_alert != "Choose an Alert" && priority == "Priority Level") {
                        $("#drop_pr").removeClass('btn-default');
                        $("#drop_pr").addClass('btn-danger');
                    } else {
                        $("#drop_alert").removeClass('btn-default');
                        $("#drop_alert").addClass('btn-danger');
                        $("#drop_pr").removeClass('btn-default');
                        $("#drop_pr").addClass('btn-danger');
                    }

                    $('.bottom-right').notify({
                        message: {text: 'Select your choices from the dropdown appropriately. Please try again.'},
                        type: 'blackgloss',
                        fadeOut: {enabled: true, delay: 5000}
                    }).show();
                } else {
                    $('.bottom-right').notify({
                        message: {text: 'Oh snap! Try submitting again. '},
                        type: 'blackgloss',
                        fadeOut: {enabled: true, delay: 5000}
                    }).show();
                }
            }
        });

    });


    $(".delete_alert").click(function (event) {
        event.preventDefault();
        var reg_al_id = this.id.split('_');
        reg_al_id = reg_al_id[1];
        $.ajax({
            url: delete_alert_url,
            type: 'POST',
            data: reg_al_id,
            success: function (data) {
                //window.location.reload(true);

                $('.bottom-right').notify({
                    message: {text: 'The alert was deleted successfully.'},
                    type: 'blackgloss',
                    fadeOut: {enabled: true, delay: 5000}
                }).show();
                setTimeout(function () {
                    window.location.reload();
                }, 3000);
            },
            error: function (data) {
                $('.bottom-right').notify({
                    message: {text: 'The alert could not deleted at the moment. Please try again later.'},
                    type: 'blackgloss',
                    fadeOut: {enabled: true, delay: 5000}
                }).show();
            }
        });
    });

    //Enable Textbox
    $('#Text').change(function () {
        $("#phone").prop("disabled", !$(this).is(':checked'));
    });

    $('#Email').change(function () {
        $("#email").prop("disabled", !$(this).is(':checked'));
    });

});