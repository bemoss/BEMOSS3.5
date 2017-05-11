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



function checkPassword(str)
  {
    // at least one number, one lowercase and one uppercase letter
    // at least six characters
    var re = /(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{6,}/;
    return re.test(str);
  }
function validateEmail(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}



    $('#register').click(function(evt) {
        evt.preventDefault();

        var firstname = $("#first-name").val();
        var lastname = $("#last-name").val();
        var username = $("#username").val();
        var password = $("#password").val();
        var email = $("#email").val();
        var phone = $("#phone").val();

        var values = {
            "firstname": firstname,
            "lastname": lastname,
            "username": username,
            "password": password,
            "email": email,
            "phone": phone
        };

        var jsonText = JSON.stringify(values);

        $.ajax({
            url : '/register_new_user/',
            type: 'POST',
            data: jsonText,
            dataType: 'json',
            success : function(data) {
                $('#reg_msg').html(data.status);
                $('.bottom-right').notify({
                    message: { text: 'Registration request sent. The administrator will approve your request shortly.' },
                    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 5000 }
                }).show();
            },
            error: function(data) {
                $('.bottom-right').notify({
                    message: { text: 'Username unavailable. Try another!' },
                    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 5000 }
                }).show();
            }
        });


    });

    $('#change_password').click(function(evt) {
        evt.preventDefault();
        var id_user_name = $("#id_user_name").val();
        var old_password = $("#id_old_password_1").val();
        var id_password_new_1 = $("#id_password_new_1").val();
        var id_password_new_2 = $("#id_password_new_2").val();
        var valid=checkPassword(id_password_new_1);
        if(id_password_new_1==id_password_new_2 && valid){
        var values = {

            "id_user_name": id_user_name,
            "old_password": old_password,
            "id_password_new_1":id_password_new_1

        };

        var jsonText = JSON.stringify(values);
        $.ajax({
            url : url_change_password,
            type: 'POST',
            data: jsonText,
            dataType: 'json',
            success : function(data) {
            if (data.status == "success") {
                $('#reg_msg').html(data.status);
                $('.bottom-right').notify({
                    message: { text: 'Password changed Successfully' },
                    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 5000 }

                }).show();}else{
                if(data.status=="failure1")
                {var message="No user found in database";}
                else
                {var message="Incorrect old password, try forgot password";}
                $('#reg_msg').html(data.status);
                $('.bottom-right').notify({
                    message: { text: message},
                    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 5000 }

                }).show();}
            },
            error: function(data) {
                $('.bottom-right').notify({
                    message: { text: 'Password was not changed' },
                    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 5000 }
                }).show();
            }
        });
}else {
                $('.bottom-right').notify({
                    message: {text: 'Passwords don\'t match or Invalid new password'},
                    type: 'blackgloss',
                    fadeOut: {enabled: true, delay: 5000}
                }).show();
            }

    });

    $('#proceed_change').click(function(evt) {
        evt.preventDefault();
        var id_email_ = $("#id_email_").val();
        var valid=validateEmail(id_email_);
if( valid){
        var values = {
            "id_email_": id_email_,
        };

        var jsonText = JSON.stringify(values);
        $.ajax({
            url : url_email_password,
            type: 'POST',
            data: jsonText,
            dataType: 'json',
            success : function(data) {
                $('#reg_msg').html(data.status);
                $('.bottom-right').notify({
                    message: { text: 'Email Sent Successfully' },
                    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 5000 }

                }).show();
            },
            error: function(data) {
                $('.bottom-right').notify({
                    message: { text: 'Email was not Sent' },
                    type: 'blackgloss',
                    fadeOut: { enabled: true, delay: 5000 }
                }).show();
            }
        });}else{
                $('.bottom-right').notify({
                    message: {text: 'Invalid Email ID'},
                    type: 'blackgloss',
                    fadeOut: {enabled: true, delay: 5000}
                }).show();
            }


    });

});