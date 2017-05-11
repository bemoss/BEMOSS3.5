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

    //var nick_re = /^[A-Za-z0-9_ ]*[A-Za-z0-9 ][A-Za-z0-9_ ]{5,10}$/;
    var nick_re = /^[A-Za-z0-9]{6,10}$/;

    $(function ($) {

        $("#add_new_zone_submit").click(function (evt) {
            evt.preventDefault();
            values = $("#add_new_zone").val();
            if (!nick_re.test(values)) {
                document.getElementById("newzoneerror").innerHTML = "Nickname can only contain letters and numbers. Please try again.";
                document.getElementById(values).value = "";
            } else {
                $.ajax({
                    url: '/add_new_zone/',
                    type: 'POST',
                    data: values,
                    success: function (data) {
                        if (data == "invalid") {
                            document.getElementById("newzoneerror").innerHTML = "Your nickname was not accepted by BEMOSS. Please try again.";
                        } else {
                            $("#accordion2").append('<div class="panel" id="sortable_' + data + '"><div class="panel-heading"><p> <a href="#collapse_' + data + '" data-toggle="collapse" class="accordion-toggle collapsed" id="' + data + '_nick_dp">' + values.charAt(0).toUpperCase() + values.slice(1) + '</a>&nbsp;&nbsp;&nbsp;<i id="' + data + '_znedit" class="icon-pencil" data-backdrop="false" data-target="#' + data + '_znmodal" data-toggle="modal"></i></p> </div><div style="display: none;" aria-hidden="true" aria-labelledby="myModalLabel" role="dialog" tabindex="-1" class="modal fade" id="' + data + '_znmodal"><div class="modal-dialog"><div class="modal-content"><div class="modal-header"><button aria-hidden="true" data-dismiss="modal" class="close" type="button">x</button><h4 id="myModalLabel" class="modal-title">Edit Zone Information</h4></div><div class="modal-body"><table class="table table-condensed"><thead><tr><th></th><th></th><th></th></tr></thead><tbody><tr><td>Zone Nickname</td><td id="' + data + '_znick">' + values.charAt(0).toUpperCase() + values.slice(1) + '</td><td><a href="javascript:;" class="znickname_edit" ><i class="icon-small icon-edit" id="' + data + '_znick_edit"></i></a></td><script>$( "#' + data + '_znick_edit" ).click(function() {var newtest = document.getElementById(this.id.replace("_edit",""));newtest.innerHTML = \'<input type="text" id="' + data + '_znickname" placeholder="' + values + '"></input>\'});</script></tr></tbody></table></div><div class="modal-footer"><button data-dismiss="modal" class="btn btn-default" type="button">Close</button><button class="btn btn-primary save_changes_zn" id="#savechanges-' + data + '" type="button">Save changes</button><script>$( ".save_changes_zn" ).click(function(evt) {evt.preventDefault();var save_this = new Common();save_this.Save_Zone_Changes(this.id);});</script></div></div><!-- /.modal-content --></div><!-- /.modal-dialog --></div><div style="height: 0px;" class="panel-collapse collapse" id="collapse_' + data + '"><ul class="panel-body connectedSortable" id="panelbody_' + data + '"><script>$(".panel-body").droppable().sortable({dropOnEmpty: true,connectWith: ".connectedSortable"}).disableSelection();</script></ul></div></div>');
                            $('.bottom-right').notify({
                                message: { text: 'A new zone was added.' },
                                type: 'blackgloss',
                                fadeOut: { enabled: true, delay: 5000 }
                            }).show();

                            $(".panel").mousemove(function (e) {
                                if (e.which == 1) {
                                    if ($(".panel-collapse").hasClass("collapse")) {
                                        $(".panel-collapse").removeClass("collapse");
                                        $(".panel-collapse").addClass("in");
                                        $(".panel-body").show();
                                    }

                                } else {

                                    $(".panel-body").mouseenter(function (e) {
                                        if (e.which == 1) {
                                            $(".panel-body").show();
                                        }
                                    });
                                }
                            });

                        }
                    },
                    error: function (data) {
                        $('.bottom-right').notify({
                            message: { text: 'Oh snap! Try submitting again. ' },
                            type: 'blackgloss',
                            fadeOut: { enabled: true, delay: 5000 }
                        }).show();
                    }
                });
            }
        });



        $(".save_changes_zn").click(function (evt) {
            evt.preventDefault();
            values = this.id.split('-');
            zone_id = values[1];
            values = values[1] + "_znickname";
            var value_er = values;
            znickname = $("#" + values).val();
            var error_id = "zonenickname_" + zone_id;
            if (!nick_re.test(znickname)) {
                document.getElementById(error_id).innerHTML = "Nickname error. Please try again.";
                document.getElementById(values).value = "";
            } else {
                values = {
                    "id": zone_id,
                    "nickname": znickname
                };
                var jsonText = JSON.stringify(values);
                $.ajax({
                    url: '/save_zone_nickname_change/',
                    type: 'POST',
                    data: jsonText,
                    contentType: "application/json; charset=utf-8",
                    dataType: 'json',
                    success: function (data) {
                        if (data == "invalid") {
                            document.getElementById(error_id).innerHTML = "Nickname error. Please try again.";
                            document.getElementById(value_er).value = "";
                        } else {

                            req_value_modal = data.zone_id + "_znick";
                            req_val_stats = data.zone_id + "_nick_dp";
                            modal_zone_nickname = data.zone_id + "_ztdnick";
                            var newtest = document.getElementById(req_value_modal);
                            document.getElementById(req_val_stats).innerHTML = znickname.charAt(0).toUpperCase() + znickname.slice(1);
                            if (document.getElementById(modal_zone_nickname) != null)
                                document.getElementById(modal_zone_nickname).innerHTML = znickname.charAt(0).toUpperCase() + znickname.slice(1);
                            newtest.innerHTML = znickname.charAt(0).toUpperCase() + znickname.slice(1);
                            $('.bottom-right').notify({
                                message: { text: 'Heads up! The zone nickname change was successful.' },
                                type: 'blackgloss',
                                fadeOut: { enabled: true, delay: 5000 }
                            }).show();
                        }
                    },
                    error: function (data) {
                        $('.bottom-right').notify({
                            message: { text: 'Oh snap! Try submitting again. ' },
                            type: 'blackgloss',
                            fadeOut: { enabled: true, delay: 5000 }
                        }).show();
                    }
                });
            }
        });


    });
});