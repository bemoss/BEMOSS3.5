# -*- coding: utf-8 -*-
'''
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
'''

from django import forms
from django.contrib.auth.forms import UserCreationForm
from users import UserModel, UsernameField
from django.utils.translation import ugettext_lazy as _
from _utils.passwords.fields import PasswordField

import string
import re

COMMON_SEQUENCES = [
    "0123456789",
    "`1234567890-=",
    "~!@#$%^&*()_+",
    "abcdefghijklmnopqrstuvwxyz",
    "qwertyuiop[]\\asdfghjkl;\'zxcvbnm,./",
    'qwertyuiop{}|asdfghjkl;"zxcvbnm<>?',
    "qwertyuiopasdfghjklzxcvbnm",
    "1qaz2wsx3edc4rfv5tgb6yhn7ujm8ik,9ol.0p;/-['=]\\",
    "qazwsxedcrfvtgbyhnujmikolp",
    "qwertzuiopü+asdfghjklöä#<yxcvbnm,.-",
    "qwertzuiopü*asdfghjklöä'>yxcvbnm;:_",
    "qaywsxedcrfvtgbzhnujmikolp",
]

User = UserModel()
PASSWORD_MIN_LENGTH = 6
PASSWORD_MAX_LENGTH = 15
PASSWORD_DICTIONARY = None
PASSWORD_MATCH_THRESHOLD = 0.9
PASSWORD_COMMON_SEQUENCES = COMMON_SEQUENCES
PASSWORD_COMPLEXITY = { # You can omit any or all of these for no limit for that particular set
    "UPPER": 0,        # Uppercase
    "LOWER": 0,        # Lowercase
    "LETTERS": 1,       # Either uppercase or lowercase letters
    "DIGITS": 0,       # Digits
    "PUNCTUATION": 0,  # Punctuation (string.punctuation)
    #"SPECIAL": 1,      # Not alphanumeric, space or punctuation character
    "WORDS": 0         # Words (alphanumeric sequences separated by a whitespace or punctuation character)
}


class RegistrationForm(UserCreationForm):
    """
    Form for registering a new user account.

    Validates that the requested username is not already in use, and
    requires the password to be entered twice to catch typos.

    Subclasses should feel free to add any additional validation they
    need, but should avoid defining a ``save()`` method -- the actual
    saving of collected user data is delegated to the active
    registration backend.

    """
    required_css_class = 'required'
    first_name = forms.CharField(label=_("First Name"))
    last_name = forms.CharField(label=_("Last Name"))
    email = forms.EmailField(label=_("E-mail"))

    class Meta:
       model = User
       fields = ("first_name", "last_name", UsernameField(), "email")

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.

        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(_("The email address provided is already registered. Please use a different email address/login now."))
        return self.cleaned_data['email']

    def clean_username(self):
        """
        Validate that the supplied username is unique for the
        site.

        """
        if User.objects.filter(email__iexact=self.cleaned_data['username']):
            raise forms.ValidationError(_("The username provided is unavailable. Please choose another."))
        return self.cleaned_data['username']

    def clean_password1(self):
        """
        Validate that the supplied password meets the criteria for strong password.

        """
        if User.objects.filter(email__iexact=self.cleaned_data['username']):
            raise forms.ValidationError(_("The username provided is unavailable. Please choose another."))
        return self.cleaned_data['username']


class RegistrationForm1(forms.Form):
    """
    Form for registering a new user account.

    Validates that the requested username is not already in use, and
    requires the password to be entered twice to catch typos.

    Subclasses should feel free to add any additional validation they
    need, but should avoid defining a ``save()`` method -- the actual
    saving of collected user data is delegated to the active
    registration backend.

    """
    required_css_class = 'required'
    first_name = forms.CharField(label=_("First Name"))
    last_name = forms.CharField(label=_("Last Name"))
    email = forms.EmailField(label=_("E-mail"))
    username = forms.RegexField(label=_("Username"), max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text = _("Required. 30 characters or fewer. Letters, digits and "
                      "@/./+/-/_ only."),
        error_messages = {
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})
    password1 = PasswordField(label=_("Password"),
        widget=forms.PasswordInput, )
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text = _("Enter the same password as above, for verification."))

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.

        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(_("The email address provided is already registered. Please use a different email address/login now."))
        return self.cleaned_data['email']

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(_("Username unavailable. Please choose another."))

    def clean_password1(self):
        """
        Validate that the supplied password meets the criteria for strong password.

        """
        password = self.cleaned_data['password1']
        if len(password) < PASSWORD_MIN_LENGTH:
            raise forms.ValidationError(_("Password should be between 6 and 15 characters in length"))
        if len(password) > PASSWORD_MAX_LENGTH:
            raise forms.ValidationError(_("Password should be between 6 and 15 characters in length"))
        complexities = PASSWORD_COMPLEXITY
        uppercase, lowercase, letters = set(), set(), set()
        digits, punctuation = set(), set()

        for character in password:
            if character.isupper():
                uppercase.add(character)
                letters.add(character)
            elif character.islower():
                lowercase.add(character)
                letters.add(character)
            elif character.isdigit():
                digits.add(character)
            elif character in string.punctuation:
                punctuation.add(character)
            #elif not character.isspace():
                #special.add(character)

        words = set(re.findall(r'\b\w+', password, re.UNICODE))

        errors = []
        if len(uppercase) < complexities.get("UPPER", 0):
            errors.append(
                _("must contain %(UPPER)s or more unique uppercase characters") %
                complexities)
        if len(lowercase) < complexities.get("LOWER", 0):
            errors.append(
                _("must contain %(LOWER)s or more unique lowercase characters") %
                complexities)
        if len(letters) < complexities.get("LETTERS", 0):
            errors.append(
                _("must contain %(LETTERS)s or more unique letters") %
                complexities)
        if len(digits) < complexities.get("DIGITS", 0):
            errors.append(
                _("must contain %(DIGITS)s or more unique digits") %
               complexities)
        if len(punctuation) < complexities.get("PUNCTUATION", 0):
            errors.append(
                (_("must contain %(PUNCTUATION)s or more unique punctuation characters: %%s"
                  ) % complexities) % string.punctuation)
        #if len(special) < complexities.get("SPECIAL", 0):
        #    errors.append(
        #        _("must contain %(SPECIAL)s or more non unique special characters") %
        #        complexities)
        if len(words) < complexities.get("WORDS", 0):
            errors.append(
                _("must contain %(WORDS)s or more unique words") %
                complexities)

        if errors:
            raise forms.ValidationError(_("Password " + u', '.join(errors)))

        return self.cleaned_data['password1']

