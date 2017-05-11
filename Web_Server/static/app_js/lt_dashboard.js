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

    $(".hue").each(function (index) {
        //alert(this.id);
        var hue_element = document.getElementById(this.id);
        var element_id = hue_element.id.split('_');
        element_id = element_id[0];
        var no_of_lights = hue_element.innerHTML;
        no_of_lights = no_of_lights.split('');
        if (no_of_lights.length > 4 && no_of_lights.length < 10) {
            divid = element_id + "_divopen";
            var class_name = document.getElementById(divid);
            class_name = class_name.className;
            $("#" + divid).attr("class", "col-md-5 col-xs-12 col-sm-6");
        }
        if (no_of_lights.length > 9) {
            divid = element_id + "_divopen";
            var class_name = document.getElementById(divid);
            //class_name = class_name.className;
            class_name.className = 'col-md-9 col-xs-12 col-sm-6';
            $("#" + divid).attr("class", "col-md-9 col-xs-12 col-sm-6");
        }
        $.each(no_of_lights, function (i, val) {
            current_innerHTML = $("#huelights_" + element_id).html();
            if (val == 1)
                $("#huelights_" + element_id).html(current_innerHTML + '<img src="/static/images/bulbon.png" width=15% height=30% alt="ON" style="-webkit-filter:brightness(1.5);">');
            if (val == 0)
                $("#huelights_" + element_id).html(current_innerHTML + '<img src="/static/images/bulbon.png" width=15% height=30% alt="OFF" style="-webkit-filter:grayscale(100%);">');
        });

        $(".hue").hide();

    });
});
