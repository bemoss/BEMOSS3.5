/**

 *  Authors: BEMOSS Team
 *  Version: 2.0
 *  Email: aribemoss@gmail.com
 *  Created: "2014-10-13 18:45:40"
 *  Updated: "2015-02-13 15:06:41"


 * Copyright © 2014 by Virginia Polytechnic Institute and State University
 * All rights reserved

 * Virginia Polytechnic Institute and State University (Virginia Tech) owns the copyright for the BEMOSS software and its
 * associated documentation ("Software") and retains rights to grant research rights under patents related to
 * the BEMOSS software to other academic institutions or non-profit research institutions.
 * You should carefully read the following terms and conditions before using this software.
 * Your use of this Software indicates your acceptance of this license agreement and all terms and conditions.

 * You are hereby licensed to use the Software for Non-Commercial Purpose only.  Non-Commercial Purpose means the
 * use of the Software solely for research.  Non-Commercial Purpose excludes, without limitation, any use of
 * the Software, as part of, or in any way in connection with a product or service which is sold, offered for sale,
 * licensed, leased, loaned, or rented.  Permission to use, copy, modify, and distribute this compilation
 * for Non-Commercial Purpose to other academic institutions or non-profit research institutions is hereby granted
 * without fee, subject to the following terms of this license.

 * Commercial Use: If you desire to use the software for profit-making or commercial purposes,
 * you agree to negotiate in good faith a license with Virginia Tech prior to such profit-making or commercial use.
 * Virginia Tech shall have no obligation to grant such license to you, and may grant exclusive or non-exclusive
 * licenses to others. You may contact the following by email to discuss commercial use:: vtippatents@vtip.org

 * Limitation of Liability: IN NO EVENT WILL VIRGINIA TECH, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR REDISTRIBUTE
 * THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR
 * CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO
 * LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR A FAILURE
 * OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF VIRGINIA TECH OR OTHER PARTY HAS BEEN ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGES.

 * For full terms and conditions, please visit https://bitbucket.org/bemoss/bemoss_os.

 * Address all correspondence regarding this license to Virginia Tech's electronic mail address:: vtippatents@vtip.org

**/

$( document ).ready(function() {
    $.csrftoken();
    $(function ($) {
        $(".thsens_gauge").each(function (index) {
            var sensor_element = document.getElementById(this.id);
            var element_id = sensor_element.id.split('_');
            element_id = element_id[1];
            divid = element_id + "_divopen";
            var class_name = document.getElementById(divid);
            class_name = class_name.className;
            $("#" + divid).attr("class", "col-md-5 col-xs-12 col-sm-6");
            var thopts = {
                lines: 12, // The number of lines to draw
                angle: 0.20, // The length of each line
                lineWidth: 0.15, // The line thickness
                pointer: {
                    length: 0.9, // The radius of the inner circle
                    strokeWidth: 0.035, // The rotation offset
                    color: '#000000' // Fill color
                },
                limitMax: 'true',   // If true, the pointer will not go past the end of the gauge
                colorStart: '#6F6EA0',   // Colors
                colorStop: '#C0C0DB',    // just experiment with them
                strokeColor: '#EEEEEE',   // to see which ones work best for you
                generateGradient: true,
                animationSpeed: 20,
                fontSize: 15
            };
            var donut_target = document.getElementById(this.id); // your canvas element
            var donut = new Donut(donut_target).setOptions(thopts); // create sexy gauge!
            donut.animationSpeed = 32; // set animation speed (32 is default value)

            var power_id = this.id.split("_");
            text_field = power_id[1] + "-ttextfield";
            donut.setTextField(document.getElementById(text_field));
            var temp_value_id = power_id[1] + "_tvalue";
            temp_value = parseFloat(document.getElementById(temp_value_id).innerHTML);
            $("#" + temp_value_id).hide();
            donut.maxValue = 100;
            if (temp_value == 0)
                temp_value = temp_value + 0.1;
            donut.set(temp_value);
            donut.setOptions(thopts);
        });

        $(".humidsens_gauge").each(function (index) {
            var hopts = {
                lines: 1, // The number of lines to draw
                angle: 0.0, // The length of each line
                lineWidth: 0.2, // The line thickness
                pointer: {
                    length: 0.7, // The radius of the inner circle
                    strokeWidth: 0.035, // The rotation offset
                    color: '#00000' // Fill color
                },
                limitMax: 'true',   // If true, the pointer will not go past the end of the gauge
                colorStart: '#6FADCF',   // Colors
                colorStop: '#8FC0DA',    // just experiment with them
                strokeColor: '#E0E0E0',   // to see which ones work best for you
                generateGradient: true,
                percentColors: [
                    [0.0, "#a9d70b" ],
                    [0.50, "#f9c802"],
                    [1.0, "#ff0000"]
                ],
                animationSpeed: 20,
                fontSize: 15
            };
            var hgauge_target = document.getElementById(this.id);
            var humid_gauge = new Gauge(hgauge_target);
            var h_id = this.id.split("_");
            htext_field = h_id[1] + "-htextfield";
            humid_gauge.setTextField(document.getElementById(htext_field));
            var h_value_id = h_id[1] + "_hvalue";
            h_value = parseFloat(document.getElementById(h_value_id).innerHTML);
            $("#" + h_value_id).hide();
            humid_gauge.maxValue = 100;


            humid_gauge.set(h_value);
            humid_gauge.setOptions(hopts);

        });

        $(".lightsens_gauge").each(function (index) {
            var lopts = {
                lines: 1, // The number of lines to draw
                angle: 0.0, // The length of each line
                lineWidth: 0.2, // The line thickness
                pointer: {
                    length: 0.7, // The radius of the inner circle
                    strokeWidth: 0.035, // The rotation offset
                    color: '#00000' // Fill color
                },
                limitMax: 'true',   // If true, the pointer will not go past the end of the gauge
                colorStart: '#6FADCF',   // Colors
                colorStop: '#8FC0DA',    // just experiment with them
                strokeColor: '#E0E0E0',   // to see which ones work best for you
                generateGradient: true,
                percentColors: [
                    [0.0, "#a9d70b" ],
                    [0.50, "#f9c802"],
                    [1.0, "#ff0000"]
                ],
                animationSpeed: 20,
                fontSize: 15
            };
            var lgauge_target = document.getElementById(this.id);
            var light_gauge = new Gauge(lgauge_target);
            var l_id = this.id.split("_");
            ltext_field = l_id[1] + "-ltextfield";
            light_gauge.setTextField(document.getElementById(ltext_field));
            var light_value_id = l_id[1] + "_lvalue";
            light_value = parseFloat(document.getElementById(light_value_id).innerHTML);
            $("#" + light_value_id).hide();
            light_gauge.maxValue = 1000;


            light_gauge.set(light_value);
            light_gauge.setOptions(lopts);

        });
    });
});