#!/usr/bin/env python
#
# Copyright (C) 2014 Google Inc.
#
# YouCompleteMe is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# YouCompleteMe is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with YouCompleteMe.  If not, see <http://www.gnu.org/licenses/>.

from ycmd.utils import Memoize, IsIdentifierChar

# TODO: Change the custom computed (and other) keys to be actual properties on
# the object.
class RequestWrap( object ):
  def __init__( self, request ):
    self._request = request
    self._computed_key = {
      'line_value': self._CurrentLine,
      'start_column': self._CompletionStartColumn
    }


  def __getitem__( self, key ):
    if key in self._computed_key:
      return self._computed_key[ key ]()
    return self._request[ key ]


  def __contains__( self, key ):
    return key in self._computed_key or key in self._request


  def get( self, key, default = None ):
    try:
      return self[ key ]
    except KeyError:
      return default


  @Memoize
  def _CurrentLine( self ):
    current_file = self._request[ 'filepath' ]
    contents = self._request[ 'file_data' ][ current_file ][ 'contents' ]

    # Handling ''.splitlines() returning [] instead of ['']
    if contents is not None and len( contents ) == 0:
      return ''
    return contents.splitlines()[ self._request[ 'line_num' ] - 1 ]


  @Memoize
  def _CompletionStartColumn( self ):
    return CompletionStartColumn( self[ 'line_value'], self[ 'column_num'] )


def CompletionStartColumn( line_value, column_num ):
  """Returns the 1-based index where the completion query should start. So if
  the user enters:
    foo.bar^
  with the cursor being at the location of the caret (so the character *AFTER*
  'r'), then the starting column would be the index of the letter 'b'."""

  start_column = column_num
  # -2 because start_column is 1-based (so -1) and another -1 because we want to
  # look at the previous character
  while start_column > 1 and IsIdentifierChar( line_value[ start_column - 2 ] ):
    start_column -= 1
  return start_column
