#!/usr/bin/env python3
#
# Copyright (C) 2016 - Francesco Frassinelli
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# External dependency
import jinja2

import argparse
import collections
import email.parser, email.policy
import mailbox
import os.path

# Default html template
# Jinja2 syntax: http://jinja.pocoo.org/docs/dev/
template = jinja2.Template("""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{{ title }}</title>
  </head>
  <body>
  {% for message in messages %}
  {% for key, value in message.header %}
  {% if key in header_filter %}
  <div><strong>{{ key }}</strong>: {{ value }}</div>
  {% endif %}
  {% endfor %}
  <hr/>
  {% if message.is_html %}
  {{ message.body|safe }}
  {% else %}
  <pre>{{ message.body }}</pre>
  {% endif %}
  {% if not loop.last %}
  <hr/>
  {% endif %}
  {% endfor %}
</body>
</html>
""".strip(), trim_blocks=True, lstrip_blocks=True, autoescape=True)

# Command line options
parser = argparse.ArgumentParser()
parser.add_argument('-p', '--plain', action='store_true',
                    help="prefer plain text over html")
parser.add_argument('-o', '--outfile', nargs='?',
                    type=argparse.FileType('w'),
                    default='-',
                    help='output html file')
parser.add_argument('mbox', type=argparse.FileType('r'),
                    help='mbox file')
args = parser.parse_args()

# Base information and header filters
info = {
    'title':os.path.basename(args.mbox.name),
    'header_filter':[
        'From',
        'Date',
    ],
    'messages':[],
}

# Mailbox parser
reverse = -1 if args.plain else 1
preferencelist = ('html', 'plain')[::reverse]
inbox = mailbox.mbox(args.mbox.name)
for index, message in inbox.items():
    message_info = collections.defaultdict(dict)
    # Message parser
    msg_parser = email.parser.BytesFeedParser(policy=email.policy.default)
    msg_parser.feed(message.as_bytes())
    msg = msg_parser.close()
    # Header
    message_info['header'] = msg.items()
    # Body
    simplest = msg.get_body(preferencelist=preferencelist)
    message_info['is_html'] = simplest.get_content_type() == 'text/html'
    message_info['body'] = simplest.get_content()
    # Add result to collection
    info['messages'].append(message_info)

# Write to file
args.outfile.write(template.render(info))
